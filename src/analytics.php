<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\AnalysisOptions;
use App\Auth;
use App\Chart;
use App\CommandCatalog;
use App\MongoSource;
use App\PythonServerClient;

const REQUEST_TIMEOUT_SECONDS = 60;

if (!Auth::user()) {
    redirect('login.php');
}

$requestedMetric = is_string($_GET['metric'] ?? null) ? $_GET['metric'] : '';
$top = filter_var($_GET['top'] ?? 10, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 100, 'default' => 10]]);
$n = filter_var($_GET['n'] ?? 2, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 5, 'default' => 2]]);
$type = is_string($_GET['type'] ?? null) && isset(AnalysisOptions::CHART_TYPES[$_GET['type']]) ? $_GET['type'] : 'bars';
$profile = is_string($_GET['profile'] ?? null) && preg_match('/^\w{1,15}$/', $_GET['profile']) === 1
        ? $_GET['profile'] : '';

$client = PythonServerClient::fromEnv();
$error = null;
$authors = [];
$chart = null;

[$overview, $database, $collection, $error] = MongoSource::resolve($client, REQUEST_TIMEOUT_SECONDS);

/** The analyses of the selected collection, worked out by the Python server from its documents. */
$metrics = [];
if (!$error && $collection !== '') {
    $reply = $client->send('analysismetrics', ['database' => $database, 'collection' => $collection], REQUEST_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    $metrics = is_array($decoded) ? $decoded : AnalysisOptions::fallback();
}
$metricKeys = array_column($metrics, 'key');
$metric = in_array($requestedMetric, $metricKeys, true) ? $requestedMetric : (string)($metricKeys[0] ?? '');

if (!$error && $collection !== '') {
    $reply = $client->send('tweetauthors', ['database' => $database, 'collection' => $collection], REQUEST_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    $authors = is_array($decoded) ? $decoded : [];
}

if (!$error && $metric !== '') {
    $reply = $client->send('mongoanalytics',
            ['database' => $database, 'collection' => $collection, 'metric' => $metric, 'top' => $top, 'username' => $profile === '' ? '-' : $profile, 'n' => $n],
            REQUEST_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($decoded) && isset($decoded['items'], $decoded['title'])) {
        $chart = $decoded;
    } else {
        $error = $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message'];
    }
}

render('header', ['title' => 'Analytics', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'analytics']); ?>
    <div class="content">
        <h1>Analytics &amp; Charts</h1>
        <p class="text-muted">Turn the documents stored in a MongoDB collection into a chart.
            <strong>1.</strong> Pick a database and collection (the list of analyses below adapts to what the
            collection contains). <strong>2.</strong> Pick what to show. <strong>3.</strong> Optionally narrow it to
            one profile, choose how many entries to list and the chart type, then press Update.</p>

        <?php if ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php endif; ?>
        <?php if ($overview !== []): ?>
            <form method="get" action="analytics.php" class="form-inline analytics-form" data-refresh>
                <?= MongoSource::fields($overview, $database, $collection) ?>
                <label for="metric">Show</label>
                <select class="form-control" id="metric" name="metric">
                    <?php foreach (array_unique(array_column($metrics, 'group')) as $group): ?>
                        <optgroup label="<?= e((string)$group) ?>">
                            <?php foreach ($metrics as $item): ?>
                                <?php if ($item['group'] === $group): ?>
                                    <option value="<?= e((string)$item['key']) ?>"<?= selected($item['key'] === $metric) ?>><?= e((string)$item['label']) ?></option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </optgroup>
                    <?php endforeach; ?>
                </select>
                <?php if ($authors !== []): ?>
                    <label for="profile">for</label>
                    <select class="form-control" id="profile" name="profile">
                        <option value="">all profiles</option>
                        <?php foreach ($authors as $author): ?>
                            <option value="<?= e((string)$author) ?>"<?= selected($author === $profile) ?>>
                                @<?= e((string)$author) ?></option>
                        <?php endforeach; ?>
                    </select>
                <?php endif; ?>
                <label for="top">top (how many rows)</label>
                <input class="form-control" id="top" name="top" type="number" min="1" max="100"
                       value="<?= (int)$top ?>">
                <label for="n">n (n-gram size)</label>
                <input class="form-control" id="n" name="n" type="number" min="1" max="5" value="<?= (int)$n ?>"
                       title="n-gram size: how many consecutive words or characters form one item (used by the n-gram analyses only)">
                <label for="type">as (chart type)</label>
                <select class="form-control" id="type" name="type">
                    <?php foreach (AnalysisOptions::CHART_TYPES as $key => $label): ?>
                        <option value="<?= e($key) ?>"<?= selected($key === $type) ?>><?= e($label) ?></option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" class="btn btn-primary">Update</button>
            </form>

            <?php if ($metrics === [] && !$error): ?>
                <p>There is nothing to analyse in <code><?= e($database . '.' . $collection) ?></code> yet (it is empty
                    or has no suitable fields). <a href="discover.php">Discover</a>, <a href="profile.php">scrape</a> or
                    <a href="store.php">store</a> some documents first.</p>
            <?php endif; ?>
            <?php if ($chart): ?>
                <?php $items = $chart['items']; ?>
                <h3><?= e((string)$chart['title']) ?>
                    <small><?= (int)$chart['tweets'] ?> documents analysed</small></h3>
                <?php if (($chart['description'] ?? '') !== ''): ?>
                    <p class="text-muted"><?= e((string)$chart['description']) ?></p>
                <?php endif; ?>
                <?php if ($items === []): ?>
                    <p>Nothing to show for this selection.</p>
                <?php else: ?>
                    <?= Chart::view($items, $type, (string)$chart['unit']) ?>
                <?php endif; ?>
            <?php endif; ?>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
