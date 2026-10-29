<?php

declare(strict_types=1);

namespace App;

/** GraphQL: the `run` mutation at /graphql. */
final class GraphqlClient extends HttpClient
{
    private const MUTATION = 'mutation Run($name: String!, $args: JSON) { run(name: $name, args: $args) { ok message } }';

    protected function dispatch(string $command, array $args, int $readTimeout): array
    {
        [$decoded, $error] = $this->post(
            '/graphql',
            ['query' => self::MUTATION, 'variables' => ['name' => $command, 'args' => (object)$args]],
            $readTimeout,
        );
        if ($error !== null) {
            return ['ok' => false, 'message' => $error];
        }
        if (is_array($decoded) && isset($decoded['errors'])) {
            return ['ok' => false, 'message' => (string)($decoded['errors'][0]['message'] ?? self::UNEXPECTED_REPLY)];
        }
        return self::reply($decoded['data']['run'] ?? $decoded);
    }
}
