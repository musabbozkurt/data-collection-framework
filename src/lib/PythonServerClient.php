<?php

declare(strict_types=1);

namespace App;

/**
 * Sends one command to the Python back end and returns ['ok' => bool, 'message' => string].
 * The transport is chosen with API_TRANSPORT: rest (default), graphql or tcp.
 */
abstract class PythonServerClient
{
    protected const UNEXPECTED_REPLY = 'Unexpected reply from the Python server';
    protected const LONG_RUNNING = 'The command was accepted and is still running on the server.';

    public function __construct(
        protected string $token = '',
        protected int    $connectTimeout = 3,
        protected int    $readTimeout = 30,
    )
    {
    }

    public static function fromEnv(): self
    {
        $token = env('PY_SERVER_TOKEN');
        return match (strtolower(env('API_TRANSPORT', 'rest'))) {
            'tcp' => new TcpClient(env('PY_SERVER_HOST', 'host.docker.internal'), (int)env('PY_SERVER_PORT', '5555'), $token),
            'graphql' => new GraphqlClient(env('PY_API_URL', 'http://python-api:8000'), $token),
            default => new RestClient(env('PY_API_URL', 'http://python-api:8000'), $token),
        };
    }

    /** Validates the decoded {"ok", "message"} reply shared by every transport. */
    protected static function reply(mixed $decoded): array
    {
        return is_array($decoded) && isset($decoded['ok'], $decoded['message'])
            ? ['ok' => (bool)$decoded['ok'], 'message' => (string)$decoded['message']]
            : ['ok' => false, 'message' => self::UNEXPECTED_REPLY];
    }

    /** @return array{ok: bool, message: string} */
    public function send(string $command, array $args, ?int $readTimeout = null): array
    {
        $started = microtime(true);
        $reply = $this->dispatch($command, $args, $readTimeout ?? $this->readTimeout);
        error_log(sprintf(
            '[python-server] page=%s transport=%s command=%s args=%s -> %s in %d ms%s',
            $_SERVER['SCRIPT_NAME'] ?? 'cli',
            static::class,
            $command,
            json_encode(array_map(static fn($v) => is_string($v) ? mb_substr($v, 0, 100) : $v, $args), JSON_UNESCAPED_UNICODE),
            $reply['ok'] ? 'ok' : 'FAILED',
            (int)((microtime(true) - $started) * 1000),
            $reply['ok'] ? '' : ': ' . mb_substr($reply['message'], 0, 200),
        ));
        return $reply;
    }

    /** @return array{ok: bool, message: string} */
    abstract protected function dispatch(string $command, array $args, int $readTimeout): array;
}
