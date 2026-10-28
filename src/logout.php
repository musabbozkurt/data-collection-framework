<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && App\Csrf::valid()) {
    App\Auth::logout();
}
redirect('index.php');
