<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\AnalysisOptions;
use App\Auth;
use App\Chart;
use App\CommandCatalog;
use App\MongoSource;
use App\PythonServerClient;

const TERMS_TIMEOUT_SECONDS = 120;

if (!Auth::user()) {
    redirect('login.php');
}

$count = static fn(string $name, int $default, int $max): int => min($max, max(1, (int)($_GET[$name] ?? $default)));
$mostCommon = $count('most_common', 10, 100);
$maxPairs = $count('max_pairs', 10, 100);
$search = is_string($_GET['search_word'] ?? null) ? trim($_GET['search_word']) : '';
if (preg_match('/^\S{1,100}$/', $search) !== 1) {
    $search = '';
}

$client = PythonServerClient::fromEnv();
[$overview, $database, $collection, $error] = MongoSource::resolve($client, 60);
$fields = $error || $collection === '' ? ['text' => [], 'labels' => []] : MongoSource::textFields($client, $database, $collection, 60);
$type = is_string($_GET['type'] ?? null) && isset(AnalysisOptions::CHART_TYPES[$_GET['type']]) ? $_GET['type'] : 'bars';
$textField = MongoSource::pick($fields['text'], $_GET['text_field'] ?? null);

$result = null;
if (isset($_GET['run']) && !$error && $textField !== '') {
    $reply = $client->send('mongoterms', ['database' => $database, 'collection' => $collection, 'text_field' => $textField,
            'most_common' => (string)$mostCommon, 'max_pairs' => (string)$maxPairs, 'search_word' => $search === '' ? '-' : $search],
            TERMS_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($decoded) && isset($decoded['terms'])) {
        $result = $decoded;
    } else {
        $error = $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message'];
    }
}

$items = static function (array $rows, bool $pairs = false): array {
    $items = [];
    foreach ($rows as $row) {
        $items[] = ['label' => $pairs ? implode(' + ', (array)$row[0]) : (string)$row[0], 'value' => (int)$row[1]];
    }
    return $items;
};

$sections = [];
if ($result) {
    $sections = [
            ['Most common terms', 'Words used most often (common stop words removed).', $items($result['terms']['terms'] ?? [])],
            ['Most common hashtags', 'Hashtags used most often.', $items($result['terms']['hashtags'] ?? [])],
            ['Terms that appear together', 'Pairs of words found in the same document.', $items($result['pairs'], true)],
    ];
    if ($result['search_word'] !== '') {
        $sections[] = ['Appears together with "' . $result['search_word'] . '"', 'Words that occur in the same document as the search word.',
                $items($result['search'])];
    }
}

render('header', ['title' => 'Term Frequency', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'terms']); ?>
    <div class="content">
        <h1>Term Frequency (MongoDB)</h1>
        <p class="text-muted">Counts which words, hashtags and word pairs occur most often in the text of the documents
            stored in a MongoDB collection.</p>
        <ul class="text-muted">
            <li>Pick the database, collection and the field that holds the text (the lists follow your data).</li>
            <li>Optionally type a word to see which words appear in the same documents as it.</li>
            <li>Press Run; every list is shown as a chart and a table.</li>
        </ul>

        <form method="get" action="terms.php" class="analytics-form" data-refresh>
            <input type="hidden" name="run" value="1" data-run-only>
            <div class="form-inline"><?= MongoSource::fields($overview, $database, $collection) ?></div>
            <div class="form-inline">
                <?= MongoSource::select('text_field', 'Text field', $fields['text'], $textField) ?>
                <label for="most_common">Top terms (most frequent words to list)</label>
                <input class="form-control" id="most_common" name="most_common" type="number" min="1" max="100"
                       value="<?= $mostCommon ?>">
                <label for="max_pairs">Top pairs (word pairs that appear together)</label>
                <input class="form-control" id="max_pairs" name="max_pairs" type="number" min="1" max="100"
                       value="<?= $maxPairs ?>">
                <label for="search_word">Search word (show words that appear with it)</label>
                <input class="form-control" id="search_word" name="search_word" type="text" maxlength="100"
                       value="<?= e($search) ?>" placeholder="optional">
                <label for="type">as (chart type)</label>
                <select class="form-control" id="type" name="type">
                    <?php foreach (AnalysisOptions::CHART_TYPES as $key => $label): ?>
                        <option value="<?= e($key) ?>"<?= $key === $type ? ' selected' : '' ?>><?= e($label) ?></option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" class="btn btn-primary"<?= $textField === '' ? ' disabled' : '' ?>>Run</button>
            </div>
            <?php if ($textField === '' && !$error): ?>
                <p class="text-muted">This collection has no text field to analyse.</p>
            <?php endif; ?>
        </form>

        <?php if ($error): ?>
            <p class="text-danger"><?= e($error) ?></p>
        <?php endif; ?>
        <?php if ($result): ?>
            <p class="text-muted"><?= (int)$result['documents'] ?> documents analysed.</p>
            <?php foreach ($sections as [$title, $help, $rows]): ?>
                <h3><?= e($title) ?></h3>
                <p class="text-muted"><?= e($help) ?></p>
                <?php if ($rows === []): ?>
                    <p>Nothing found.</p>
                <?php else: ?>
                    <?= Chart::view($rows, $type, 'count', 'Term') ?>
                <?php endif; ?>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
