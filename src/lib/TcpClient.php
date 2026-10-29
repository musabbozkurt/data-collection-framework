<?php

declare(strict_types=1);

namespace App;

/** Line-delimited JSON over TCP to server.py (the original transport; also used by `make server` on the host). */
final class TcpClient extends PythonServerClient
{
    public function __construct(private string $host, private int $port, string $token = '')
    {
        parent::__construct($token);
    }

    protected function dispatch(string $command, array $args, int $readTimeout): array
    {
        // Docker Desktop resolves host.docker.internal to an unreachable IPv6 address first, so prefer IPv4
        $ipv4 = filter_var($this->host, FILTER_VALIDATE_IP) ? false : gethostbynamel($this->host);
        $address = $ipv4[0] ?? $this->host;
        $socket = @stream_socket_client("tcp://{$address}:{$this->port}", $errno, $error, $this->connectTimeout);
        if ($socket === false) {
            return ['ok' => false, 'message' => "Cannot reach the Python server ({$error})"];
        }

        try {
            stream_set_timeout($socket, $readTimeout);
            $payload = json_encode(['command' => $command, 'args' => $args, 'token' => $this->token], JSON_THROW_ON_ERROR);
            fwrite($socket, $payload . "\n");
            $line = fgets($socket);

            if ($line === false) {
                $timedOut = stream_get_meta_data($socket)['timed_out'] ?? false;
                return $timedOut
                    ? ['ok' => true, 'message' => self::LONG_RUNNING]
                    : ['ok' => false, 'message' => 'The Python server closed the connection without a reply'];
            }
            return self::reply(json_decode($line, true));
        } finally {
            fclose($socket);
        }
    }
}
