<?php

declare(strict_types=1);

namespace App;

/**
 * Describes every command the Python server understands, grouped for the UI.
 * Field names match the Python command parameters; the server remains the authority on validation.
 */
final class CommandCatalog
{
    private const PLOTS = [
        'plotlanguage' => 'Language', 'plotcountry' => 'Country', 'plotlocation' => 'Location',
        'plottimezone' => 'Timezone', 'plottweet' => 'Tweet', 'plottweetcreatedat' => 'Tweet Created At',
        'plotuserid' => 'User ID', 'plotstringofid' => 'String of ID', 'plotusername' => 'Username',
        'plotscreenname' => 'ScreenName', 'plotfollowerscount' => 'Followers Count',
        'plotfriendscount' => 'Friends Count', 'plotuserlanguage' => 'User Language',
        'plotretweet' => 'Retweet Count', 'plotfavourite' => 'Favorite Count',
    ];

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
        $username = self::field('Twitter username', 'text', ['pattern' => '[A-Za-z0-9_]{1,15}', 'maxlength' => 15]);
        $tweets = self::field('How many tweets do you want to collect?', 'number', ['min' => 1, 'max' => 3200]);
        $name = ['pattern' => '[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}', 'maxlength' => 64];
        $stream = [
            'database' => self::field('Database name', 'text', $name),
            'collection' => self::field('Collection name', 'text', $name),
            'filename' => self::field('File name', 'text', $name),
            'end_time' => self::field('Finishing date and time', 'datetime'),
        ];

        $plots = [];
        foreach (self::PLOTS as $command => $label) {
            $plots[$command] = [
                'label' => "Plot {$label}",
                'fields' => ['bars' => self::field('How many bars do you want to see in your plot?', 'number',
                    ['min' => 1, 'max' => 100])],
            ];
        }

        return [
            'Collecting Tweets' => [
                'collecttweetfromuserlist' => ['label' => 'Collect tweets from the user list',
                    'fields' => ['tweet_count' => $tweets]],
                'collecttweetfromusername' => ['label' => 'Collect tweets from a username',
                    'fields' => ['username' => $username, 'tweet_count' => $tweets]],
            ],
            'Collecting Followers' => [
                'collectfollowerfromuserlist' => ['label' => 'Collect followers from the user list', 'fields' => []],
                'collectfollowerfromusername' => ['label' => 'Collect followers from a username',
                    'fields' => ['username' => $username]],
            ],
            'Storing Data' => [
                'storedata' => ['label' => 'Store data in MongoDB', 'fields' => [
                    'database' => self::field('Database name', 'text', $name),
                    'collection' => self::field('Collection name', 'text', $name),
                ]],
            ],
            'Analysis of Tweets' => $plots,
            'Streaming' => [
                'streamfromlist' => ['label' => 'Stream the configured keyword list', 'fields' => $stream],
                'streamfrominput' => ['label' => 'Stream a given keyword', 'fields' => $stream + [
                        'keyword' => self::field('Word or hashtag to track', 'text', ['maxlength' => 100]),
                    ]],
            ],
            'Cross Validation & F1' => [
                'crossvalidation' => ['label' => 'Cross validation and F1 macro scoring', 'fields' => [
                    'folds' => self::field('Number of folds', 'number', ['min' => 2, 'max' => 100]),
                    'splits' => self::field('Number of shuffle splits', 'number', ['min' => 1, 'max' => 100]),
                    'test_size' => self::field('Test size (0-1)', 'number', ['min' => 0.01, 'max' => 0.99, 'step' => 0.01]),
                    'random_state' => self::field('Random state', 'number', ['min' => 0]),
                    'train_test_size' => self::field('Train/test split test size (0-1)', 'number',
                        ['min' => 0.01, 'max' => 0.99, 'step' => 0.01]),
                    'svm_c' => self::field('C value of the SVC kernel', 'number', ['min' => 1]),
                ]],
            ],
            'Term Frequency' => [
                'termfrequency' => ['label' => 'Term frequency and co-occurrence', 'fields' => [
                    'most_common' => self::field('How many most common terms?', 'number', ['min' => 1, 'max' => 1000]),
                    'max_pairs' => self::field('How many top co-occurrences?', 'number', ['min' => 1, 'max' => 1000]),
                    'search_word' => self::field('Word to find co-occurrences for', 'text', ['maxlength' => 100]),
                ]],
            ],
        ];
    }

    private static function field(string $label, string $type = 'text', array $attrs = []): array
    {
        return ['label' => $label, 'type' => $type] + $attrs;
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
            $date = \DateTimeImmutable::createFromFormat('Y-m-d\TH:i', substr($value, 0, 16))
                ?: \DateTimeImmutable::createFromFormat('Y-m-d H:i:s', $value);
            $result = $date ? [$date->format('Y-m-d H:i:s'), null] : ['', 'Invalid date'];
        }
        return $result;
    }
}
