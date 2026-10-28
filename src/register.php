<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\Csrf;
use App\Database;
use App\UserRepository;

Auth::requireGuest();

$errors = [];
$success = false;
$name = $email = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim((string)($_POST['name'] ?? ''));
    $email = trim((string)($_POST['email'] ?? ''));
    $password = (string)($_POST['password'] ?? '');
    $confirm = (string)($_POST['cpassword'] ?? '');

    if (!Csrf::valid()) {
        http_response_code(403);
        $errors['form'] = 'Invalid or expired form token. Please try again.';
    }
    if (!preg_match('/^[\p{L} ]{1,60}$/u', $name)) {
        $errors['name'] = 'Name must contain only letters and spaces (max 60).';
    }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 255) {
        $errors['email'] = 'Please enter a valid email address.';
    }
    if (strlen($password) < 8 || strlen($password) > 72) { // 72 bytes is bcrypt's limit
        $errors['password'] = 'Password must be 8 to 72 characters.';
    }
    if ($password !== $confirm) {
        $errors['cpassword'] = "Password and confirmation don't match.";
    }

    if (!$errors) {
        $users = new UserRepository(Database::connection());
        try {
            if ($users->emailExists($email)) {
                $errors['email'] = 'This email is already registered.';
            } else {
                $users->create($name, $email, $password);
                $success = true;
            }
        } catch (PDOException $exception) {
            error_log($exception->getMessage());
            $errors['form'] = 'Error in registering. Please try again later.';
        }
    }
}

render('header', ['title' => 'Register']);
?>
<div class="app-shell auth-shell">
    <div class="row">
        <div class="col-md-4 col-md-offset-4 well">
            <form method="post" action="register.php">
                <fieldset>
                    <legend>Sign Up</legend>
                    <?= Csrf::field() ?>
                    <?php foreach ([
                                           ['name', 'Full Name', 'text', $name, 'name'],
                                           ['email', 'Email', 'email', $email, 'email'],
                                           ['password', 'Password', 'password', '', 'new-password'],
                                           ['cpassword', 'Confirm Password', 'password', '', 'new-password'],
                                   ] as [$field, $label, $type, $value, $autocomplete]): ?>
                        <div class="form-group<?= isset($errors[$field]) ? ' has-error' : '' ?>">
                            <label for="<?= $field ?>"><?= $label ?></label>
                            <input type="<?= $type ?>" id="<?= $field ?>" name="<?= $field ?>"
                                   value="<?= e($value) ?>" autocomplete="<?= $autocomplete ?>" required
                                   class="form-control">
                            <?php if (isset($errors[$field])): ?>
                                <span class="help-block"><?= e($errors[$field]) ?></span>
                            <?php endif; ?>
                        </div>
                    <?php endforeach; ?>
                    <button type="submit" class="btn btn-primary">Sign Up</button>
                </fieldset>
            </form>
            <?php if (isset($errors['form'])): ?><p class="text-danger"><?= e($errors['form']) ?></p><?php endif; ?>
            <?php if ($success): ?>
                <p class="text-success">Successfully registered! <a href="login.php">Click here to log in</a></p>
            <?php endif; ?>
        </div>
    </div>
    <div class="row">
        <div class="col-md-4 col-md-offset-4 text-center">
            Already registered? <a href="login.php">Login here</a>
        </div>
    </div>
</div>
<?php render('footer'); ?>
