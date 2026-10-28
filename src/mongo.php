<?php

declare(strict_types=1);

const UNEXPECTED_REPLY = 'Unexpected reply from the Python server.';
const PAGE_PARAM = '&page=';

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\JsonTree;
use App\PythonServerClient;

const NAME_PATTERN = '/^[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}$/';
const PAGE_SIZE = 10;
const GROUP_PAGE_SIZE = 20;
const REQUEST_TIMEOUT_SECONDS = 30;

if (!Auth::user()) {
    redirect('login.php');
}

$database = is_string($_GET['db'] ?? null) ? $_GET['db'] : '';
$collection = is_string($_GET['collection'] ?? null) ? $_GET['collection'] : '';
$page = filter_var($_GET['page'] ?? 1, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'default' => 1]]);
$user = is_string($_GET['user'] ?? null) && preg_match('/^\w{1,15}$/', $_GET['user']) === 1 ? $_GET['user'] : '';
$view = ($_GET['view'] ?? '') === 'all' ? 'all' : 'profiles';
$selected = preg_match(NAME_PATTERN, $database) === 1 && preg_match(NAME_PATTERN, $collection) === 1;

$client = PythonServerClient::fromEnv();
$error = null;
$overview = [];
$documents = [];
$pages = 1;
$total = 0;
$groups = [];
$groupPages = 1;
$groupTotal = 0;

$reply = $client->send('mongodatabases', [], REQUEST_TIMEOUT_SECONDS);
$decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
if (is_array($decoded)) {
    $overview = $decoded;
} else {
    $error = $reply['ok'] ? UNEXPECTED_REPLY : $reply['message'];
}

// Collections whose documents carry a username are browsed per profile; others stay a flat list.
if ($selected && !$error && $view === 'profiles') {
    $reply = $client->send('mongogroups', ['database' => $database, 'collection' => $collection,
            'page' => $user === '' ? $page : 1, 'page_size' => GROUP_PAGE_SIZE], REQUEST_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($decoded) && isset($decoded['groups'], $decoded['total'])) {
        $groups = $decoded['groups'];
        $groupTotal = (int)$decoded['total'];
        $groupPages = (int)$decoded['pages'];
        if ($user === '' && $groups !== []) {
            $page = (int)$decoded['page'];
        }
    }
}
$grouped = $groups !== [];
if ($selected && !$error && $grouped && $user !== '') {
    $reply = $client->send('mongoprofiledocuments', ['database' => $database, 'collection' => $collection,
            'username' => $user, 'page' => $page, 'page_size' => PAGE_SIZE], REQUEST_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($decoded) && isset($decoded['documents'], $decoded['page'], $decoded['pages'], $decoded['total'])) {
        $documents = $decoded['documents'];
        $page = (int)$decoded['page'];
        $pages = (int)$decoded['pages'];
        $total = (int)$decoded['total'];
    } else {
        $error = $reply['ok'] ? UNEXPECTED_REPLY : $reply['message'];
    }
    if ($user !== '' && !in_array($user, array_column($groups, 'username'), true)) {
        array_unshift($groups, ['username' => $user, 'count' => $total]);
    }
} elseif ($selected && !$error && !$grouped) {
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
        $error = $reply['ok'] ? UNEXPECTED_REPLY : $reply['message'];
    }
}

render('header', ['title' => 'MongoDB Data', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'mongo']); ?>
    <div class="content">
        <h1>MongoDB Data</h1>
        <p class="text-muted">Browse what is stored in MongoDB. Pick a collection to see its documents; tweet
            collections are grouped by profile (open a profile to read its tweets). Use
            <a href="store.php">Store Data</a> to add files and <a href="analytics.php">Analytics</a> to chart them.</p>

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
            <?php $base = 'mongo.php?db=' . rawurlencode($database) . '&collection=' . rawurlencode($collection); ?>
            <h3><?= e($database) ?> / <?= e($collection) ?>
                <?php if ($grouped): ?>
                    <small><?= e((string)$groupTotal) ?> profiles
                        &middot; <a href="<?= e($base . '&view=all') ?>">show all documents</a></small>
                <?php elseif ($view === 'all'): ?>
                    <small><a href="<?= e($base) ?>">group by profile</a></small>
                <?php endif; ?>
            </h3>

            <?php if ($grouped): ?>
                <div class="profile-groups">
                    <?php foreach ($groups as $group): ?>
                        <?php $name = (string)$group['username'];
                        $open = $name === $user; ?>
                        <details class="json-node"<?= $open ? ' open' : '' ?>>
                            <summary>
                                <a href="<?= e($base . '&user=' . rawurlencode($name)) ?>">@<?= e($name) ?></a>
                                <span class="text-muted">(<?= (int)$group['count'] ?> tweets)</span>
                            </summary>
                            <?php if ($open): ?>
                                <div class="mongo-docs">
                                    <?php foreach ($documents as $i => $document): ?>
                                        <?= JsonTree::document((array)$document, ($page - 1) * PAGE_SIZE + $i + 1) ?>
                                    <?php endforeach; ?>
                                </div>
                            <?php endif; ?>
                        </details>
                    <?php endforeach; ?>
                </div>
                <?php
                $link = static fn(int $target): string => $user === ''
                        ? $base . PAGE_PARAM . $target
                        : $base . '&user=' . rawurlencode($user) . PAGE_PARAM . $target;
                $pages = $user === '' ? $groupPages : $pages;
                ?>
            <?php else: ?>
                <?php if ($documents === []): ?>
                    <p>This collection is empty.</p>
                <?php endif; ?>
                <div class="mongo-docs">
                    <?php foreach ($documents as $i => $document): ?>
                        <?= JsonTree::document((array)$document, ($page - 1) * PAGE_SIZE + $i + 1) ?>
                    <?php endforeach; ?>
                </div>
                <?php
                $link = static fn(int $target): string => $base . ($view === 'all' ? '&view=all' : '') . PAGE_PARAM . $target;
                ?>
            <?php endif; ?>
            <?php if ($pages > 1): ?>
                <?php
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
