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
    public function send(string $command, array $args, ?int $readTimeout = null): array
    {
        $started = microtime(true);
        $reply = $this->dispatch($command, $args, $readTimeout);
        error_log(sprintf(
            '[python-server] page=%s command=%s args=%s -> %s in %d ms%s',
            $_SERVER['SCRIPT_NAME'] ?? 'cli',
            $command,
            json_encode(array_map(static fn($v) => is_string($v) ? mb_substr($v, 0, 100) : $v, $args), JSON_UNESCAPED_UNICODE),
            $reply['ok'] ? 'ok' : 'FAILED',
            (int)((microtime(true) - $started) * 1000),
            $reply['ok'] ? '' : ': ' . mb_substr($reply['message'], 0, 200),
        ));
        return $reply;
    }

    /** @return array{ok: bool, message: string} */
    private function dispatch(string $command, array $args, ?int $readTimeout): array
    {
        // Docker Desktop resolves host.docker.internal to an unreachable IPv6 address first, so prefer IPv4
        $ipv4 = filter_var($this->host, FILTER_VALIDATE_IP) ? false : gethostbynamel($this->host);
        $address = $ipv4[0] ?? $this->host;
        $socket = @stream_socket_client("tcp://{$address}:{$this->port}", $errno, $error, $this->connectTimeout);
        if ($socket === false) {
            return ['ok' => false, 'message' => "Cannot reach the Python server ({$error})"];
        }

        try {
            stream_set_timeout($socket, $readTimeout ?? $this->readTimeout);
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
