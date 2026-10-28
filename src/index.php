<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;

$user = Auth::user();
$groups = $user ? CommandCatalog::groups() : [];
$result = null;
$errors = [];
$activeCommand = null;

if ($user && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $commandName = is_string($_POST['command'] ?? null) ? $_POST['command'] : '';
    $command = CommandCatalog::find($commandName);

    if (!Csrf::valid()) {
        http_response_code(403);
        $result = ['ok' => false, 'message' => 'Invalid or expired form token. Please try again.'];
    } elseif ($command === null) {
        http_response_code(400);
        $result = ['ok' => false, 'message' => 'Unknown command.'];
    } else {
        $activeCommand = $commandName;
        [$args, $errors] = CommandCatalog::collect($command['fields'], $_POST);
        if (!$errors) {
            $result = PythonServerClient::fromEnv()->send($commandName, $args);
        }
    }
}

render('header', ['title' => 'Home', 'active' => $activeCommand]);
?>
<div class="app-shell">
    <?php if (!$user): ?>
        <div class="content welcome">
            <h1>Welcome</h1>
            <p>Please <a href="login.php">log in</a> or <a href="register.php">sign up</a> to use the framework.</p>
        </div>
    <?php else: ?>
        <?php render('menu', ['groupNames' => array_keys($groups), 'current' => 'home']); ?>

        <div class="content">
            <?php if ($result): ?>
                <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>" role="alert">
                    <?= e($result['message']) ?>
                </div>
            <?php endif; ?>

            <section class="tab" data-tab="main"><h1>Welcome</h1></section>

            <?php foreach (array_values($groups) as $i => $commands): ?>
                <section class="tab" data-tab="tab<?= $i ?>" hidden>
                    <?php foreach ($commands as $name => $command): ?>
                        <button type="button" class="menu-item" data-command="<?= e($name) ?>">
                            <?= e($command['label']) ?>
                        </button>
                    <?php endforeach; ?>

                    <?php foreach ($commands as $name => $command): ?>
                        <form method="post" action="index.php" class="command-form" data-command="<?= e($name) ?>"
                              hidden>
                            <h3><?= e($command['label']) ?></h3>
                            <?= Csrf::field() ?>
                            <input type="hidden" name="command" value="<?= e($name) ?>">
                            <?php foreach ($command['fields'] as $field => $spec): ?>
                                <?php
                                $id = $name . '-' . $field;
                                $attrs = array_diff_key($spec, ['label' => 1, 'type' => 1]);
                                $type = $spec['type'] === 'datetime' ? 'datetime-local' : $spec['type'];
                                $value = $activeCommand === $name ? ($_POST[$field] ?? '') : '';
                                ?>
                                <div class="form-group<?= isset($errors[$field]) && $activeCommand === $name ? ' has-error' : '' ?>">
                                    <label for="<?= e($id) ?>"><?= e($spec['label']) ?></label>
                                    <input class="form-control" id="<?= e($id) ?>" name="<?= e($field) ?>"
                                           type="<?= e($type) ?>" value="<?= e(is_string($value) ? $value : '') ?>"
                                           required
                                           <?php foreach ($attrs

                                           as $attr => $attrValue): ?>
                                           <?= e($attr) ?>="<?= e($attrValue) ?>"
                                            <?php endforeach; ?>>
                                    <?php if ($activeCommand === $name && isset($errors[$field])): ?>
                                        <span class="help-block"><?= e($errors[$field]) ?></span>
                                    <?php endif; ?>
                                </div>
                            <?php endforeach; ?>
                            <button type="submit" class="btn btn-primary">Run</button>
                        </form>
                    <?php endforeach; ?>
                </section>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</div>
<?php render('footer'); ?>
