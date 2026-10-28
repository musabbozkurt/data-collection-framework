<?php

declare(strict_types=1);

namespace App;

final class Csrf
{
    public static function field(): string
    {
        return '<input type="hidden" name="csrf" value="' . e(self::token()) . '">';
    }

    public static function token(): string
    {
        return $_SESSION['csrf'] ??= bin2hex(random_bytes(32));
    }

    public static function valid(): bool
    {
        return isset($_POST['csrf']) && is_string($_POST['csrf']) && hash_equals(self::token(), $_POST['csrf']);
    }
}
