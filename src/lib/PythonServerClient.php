<?php

declare(strict_types=1);

namespace App;

/** Sends one command to the Python server (line-delimited JSON over TCP) and returns its reply. */
final class PythonServerClient
{
    public function __construct(
        private string $host,
        private int    $port,
        private string $token = '',
        private int    $connectTimeout = 3,
        private int    $readTimeout = 30,
    )
    {
    }

    public static function fromEnv(): self
    {
        return new self(
            env('PY_SERVER_HOST', 'host.docker.internal'),
            (int)env('PY_SERVER_PORT', '5555'),
            env('PY_SERVER_TOKEN'),
        );
    }

    /** @return array{ok: bool, message: string} */
    public function send(string $command, array $args): array
    {
        // Docker Desktop resolves host.docker.internal to an unreachable IPv6 address first, so prefer IPv4
        $ipv4 = filter_var($this->host, FILTER_VALIDATE_IP) ? false : gethostbynamel($this->host);
        $address = $ipv4[0] ?? $this->host;
        $socket = @stream_socket_client("tcp://{$address}:{$this->port}", $errno, $error, $this->connectTimeout);
        if ($socket === false) {
            return ['ok' => false, 'message' => "Cannot reach the Python server ({$error})"];
        }

        try {
            stream_set_timeout($socket, $this->readTimeout);
            $payload = json_encode(['command' => $command, 'args' => $args, 'token' => $this->token], JSON_THROW_ON_ERROR);
            fwrite($socket, $payload . "\n");
            $line = fgets($socket);

            if ($line === false) {
                $timedOut = stream_get_meta_data($socket)['timed_out'] ?? false;
                return $timedOut
                    ? ['ok' => true, 'message' => 'The command was accepted and is still running on the server.']
                    : ['ok' => false, 'message' => 'The Python server closed the connection without a reply'];
            }
            $reply = json_decode($line, true);
            return is_array($reply) && isset($reply['ok'], $reply['message'])
                ? ['ok' => (bool)$reply['ok'], 'message' => (string)$reply['message']]
                : ['ok' => false, 'message' => 'Unexpected reply from the Python server'];
        } finally {
            fclose($socket);
        }
    }
}
