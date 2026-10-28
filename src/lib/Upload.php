<?php

declare(strict_types=1);

namespace App;

/** Stores files uploaded in the browser in MongoDB through the Python server. */
final class Upload
{
    private const CHUNK_BYTES = 30000;
    private const SUFFIXES = ['txt', 'json'];
    private const JSON_FLAGS = JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;

    /** Indexes of the files the user actually chose in the $_FILES['uploads'] array. */
    public static function chosen(mixed $uploads): array
    {
        if (!is_array($uploads) || !is_array($uploads['name'] ?? null)) {
            return [];
        }
        return array_keys(array_filter($uploads['name'], 'strlen'));
    }

    /** @throws AppException with a message that is safe to show */
    public static function store(PythonServerClient $client, array $uploads, array $indexes, string $database,
                                 string             $collection, int $timeout): int
    {
        $total = 0;
        foreach ($indexes as $i) {
            $name = (string)$uploads['name'][$i];
            self::check($name, (int)$uploads['error'][$i]);
            $lines = self::lines((string)file_get_contents($uploads['tmp_name'][$i]), $name);
            $total += self::send($client, $database, $collection, $lines, $timeout);
        }
        return $total;
    }

    private static function check(string $name, int $error): void
    {
        if ($error !== UPLOAD_ERR_OK) {
            throw new AppException("$name could not be uploaded (check upload_max_filesize).");
        }
        if (!in_array(self::extension($name), self::SUFFIXES, true)) {
            throw new AppException("$name: only .txt and .json files are supported.");
        }
    }

    private static function extension(string $name): string
    {
        return strtolower(pathinfo($name, PATHINFO_EXTENSION));
    }

    /** Turns .txt (one JSON document per line) or .json (list or object) content into JSON lines. */
    private static function lines(string $content, string $name): array
    {
        return self::extension($name) === 'json' ? self::jsonLines($content, $name) : self::textLines($content, $name);
    }

    private static function jsonLines(string $content, string $name): array
    {
        $decoded = json_decode($content, true);
        if (!is_array($decoded)) {
            throw new AppException("$name is not valid JSON");
        }
        $documents = array_is_list($decoded) ? $decoded : [$decoded];
        return array_map(static fn($d) => json_encode($d, self::JSON_FLAGS), $documents);
    }

    private static function textLines(string $content, string $name): array
    {
        $lines = [];
        foreach (preg_split('/\R/', $content) as $number => $line) {
            if (trim($line) === '') {
                continue;
            }
            if (!is_array(json_decode($line, true))) {
                throw new AppException($name . ', line ' . ($number + 1) . ' is not a JSON object');
            }
            $lines[] = $line;
        }
        return $lines;
    }

    private static function send(PythonServerClient $client, string $database, string $collection, array $lines,
                                 int                $timeout): int
    {
        $stored = 0;
        foreach (self::chunks($lines) as $chunk) {
            $reply = $client->send('storeupload', ['database' => $database, 'collection' => $collection,
                'data' => base64_encode(implode("\n", $chunk))], $timeout);
            if (!$reply['ok']) {
                throw new AppException($reply['message']);
            }
            $stored += count($chunk);
        }
        return $stored;
    }

    /** Groups lines into chunks that fit the Python server's request size limit. */
    private static function chunks(array $lines): array
    {
        $chunks = [];
        $current = [];
        $size = 0;
        foreach ($lines as $line) {
            $length = strlen($line) + 1;
            if ($length > self::CHUNK_BYTES) {
                throw new AppException('A single document is larger than ' . self::CHUNK_BYTES . ' bytes.');
            }
            if ($size + $length > self::CHUNK_BYTES) {
                $chunks[] = $current;
                [$current, $size] = [[], 0];
            }
            $current[] = $line;
            $size += $length;
        }
        if ($current !== []) {
            $chunks[] = $current;
        }
        return $chunks;
    }
}
