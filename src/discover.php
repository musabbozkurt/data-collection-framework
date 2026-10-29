<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;

const DISCOVER_TIMEOUT_SECONDS = 300;
const SCRAPE_TIMEOUT_SECONDS = 900;
const SELECTED_LIMIT = 5;
const LIST_PAGE_SIZE = 25;

if (!Auth::user()) {
    redirect('login.php');
}

$client = PythonServerClient::fromEnv();
$result = null;
$error = null;
$letter = strtoupper((string)($_GET['letter'] ?? 'ALL'));
$letter = preg_match('/^([A-Z]|ALL)$/', $letter) === 1 ? $letter : 'ALL';
$page = filter_var($_GET['page'] ?? 1, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'default' => 1]]);
$keyword = is_string($_GET['keyword'] ?? null) ? trim($_GET['keyword']) : '';
$keyword = preg_match('/^[\w .+#&-]{1,40}$/u', $keyword) === 1 ? $keyword : '';
$maxTweets = 5;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = is_string($_POST['action'] ?? null) ? $_POST['action'] : '';
    $maxTweets = filter_var($_POST['max_tweets'] ?? 5, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 50]]);

    if (!Csrf::valid()) {
        http_response_code(403);
        $error = 'Invalid or expired form token. Please try again.';
    } elseif ($action === 'discover') {
        $target = strtoupper((string)($_POST['discover_letter'] ?? ''));
        if (preg_match('/^([A-Z]|ALL)$/', $target) !== 1) {
            $error = 'Pick a letter from A to Z.';
        } else {
            $topic = is_string($_POST['topic'] ?? null) ? trim($_POST['topic']) : '';
            if ($topic !== '' && preg_match('/^[\w .+#&-]{1,40}$/u', $topic) !== 1) {
                $error = 'Keyword: up to 40 letters, digits, spaces or . + # & -';
            } else {
                $result = $client->send(
                        'discoverprofiles',
                        ['letter' => $target, 'keyword' => $topic === '' ? '-' : $topic],
                        DISCOVER_TIMEOUT_SECONDS,
                );
                $keyword = $topic !== '' && $result['ok'] ? $topic : $keyword;
            }
        }
    } elseif ($action === 'add') {
        $names = is_string($_POST['usernames'] ?? null) ? trim($_POST['usernames']) : '';
        $result = $names === ''
                ? ['ok' => false, 'message' => 'Enter at least one username.']
                : $client->send('addprofiles', ['usernames' => $names]);
    } elseif ($action === 'scrape') {
        $selected = array_values(array_unique(array_filter(
                is_array($_POST['selected'] ?? null) ? $_POST['selected'] : [],
                static fn($name) => is_string($name) && preg_match('/^\w{1,15}$/', $name) === 1,
        )));
        if ($selected === []) {
            $error = 'Tick at least one profile first.';
        } elseif (count($selected) > SELECTED_LIMIT) {
            $error = 'Select at most ' . SELECTED_LIMIT . ' profiles per run.';
        } elseif ($maxTweets === false) {
            $error = 'Posts per profile must be a number between 1 and 50.';
        } else {
            $result = $client->send(
                    'scrapeselected',
                    ['usernames' => implode(',', $selected), 'max_tweets' => $maxTweets],
                    SCRAPE_TIMEOUT_SECONDS,
            );
        }
    }
}
if ($maxTweets === false) {
    $maxTweets = 5;
}

$listing = ['total' => 0, 'letters' => [], 'profiles' => []];
$reply = $client->send('listprofiles', ['letter' => $letter === 'ALL' ? '-' : $letter, 'keyword' => $keyword === '' ? '-' : $keyword, 'page' => $page, 'page_size' => LIST_PAGE_SIZE]);
if ($reply['ok']) {
    $decoded = json_decode($reply['message'], true);
    if (is_array($decoded) && isset($decoded['profiles'], $decoded['total'])) {
        $listing = $decoded;
    }
} elseif ($error === null && $result === null) {
    $error = $reply['message'];
}
$pages = max(1, (int)ceil($listing['total'] / LIST_PAGE_SIZE));
$link = static fn(string $l, int $p = 1): string => 'discover.php?letter=' . rawurlencode($l) . '&page=' . $p
        . ($keyword === '' ? '' : '&keyword=' . rawurlencode($keyword));

render('header', ['title' => 'Discover Profiles', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'discover']); ?>
    <div class="content">
        <h1>Discover Profiles</h1>
        <p>Finds X usernames through web search (no X login), stores them in MongoDB
            <code>x_profile_db.discovered_profiles</code>, and lets you tick profiles to scrape their posts. Search
            returns only a few names per try, so run it several times or add usernames by hand. Without a connected
            X account only the newest ~5 posts per profile are available.</p>

        <?php if ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php elseif ($result): ?>
            <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>" role="alert">
                <pre class="scraper-result"><?= e($result['message']) ?></pre>
            </div>
        <?php endif; ?>

        <form method="post" action="<?= e($link($letter, $page)) ?>" class="command-form form-inline">
            <?= Csrf::field() ?>
            <input type="hidden" name="action" value="discover">
            <label for="discover_letter">Find profiles starting with</label>
            <select class="form-control" id="discover_letter" name="discover_letter">
                <?php foreach (range('A', 'Z') as $l): ?>
                    <option value="<?= $l ?>"<?= $l === $letter ? ' selected' : '' ?>><?= $l ?></option>
                <?php endforeach; ?>
                <option value="ALL">All letters (slow)</option>
            </select>
            <label for="topic">related to</label>
            <input class="form-control" id="topic" name="topic" type="text" maxlength="40"
                   placeholder="e.g. Java developer (optional)" value="<?= e($keyword) ?>">
            <button type="submit" class="btn btn-primary">Discover</button>
        </form>

        <form method="post" action="<?= e($link($letter, $page)) ?>" class="command-form form-inline">
            <?= Csrf::field() ?>
            <input type="hidden" name="action" value="add">
            <label for="usernames">Add usernames</label>
            <input class="form-control" id="usernames" name="usernames" type="text" maxlength="800"
                   placeholder="NASA, @elonmusk">
            <button type="submit" class="btn btn-default">Add</button>
        </form>

        <?php if (!empty($listing['keywords'])): ?>
            <p class="keyword-bar">Topics:
                <a class="btn btn-xs <?= $keyword === '' ? 'btn-primary' : 'btn-default' ?>"
                   href="discover.php?letter=<?= e(rawurlencode($letter)) ?>">any</a>
                <?php foreach ($listing['keywords'] as $topicName): ?>
                    <a class="btn btn-xs <?= strtolower($keyword) === $topicName ? 'btn-primary' : 'btn-default' ?>"
                       href="discover.php?letter=<?= e(rawurlencode($letter)) ?>&amp;keyword=<?= e(rawurlencode((string)$topicName)) ?>"><?= e((string)$topicName) ?></a>
                <?php endforeach; ?>
            </p>
        <?php endif; ?>

        <p class="letter-bar">
            <a class="btn btn-xs <?= $letter === 'ALL' ? 'btn-primary' : 'btn-default' ?>"
               href="<?= e($link('ALL')) ?>">All</a>
            <?php foreach (range('A', 'Z') as $l): ?>
                <a class="btn btn-xs <?= $l === $letter ? 'btn-primary' : 'btn-default' ?>"
                   href="<?= e($link($l)) ?>"><?= $l ?></a>
            <?php endforeach; ?>
        </p>

        <form method="post" action="<?= e($link($letter, $page)) ?>" id="scrape-selected-form">
            <?= Csrf::field() ?>
            <input type="hidden" name="action" value="scrape">
            <?php if ($listing['profiles'] === []): ?>
                <p class="text-muted">No profiles stored<?= $letter === 'ALL' ? '' : " for $letter" ?> yet.</p>
            <?php else: ?>
                <table class="table table-condensed profiles-table">
                    <thead>
                    <tr>
                        <th><input type="checkbox" id="select-all" aria-label="Select the first 5 on this page"></th>
                        <th>Username</th>
                        <th>Topics</th>
                        <th>Source</th>
                        <th>Last scraped</th>
                        <th>Posts scraped</th>
                    </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($listing['profiles'] as $profile): ?>
                        <tr>
                            <td><input type="checkbox" class="profile-check" name="selected[]"
                                       value="<?= e((string)$profile['username']) ?>"
                                       aria-label="Select <?= e((string)$profile['username']) ?>"></td>
                            <td><a href="https://x.com/<?= e(rawurlencode((string)$profile['username'])) ?>"
                                   target="_blank" rel="noopener noreferrer">@<?= e((string)$profile['username']) ?></a>
                            </td>
                            <td><?= e(implode(', ', (array)($profile['keywords'] ?? []))) ?></td>
                            <td><?= e((string)$profile['source']) ?></td>
                            <td><?= e((string)($profile['last_scraped_at'] ?? '—')) ?></td>
                            <td><?= e((string)$profile['tweets_scraped']) ?></td>
                        </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>

                <div class="form-inline">
                    <label for="max_tweets">Posts per profile</label>
                    <input class="form-control" id="max_tweets" name="max_tweets" type="number" min="1" max="50"
                           value="<?= e((string)$maxTweets) ?>">
                    <button type="submit" class="btn btn-primary" id="scrape-selected">Scrape selected
                        (max <?= SELECTED_LIMIT ?>)
                    </button>
                    <span class="text-muted" id="selected-count">0 selected</span>
                </div>
            <?php endif; ?>
        </form>

        <?php if ($pages > 1): ?>
            <nav aria-label="Profile pages">
                <ul class="pagination">
                    <li class="<?= $page <= 1 ? 'disabled' : '' ?>"><a
                                href="<?= e($link($letter, max(1, $page - 1))) ?>">&laquo; Prev</a></li>
                    <?php foreach (range(max(1, $page - 2), min($pages, $page + 2)) as $number): ?>
                        <li class="<?= $number === $page ? 'active' : '' ?>"><a
                                    href="<?= e($link($letter, $number)) ?>"><?= $number ?></a></li>
                    <?php endforeach; ?>
                    <li class="<?= $page >= $pages ? 'disabled' : '' ?>"><a
                                href="<?= e($link($letter, min($pages, $page + 1))) ?>">Next &raquo;</a></li>
                </ul>
                <p class="text-muted">Page <?= $page ?> of <?= $pages ?> &middot; <?= (int)$listing['total'] ?>
                    profiles</p>
            </nav>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
