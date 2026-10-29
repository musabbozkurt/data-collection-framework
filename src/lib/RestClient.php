<?php

declare(strict_types=1);

namespace App;

/** REST: POST /api/commands/{name} with {"args": {...}} and a bearer token. */
final class RestClient extends HttpClient
{
    protected function dispatch(string $command, array $args, int $readTimeout): array
    {
        [$decoded, $error] = $this->post('/api/commands/' . rawurlencode($command), ['args' => (object)$args], $readTimeout);
        return $error === null ? self::reply($decoded) : ['ok' => false, 'message' => $error];
    }
}
