<?php

declare(strict_types=1);

spl_autoload_register(static function (string $class): void {
    $file = __DIR__ . '/lib/' . str_replace('App\\', '', $class) . '.php';
    if (is_file($file)) {
        require_once $file;
    }
});

ini_set('session.cookie_samesite', 'Lax');
// lifetime, path, domain, secure, httponly; Chrome and Firefox accept Secure cookies on http://localhost
session_set_cookie_params(0, '/', '', true, true);
session_start();

header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header("Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self'");

/** Escapes a value for safe HTML output. */
function e(mixed $value): string
{
    return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** The HTML attribute that marks an <option> as chosen. */
function selected(bool $on): string
{
    return $on ? ' selected' : '';
}

function redirect(string $location): never
{
    header('Location: ' . $location);
    exit;
}

/** Reads an environment variable with a default. */
function env(string $key, string $default = ''): string
{
    $value = getenv($key);
    return $value === false ? $default : $value;
}

function render(string $template, array $vars = []): void
{
    extract($vars, EXTR_SKIP);
    require_once __DIR__ . '/templates/' . $template . '.php';
}
