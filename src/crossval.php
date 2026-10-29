<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\Chart;
use App\CommandCatalog;
use App\MongoSource;
use App\PythonServerClient;

const CV_TIMEOUT_SECONDS = 300;
const DEFAULTS = ['folds' => 5, 'splits' => 5, 'test_size' => 0.25, 'random_state' => 42, 'train_test_size' => 0.25,
        'svm_c' => 1];

if (!Auth::user()) {
    redirect('login.php');
}

$run = isset($_GET['run']);
$input = [];
foreach (DEFAULTS as $name => $default) {
    $raw = is_string($_GET[$name] ?? null) ? trim($_GET[$name]) : '';
    $input[$name] = is_numeric($raw) ? $raw : (string)$default;
}

$client = PythonServerClient::fromEnv();
$result = null;
[$overview, $database, $collection, $error] = MongoSource::resolve($client, 60);
$fields = $error || $collection === '' ? ['text' => [], 'labels' => []] : MongoSource::textFields($client, $database, $collection, 60);
$textField = MongoSource::pick($fields['text'], $_GET['text_field'] ?? null);
$labelField = MongoSource::pick($fields['labels'], $_GET['label_field'] ?? null);
if ($run && !$error && $textField !== '' && $labelField !== '') {
    $reply = $client->send('mongocrossvalidation', ['database' => $database, 'collection' => $collection,
                    'text_field' => $textField, 'label_field' => $labelField] + $input, CV_TIMEOUT_SECONDS);
    $decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($decoded) && isset($decoded['classes'])) {
        $result = $decoded;
    } else {
        $error = $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message'];
    }
}

$percent = static fn(float $v): string => number_format($v * 100, 1) . '%';
$series = static function (array $values, string $prefix): array {
    $items = [];
    foreach (array_values($values) as $i => $v) {
        $items[] = ['label' => $prefix . ($i + 1), 'value' => round((float)$v, 3)];
    }
    return $items;
};

render('header', ['title' => 'Cross Validation', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'crossval']); ?>
    <div class="content">
        <h1>Cross Validation (MongoDB)</h1>
        <p class="text-muted">Checks how well a program can predict a <strong>label</strong> (for tweets: who wrote
            them) from the <strong>text</strong> alone. It learns from part of the documents and is then tested on the
            rest, which is repeated <em>folds</em> times; the closer the scores are to 100%, the more the texts of each
            label differ from the others.</p>
        <ul class="text-muted">
            <li>Pick the database and collection, then the field that holds the text and the field to predict
                (the lists show what the selected collection contains).
            </li>
            <li>You need at least two labels with at least as many documents as the number of folds.</li>
            <li><strong>Accuracy</strong> is the share of documents guessed correctly; <strong>F1</strong> balances
                precision and recall across labels. The matrix shows which labels get mixed up.
            </li>
            <li>The defaults are a good start; change them only to experiment.</li>
        </ul>

        <form method="get" action="crossval.php" class="analytics-form" data-refresh>
            <input type="hidden" name="run" value="1" data-run-only>
            <div class="form-inline"><?= MongoSource::fields($overview, $database, $collection) ?></div>
            <div class="form-inline">
                <?= MongoSource::select('text_field', 'Text field', $fields['text'], $textField) ?>
                <?= MongoSource::select('label_field', 'Label field (what to predict)', $fields['labels'], $labelField) ?>
            </div>
            <?php if ($fields['text'] === [] || $fields['labels'] === []): ?>
                <p class="text-muted">This collection has no text field or no label field (a field with a few repeated
                    values, such as the profile name), so it cannot be used here.</p>
            <?php endif; ?>
            <?php foreach ([
                                   'folds' => ['Folds', 2, 100, 1, 'Number of parts the data is cut into. Each part is used once for testing while the others train. More folds = more reliable but slower.'],
                                   'splits' => ['Shuffle splits', 1, 100, 1, 'How many times the data is shuffled and split again into a random train and test part. More splits = a steadier average.'],
                                   'test_size' => ['Shuffle test size', 0.01, 0.99, 0.01, 'Share of the documents kept for testing in each shuffle split (0.2 = 20%).'],
                                   'random_state' => ['Random state', 0, 999999, 1, 'Seed for the shuffling. The same number gives the same split, so results can be repeated.'],
                                   'train_test_size' => ['Hold-out test size', 0.01, 0.99, 0.01, 'Share of the documents set aside for one final test, used for the confusion matrix and the report (0.2 = 20%).'],
                                   'svm_c' => ['SVM C', 1, 10000, 1, 'Strictness of the SVM classifier. A higher value fits the training data more closely but may overfit; a lower value is more forgiving.'],
                           ] as $name => [$label, $min, $max, $step, $help]): ?>
                <div class="form-group">
                    <label for="<?= e($name) ?>"><?= e($label) ?></label>
                    <input class="form-control" id="<?= e($name) ?>" name="<?= e($name) ?>" type="number"
                           min="<?= $min ?>" max="<?= $max ?>" step="<?= $step ?>" value="<?= e($input[$name]) ?>"
                           aria-describedby="<?= e($name) ?>-help">
                    <p class="help-block" id="<?= e($name) ?>-help"><?= e($help) ?></p>
                </div>
            <?php endforeach; ?>
            <button type="submit" class="btn btn-primary">Run</button>
        </form>

        <?php if ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php elseif ($result): ?>
            <p><strong><?= (int)$result['documents'] ?></strong> documents,
                <strong><?= (int)$result['features'] ?></strong> terms,
                <?= count($result['classes']) ?> labels:
                <?php foreach ($result['class_sizes'] as $name => $size): ?>
                    <?= e((string)$name) ?> (<?= (int)$size ?>)
                <?php endforeach; ?></p>

            <table class="table">
                <tbody>
                <tr>
                    <th>Mean accuracy (k-fold)</th>
                    <td><?= $percent((float)$result['mean_accuracy']) ?>
                        &plusmn; <?= $percent((float)$result['confidence_margin']) ?> (95%)
                    </td>
                </tr>
                <tr>
                    <th>Mean F1 macro (k-fold)</th>
                    <td><?= $percent((float)$result['mean_f1_macro']) ?></td>
                </tr>
                <tr>
                    <th>Accuracy of the k-fold predictions</th>
                    <td><?= $percent((float)$result['cross_val_predict_accuracy']) ?></td>
                </tr>
                <tr>
                    <th>Hold-out accuracy (Naive Bayes)</th>
                    <td><?= $percent((float)$result['holdout_accuracy']) ?></td>
                </tr>
                </tbody>
            </table>

            <h3>Accuracy per fold</h3>
            <div class="chart-box"><?= Chart::columns($series($result['accuracy_scores'], 'fold '), 'accuracy') ?></div>
            <h3>F1 macro per fold</h3>
            <div class="chart-box"><?= Chart::columns($series($result['f1_macro_scores'], 'fold '), 'f1') ?></div>
            <h3>Accuracy per shuffle split</h3>
            <div class="chart-box"><?= Chart::columns($series($result['shuffle_scores'], 'split '), 'accuracy') ?></div>
            <h3>Documents per label</h3>
            <div class="chart-box"><?= Chart::pie(array_map(
                        static fn($name, $size) => ['label' => (string)$name, 'value' => $size],
                        array_keys($result['class_sizes']), array_values($result['class_sizes']))) ?></div>

            <h3>Confusion matrix <small>rows = actual, columns = predicted</small></h3>
            <table class="table matrix">
                <thead>
                <tr>
                    <th></th><?php foreach ($result['classes'] as $name): ?>
                        <th><?= e((string)$name) ?></th><?php endforeach; ?></tr>
                </thead>
                <tbody>
                <?php foreach ($result['confusion_matrix'] as $r => $row): ?>
                    <tr>
                        <th><?= e((string)$result['classes'][$r]) ?></th>
                        <?php foreach ($row as $cell): ?>
                            <td><?= (int)$cell ?></td><?php endforeach; ?></tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
