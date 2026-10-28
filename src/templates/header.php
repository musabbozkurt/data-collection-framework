<?php
/** @var string $title */
/** @var string|null $active */
$user = App\Auth::user();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title><?= e($title) ?> | Data Collection Framework</title>
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <script src="js/theme.js?v=<?= filemtime(__DIR__ . '/../js/theme.js') ?>"></script>
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/app.css?v=<?= filemtime(__DIR__ . '/../css/app.css') ?>">
</head>
<body data-active="<?= e($active ?? '') ?>">
<nav class="navbar navbar-inverse app-header" role="navigation">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar1">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span><span class="icon-bar"></span><span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="index.php">Data Collection Framework</a>
        </div>
        <div class="collapse navbar-collapse" id="navbar1">
            <ul class="nav navbar-nav navbar-right header-actions">
                <li>
                    <button type="button" class="btn btn-default btn-sm theme-toggle" id="theme-toggle"
                            aria-label="Toggle light and dark theme">
                        <span class="to-light">Light</span>
                        <span class="to-dark">Dark</span>
                    </button>
                </li>
                <?php if ($user): ?>
                    <li class="header-user">Signed in as <?= e($user['name']) ?></li>
                    <li>
                        <form method="post" action="logout.php" class="header-logout">
                            <?= App\Csrf::field() ?>
                            <button type="submit" class="btn btn-default btn-sm">Log Out</button>
                        </form>
                    </li>
                <?php else: ?>
                    <li><a href="login.php">Login</a></li>
                    <li><a href="register.php">Sign Up</a></li>
                <?php endif; ?>
            </ul>
        </div>
    </div>
</nav>
