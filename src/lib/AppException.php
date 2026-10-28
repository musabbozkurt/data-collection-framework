<?php

declare(strict_types=1);

namespace App;

use RuntimeException;

/** A failure whose message is safe to show to the user. */
final class AppException extends RuntimeException
{
}
