<?php

declare(strict_types=1);

namespace App;

/** Renders decoded JSON as nested, collapsible <details> dropdowns. */
final class JsonTree
{
    private const SUMMARY_KEYS = ['keyword', 'url', 'title', 'name', 'text', '_id'];

    public static function document(array $document, int $index): string
    {
        $json = json_encode($document, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) ?: '';
        return '<details class="json-node json-root"><summary>' . self::e(self::title($document, $index))
            . ' <button type="button" class="btn btn-xs btn-default json-copy" data-json="' . self::e($json)
            . '">Copy</button></summary>' . self::children($document) . '</details>';
    }

    private static function e(string $text): string
    {
        return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }

    private static function title(array $document, int $index): string
    {
        foreach (self::SUMMARY_KEYS as $key) {
            if (isset($document[$key]) && is_scalar($document[$key])) {
                return '#' . $index . ' · ' . mb_strimwidth((string)$document[$key], 0, 90, '…');
            }
        }
        return '#' . $index;
    }

    private static function children(array $values): string
    {
        $html = '<div class="json-children">';
        foreach ($values as $key => $value) {
            $html .= self::node($key, $value);
        }
        return $html . '</div>';
    }

    private static function node(string|int $key, mixed $value): string
    {
        $label = '<span class="json-key">' . self::e((string)$key) . '</span>';
        if (!is_array($value)) {
            return '<div class="json-leaf">' . $label . ': ' . self::scalar($value) . '</div>';
        }
        $hint = array_is_list($value) ? '[' . count($value) . ']' : '{' . count($value) . '}';
        return '<details class="json-node"><summary>' . $label . ' <span class="text-muted">' . $hint
            . '</span></summary>' . self::children($value) . '</details>';
    }

    private static function scalar(mixed $value): string
    {
        $class = match (true) {
            is_string($value) => 'json-string',
            is_bool($value) => 'json-bool',
            $value === null => 'json-null',
            default => 'json-number',
        };
        $text = is_string($value) ? $value : json_encode($value);
        return '<span class="' . $class . '">' . self::e((string)$text) . '</span>';
    }
}
