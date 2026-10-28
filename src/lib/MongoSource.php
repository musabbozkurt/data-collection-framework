<?php

declare(strict_types=1);

namespace App;

/** Lets a page pick the MongoDB database and collection its data comes from. */
final class MongoSource
{
    public const DEFAULT_DATABASE = 'x_profile_db';
    public const DEFAULT_COLLECTION = 'profile_tweets';

    /** @return array{0: array<string, array<string, int>>, 1: string, 2: string, 3: ?string} overview, database, collection, error */
    public static function resolve(PythonServerClient $client, int $timeout): array
    {
        $reply = $client->send('mongodatabases', [], $timeout);
        $overview = $reply['ok'] ? json_decode($reply['message'], true) : null;
        if (!is_array($overview)) {
            return [[], '', '', $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message']];
        }
        $database = is_string($_GET['db'] ?? null) ? $_GET['db'] : self::DEFAULT_DATABASE;
        if (!isset($overview[$database])) {
            $database = isset($overview[self::DEFAULT_DATABASE]) ? self::DEFAULT_DATABASE : (string)(array_key_first($overview) ?? '');
        }
        $collections = $overview[$database] ?? [];
        $collection = is_string($_GET['collection'] ?? null) ? $_GET['collection'] : self::DEFAULT_COLLECTION;
        if (!isset($collections[$collection])) {
            $collection = isset($collections[self::DEFAULT_COLLECTION]) ? self::DEFAULT_COLLECTION : (string)(array_key_first($collections) ?? '');
        }
        return [$overview, $database, $collection, null];
    }

    /** Renders a database select and a collection select; the collections follow the chosen database. */
    public static function fields(array $overview, string $database, string $collection): string
    {
        $e = static fn(string $v): string => htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $html = '<label for="db">Database</label> <select class="form-control" id="db" name="db" data-source-db>';
        foreach ($overview as $name => $collections) {
            $html .= '<option value="' . $e((string)$name) . '"' . \selected($name === $database) . '>' . $e((string)$name) . '</option>';
        }
        $html .= '</select> <label for="collection">Collection</label> <select class="form-control" id="collection" name="collection" data-source-collection>';
        foreach ($overview as $name => $collections) {
            foreach ($collections as $c => $count) {
                $html .= '<option value="' . $e((string)$c) . '" data-db="' . $e((string)$name) . '"'
                    . \selected($name === $database && $c === $collection) . '>' . $e((string)$c) . ' (' . (int)$count . ')</option>';
            }
        }
        return $html . '</select>';
    }

    /** @return array{text: string[], labels: string[]} the fields of a collection usable as text and as labels */
    public static function textFields(PythonServerClient $client, string $database, string $collection, int $timeout): array
    {
        $reply = $client->send('collectionfields', ['database' => $database, 'collection' => $collection], $timeout);
        $fields = $reply['ok'] ? json_decode($reply['message'], true) : null;
        return is_array($fields) ? ['text' => (array)($fields['text'] ?? []), 'labels' => (array)($fields['labels'] ?? [])]
            : ['text' => [], 'labels' => []];
    }

    /** The requested option when it is offered, otherwise the first one (or $fallback when there are none). */
    public static function pick(array $options, mixed $requested, string $fallback = ''): string
    {
        return is_string($requested) && in_array($requested, $options, true) ? $requested : (string)($options[0] ?? $fallback);
    }

    /** A labelled select whose option values and texts are both the given strings. */
    public static function select(string $name, string $label, array $options, string $current): string
    {
        $e = static fn(string $v): string => htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $html = '<label for="' . $name . '">' . $e($label) . '</label> <select class="form-control" id="' . $name . '" name="' . $name . '">';
        foreach ($options as $option) {
            $html .= '<option value="' . $e((string)$option) . '"' . \selected((string)$option === $current) . '>'
                . $e((string)$option) . '</option>';
        }
        return $html . '</select>';
    }
}
