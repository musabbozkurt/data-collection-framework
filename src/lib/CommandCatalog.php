<?php

declare(strict_types=1);

namespace App;

use DateTimeImmutable;

/**
 * Describes every command the Python server understands, grouped for the UI.
 * Field names match the Python command parameters; the server remains the authority on validation.
 */
final class CommandCatalog
{
    /** Suggested keywords for the streaming forms. */
    public const KEYWORD_SUGGESTIONS = ['python', '#python', 'java', '#java', 'javascript', '#ai', '#opensource', 'nasa', 'bitcoin'];

    /** @return array{label: string, fields: array}|null */
    public static function find(string $command): ?array
    {
        foreach (self::groups() as $commands) {
            if (isset($commands[$command])) {
                return $commands[$command];
            }
        }
        return null;
    }

    /** @return array<string, array<string, array{label: string, fields: array}>> */
    public static function groups(): array
    {
        $username = self::field('Twitter username', 'text', ['pattern' => '\w{1,15}', 'maxlength' => 15]);
        $tweets = self::field('How many tweets do you want to collect?', 'number', ['min' => 1, 'max' => 3200]);
        $name = ['pattern' => '[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}', 'maxlength' => 64];
        $stream = [
            'database' => self::field('Database (pick one or type a new name)', 'text',
                $name + ['list' => 'dl-databases', 'placeholder' => 'e.g. stream_db']),
            'collection' => self::field('Collection (pick one or type a new name)', 'text',
                $name + ['list' => 'dl-collections', 'placeholder' => 'e.g. stream_tweets']),
            'filename' => self::field('File name for the raw tweets', 'text', $name + ['placeholder' => 'e.g. stream_python.txt']),
            'end_time' => self::field('Finishing date and time', 'datetime'),
        ];

        return [
            'Collecting Tweets & Followers' => [
                'collecttweetfromuserlist' => ['label' => 'Collect tweets from the user list',
                    'fields' => ['tweet_count' => $tweets]],
                'collecttweetfromusername' => ['label' => 'Collect tweets from a username',
                    'fields' => ['username' => $username, 'tweet_count' => $tweets]],
                'collectfollowerfromuserlist' => ['label' => 'Collect followers from the user list', 'fields' => []],
                'collectfollowerfromusername' => ['label' => 'Collect followers from a username',
                    'fields' => ['username' => $username]],
            ],
            'Streaming' => [
                'streamfromlist' => ['label' => 'Stream the configured keyword list', 'fields' => $stream],
                'streamfrominput' => ['label' => 'Stream a given keyword', 'fields' => $stream + [
                        'keyword' => self::field('Word or hashtag to track', 'text',
                            ['maxlength' => 100, 'list' => 'dl-keywords', 'placeholder' => 'e.g. python or #java']),
                    ]],
            ],
        ];
    }

    private static function field(string $label, string $type = 'text', array $attrs = []): array
    {
        return ['label' => $label, 'type' => $type] + $attrs;
    }

    /** Short explanation shown above each group's buttons and (per command) above its form. */
    public static function description(string $name): string
    {
        return [
            'Collecting Tweets & Followers' => 'Collect tweets or followers through the X API, for one username or for the '
                . 'list in usernames.txt. Needs X API credentials in config.ini.',
            'Streaming' => 'Listen live to new tweets that contain your keywords and save them in a MongoDB database and a '
                . 'file until the finishing time. Needs X API credentials.',
            'streamfromlist' => 'Tracks every keyword of word_list_for_streaming in config.ini.',
            'streamfrominput' => 'Tracks one word or hashtag that you type.',
        ][$name] ?? '';
    }

    /**
     * Collects the submitted values of a command's fields.
     *
     * @return array{0: array<string, string>, 1: array<string, string>} [args, errors]
     */
    public static function collect(array $fields, array $input): array
    {
        $args = $errors = [];
        foreach ($fields as $name => $field) {
            $raw = $input[$name] ?? '';
            [$value, $error] = self::parseValue($field['type'], is_string($raw) ? trim($raw) : '');
            if ($error !== null) {
                $errors[$name] = $error;
            } else {
                $args[$name] = $value;
            }
        }
        return [$args, $errors];
    }

    /** @return array{0: string, 1: string|null} [normalized value, error] */
    private static function parseValue(string $type, string $value): array
    {
        $result = [$value, null];
        if ($value === '') {
            $result = ['', 'Required'];
        } elseif ($type === 'number' && !is_numeric($value)) {
            $result = ['', 'Must be a number'];
        } elseif ($type === 'datetime') {
            $date = DateTimeImmutable::createFromFormat('Y-m-d\TH:i', substr($value, 0, 16))
                ?: DateTimeImmutable::createFromFormat('Y-m-d H:i:s', $value);
            $result = $date ? [$date->format('Y-m-d H:i:s'), null] : ['', 'Invalid date'];
        }
        return $result;
    }
}
