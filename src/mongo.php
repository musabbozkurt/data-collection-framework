<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\JsonTree;
use App\PythonServerClient;

const NAME_PATTERN = '/^[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}$/';
const PAGE_SIZE = 10;
const REQUEST_TIMEOUT_SECONDS = 30;

if (!Auth::user()) {
    redirect('login.php');
}

$database = is_string($_GET['db'] ?? null) ? $_GET['db'] : '';
$collection = is_string($_GET['collection'] ?? null) ? $_GET['collection'] : '';
$page = filter_var($_GET['page'] ?? 1, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'default' => 1]]);
$selected = preg_match(NAME_PATTERN, $database) === 1 && preg_match(NAME_PATTERN, $collection) === 1;

$client = PythonServerClient::fromEnv();
$error = null;
$overview = [];
$documents = [];
$pages = 1;
$total = 0;

$reply = $client->send('mongodatabases', [], REQUEST_TIMEOUT_SECONDS);
$decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
if (is_array($decoded)) {
    $overview = $decoded;
} else {
    $error = $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message'];
}

if ($selected && !$error) {
    $reply = $client->send('mongodocuments',
            ['database' => $database, 'collection' => $collection, 'page' => $page, 'page_size' => PAGE_SIZE],
            REQUEST_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($decoded) && isset($decoded['documents'], $decoded['page'], $decoded['pages'], $decoded['total'])) {
        $documents = $decoded['documents'];
        $page = (int)$decoded['page'];
        $pages = (int)$decoded['pages'];
        $total = (int)$decoded['total'];
    } else {
        $error = $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message'];
    }
}

render('header', ['title' => 'MongoDB Data', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'mongo']); ?>
    <div class="content">
        <h1>MongoDB Data</h1>

        <?php if ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php elseif ($overview === []): ?>
            <p>No databases yet. Collect or store some data first.</p>
        <?php else: ?>
            <h3>Databases</h3>
            <ul class="mongo-list">
                <?php foreach ($overview as $dbName => $collections): ?>
                    <li><strong><?= e((string)$dbName) ?></strong>
                        <?php if ($collections === []): ?>
                            <em>(empty)</em>
                        <?php else: ?>
                            <ul>
                                <?php foreach ($collections as $collectionName => $count): ?>
                                    <li>
                                        <?php if (preg_match(NAME_PATTERN, (string)$dbName) && preg_match(NAME_PATTERN, (string)$collectionName)): ?>
                                            <a href="mongo.php?db=<?= e(rawurlencode((string)$dbName)) ?>&amp;collection=<?= e(rawurlencode((string)$collectionName)) ?>"><?= e((string)$collectionName) ?></a>
                                        <?php else: ?>
                                            <?= e((string)$collectionName) ?>
                                        <?php endif; ?>
                                        <span class="text-muted">(<?= e((string)$count) ?> documents)</span>
                                    </li>
                                <?php endforeach; ?>
                            </ul>
                        <?php endif; ?>
                    </li>
                <?php endforeach; ?>
            </ul>
        <?php endif; ?>

        <?php if ($selected && !$error): ?>
            <h3><?= e($database) ?> / <?= e($collection) ?>
                <small><?= e((string)$total) ?> documents, newest first</small></h3>
            <?php if ($documents === []): ?>
                <p>This collection is empty.</p>
            <?php endif; ?>
            <div class="mongo-docs">
                <?php foreach ($documents as $i => $document): ?>
                    <?= JsonTree::document((array)$document, ($page - 1) * PAGE_SIZE + $i + 1) ?>
                <?php endforeach; ?>
            </div>
            <?php if ($pages > 1): ?>
                <?php
                $link = static fn(int $target): string => 'mongo.php?db=' . rawurlencode($database)
                        . '&collection=' . rawurlencode($collection) . '&page=' . $target;
                $window = range(max(1, $page - 2), min($pages, $page + 2));
                ?>
                <nav aria-label="Document pages">
                    <ul class="pagination">
                        <li class="<?= $page <= 1 ? 'disabled' : '' ?>"><a href="<?= e($link(max(1, $page - 1))) ?>">&laquo;
                                Previous</a></li>
                        <?php if ($window[0] > 1): ?>
                            <li><a href="<?= e($link(1)) ?>">1</a></li>
                        <?php endif; ?>
                        <?php foreach ($window as $number): ?>
                            <li class="<?= $number === $page ? 'active' : '' ?>"><a
                                        href="<?= e($link($number)) ?>"><?= $number ?></a></li>
                        <?php endforeach; ?>
                        <?php if (end($window) < $pages): ?>
                            <li><a href="<?= e($link($pages)) ?>"><?= $pages ?></a></li>
                        <?php endif; ?>
                        <li class="<?= $page >= $pages ? 'disabled' : '' ?>"><a
                                    href="<?= e($link(min($pages, $page + 1))) ?>">Next &raquo;</a></li>
                    </ul>
                    <p class="text-muted">Page <?= $page ?> of <?= $pages ?></p>
                </nav>
            <?php endif; ?>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
