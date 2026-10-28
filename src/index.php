<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\Chart;
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

$overview = [];
if ($user) {
    $reply = PythonServerClient::fromEnv()->send('mongodatabases', [], 30);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    $overview = is_array($decoded) ? $decoded : [];
}

$stored = [];
foreach ($overview as $dbName => $collections) {
    foreach ($collections as $c => $count) {
        $stored[] = ['label' => "$dbName.$c", 'value' => (int)$count];
    }
}
usort($stored, static fn($a, $b) => $b['value'] <=> $a['value']);
$stored = array_slice(array_values(array_filter($stored, static fn($r) => $r['value'] > 0)), 0, 10);

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

            <section class="tab" data-tab="main">
                <h1>Welcome</h1>
                <p class="text-muted">Pick a menu entry on the left. The pages <strong>X Scraper</strong>, <strong>X
                        Profile
                        Scraper</strong> and <strong>Discover Profiles</strong> collect data without an X account;
                    <strong>Store Data</strong> loads files into MongoDB; <strong>Analytics</strong>,
                    <strong>Cross Validation</strong> and <strong>Term Frequency</strong> analyse what is stored. The
                    tabs below the menu (collecting and streaming) use the X API.</p>
                <h3>How it fits together</h3>
                <div class="flow">
                    <div class="flow-step chart-c0"><strong>1. Collect</strong><span>Scrapers, X API, streaming</span>
                    </div>
                    <span class="flow-arrow">&rarr;</span>
                    <div class="flow-step chart-c1"><strong>2. Store</strong><span>MongoDB, or files you load</span>
                    </div>
                    <span class="flow-arrow">&rarr;</span>
                    <div class="flow-step chart-c2"><strong>3.
                            Analyse</strong><span>Charts, classifiers, term counts</span></div>
                </div>
                <h3>What is stored now</h3>
                <?php if ($stored): ?>
                    <p class="text-muted">Documents per MongoDB collection
                        (<?= number_format(array_sum(array_column($stored, 'value'))) ?> in total).</p>
                    <div class="analytics-result"><?= Chart::view($stored, 'pie', 'documents', 'Collection') ?></div>
                <?php else: ?>
                    <p class="text-muted">Nothing is stored yet. Start with <a href="discover.php">Discover Profiles</a>
                        or <a href="store.php">Store Data</a>.</p>
                <?php endif; ?>
            </section>

            <?php foreach (array_values($groups) as $i => $commands): ?>
                <section class="tab" data-tab="tab<?= $i ?>" hidden>
                    <h1><?= e((string)array_keys($groups)[$i]) ?></h1>
                    <p class="text-muted"><?= e(CommandCatalog::description((string)array_keys($groups)[$i])) ?></p>
                    <?php foreach ($commands as $name => $command): ?>
                        <button type="button" class="menu-item" data-command="<?= e($name) ?>">
                            <?= e($command['label']) ?>
                        </button>
                    <?php endforeach; ?>

                    <?php foreach ($commands as $name => $command): ?>
                        <form method="post" action="index.php" class="command-form" data-command="<?= e($name) ?>"
                              hidden>
                            <h3><?= e($command['label']) ?></h3>
                            <p class="text-muted"><?= e(CommandCatalog::description($name)) ?></p>
                            <?= Csrf::field() ?>
                            <input type="hidden" name="command" value="<?= e($name) ?>">
                            <?php foreach ($command['fields'] as $field => $spec): ?>
                                <?php
                                $id = $name . '-' . $field;
                                $attrs = array_diff_key($spec, ['label' => 1, 'type' => 1]);
                                $type = $spec['type'] === 'datetime' ? 'datetime-local' : $spec['type'];
                                $posted = $activeCommand === $name ? ($_POST[$field] ?? '') : '';
                                $value = is_string($posted) ? $posted : '';
                                $failed = $activeCommand === $name && isset($errors[$field]);
                                ?>
                                <div class="form-group<?= $failed ? ' has-error' : '' ?>">
                                    <label for="<?= e($id) ?>"><?= e($spec['label']) ?></label>
                                    <?php if (isset($attrs['list']) && in_array($attrs['list'], ['dl-databases', 'dl-collections'], true)): ?>
                                        <?php $isDb = $attrs['list'] === 'dl-databases'; ?>
                                        <select class="form-control" id="<?= e($id) ?>-pick"
                                                aria-label="<?= e($spec['label']) ?>"
                                                data-pick="<?= $isDb ? 'database' : 'collection' ?>">
                                            <?php foreach ($overview as $dbName => $collections): ?>
                                                <?php if ($isDb): ?>
                                                    <option value="<?= e((string)$dbName) ?>"><?= e((string)$dbName) ?></option>
                                                <?php else: ?>
                                                    <?php foreach ($collections as $c => $count): ?>
                                                        <option value="<?= e((string)$c) ?>"
                                                                data-db="<?= e((string)$dbName) ?>"><?= e((string)$c) ?>
                                                            (<?= (int)$count ?>)
                                                        </option>
                                                    <?php endforeach; ?>
                                                <?php endif; ?>
                                            <?php endforeach; ?>
                                            <option value="__new__">+ New <?= $isDb ? 'database' : 'collection' ?>...
                                            </option>
                                        </select>
                                        <?php unset($attrs['list']); ?>
                                    <?php endif; ?>
                                    <input class="form-control" id="<?= e($id) ?>" name="<?= e($field) ?>"
                                           type="<?= e($type) ?>" value="<?= e($value) ?>"
                                           required
                                           <?php foreach ($attrs

                                           as $attr => $attrValue): ?>
                                           <?= e($attr) ?>="<?= e($attrValue) ?>"
                                            <?php endforeach; ?>>
                                    <?php if ($failed): ?>
                                        <span class="help-block"><?= e($errors[$field]) ?></span>
                                    <?php endif; ?>
                                </div>
                            <?php endforeach; ?>
                            <button type="submit" class="btn btn-primary">Run</button>
                            <?php if (str_ends_with($name, 'fromuserlist')): ?>
                                <a class="btn btn-default" href="usernames.php">Load usernames file</a>
                                <a href="usernames.php?template=1">Example template</a>
                            <?php endif; ?>
                        </form>
                    <?php endforeach; ?>
                </section>
            <?php endforeach; ?>
        </div>
        <datalist id="dl-keywords">
            <?php foreach (CommandCatalog::KEYWORD_SUGGESTIONS as $k): ?>
            <option value="<?= e($k) ?>"><?php endforeach; ?>
        </datalist>
    <?php endif; ?>
</div>
<?php render('footer'); ?>
