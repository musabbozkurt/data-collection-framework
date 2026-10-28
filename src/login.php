<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\Csrf;
use App\Database;
use App\UserRepository;

Auth::requireGuest();

$error = null;
$email = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim((string)($_POST['email'] ?? ''));
    $password = (string)($_POST['password'] ?? '');

    if (!Csrf::valid()) {
        http_response_code(403);
        $error = 'Invalid or expired form token. Please try again.';
    } elseif ((new Auth(new UserRepository(Database::connection())))->attempt($email, $password)) {
        redirect('index.php');
    } else {
        $error = 'Incorrect email or password.';
    }
}

render('header', ['title' => 'Login']);
?>
<div class="app-shell auth-shell">
    <div class="row">
        <div class="col-md-4 col-md-offset-4 well">
            <form method="post" action="login.php">
                <fieldset>
                    <legend>Login</legend>
                    <?= Csrf::field() ?>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" value="<?= e($email) ?>" required
                               autocomplete="username" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required
                               autocomplete="current-password" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </fieldset>
            </form>
            <?php if ($error): ?><p class="text-danger"><?= e($error) ?></p><?php endif; ?>
        </div>
    </div>
    <div class="row">
        <div class="col-md-4 col-md-offset-4 text-center">
            New user? <a href="register.php">Sign up here</a>
        </div>
    </div>
</div>
<?php render('footer'); ?>
