<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\AppException;
use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;
use App\Upload;

const NAME_PATTERN = '/^[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}$/';
const STORE_TIMEOUT_SECONDS = 300;

if (!Auth::user()) {
    redirect('login.php');
}

$client = PythonServerClient::fromEnv();
$result = null;
$error = null;
$database = 'tweets_db';
$collection = 'tweets';
$reply = $client->send('mongodatabases', [], 60);
$decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
$overview = is_array($decoded) ? $decoded : [];
$newDatabase = '';
$newCollection = '';
$field = static fn(string $name): string => is_string($_POST[$name] ?? null) ? trim($_POST[$name]) : '';
$chosen = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $newDatabase = $field('new_database');
    $newCollection = $field('new_collection');
    $database = $field('database') === 'new' ? $newDatabase : $field('database');
    $collection = $field('collection') === 'new' ? $newCollection : $field('collection');
    $chosen = array_values(array_filter((array)($_POST['files'] ?? []), 'is_string'));
    $uploads = $_FILES['uploads'] ?? null;
    $uploaded = Upload::chosen($uploads);

    if (!Csrf::valid()) {
        http_response_code(403);
        $error = 'Invalid or expired form token. Please try again.';
    } elseif (preg_match(NAME_PATTERN, $database) !== 1 || preg_match(NAME_PATTERN, $collection) !== 1) {
        $error = 'Database and collection: letters, digits, _ . - (up to 64 characters).';
    } elseif ($chosen === [] && $uploaded === []) {
        $error = 'Select at least one file.';
    } elseif ($uploaded !== []) {
        try {
            $total = Upload::store($client, $uploads, $uploaded, $database, $collection, STORE_TIMEOUT_SECONDS);
            $result = ['ok' => true, 'message' => "Stored $total documents from " . count($uploaded)
                    . " uploaded file(s) into $database.$collection"];
        } catch (AppException $e) {
            $error = $e->getMessage();
        }
    } else {
        $result = $client->send('storefiles',
                ['database' => $database, 'collection' => $collection, 'files' => implode(',', $chosen)],
                STORE_TIMEOUT_SECONDS);
    }
}

$files = [];
$reply = $client->send('listdatafiles', []);
$decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
if (is_array($decoded)) {
    $files = $decoded;
} else {
    $error ??= $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message'];
}

$size = static function (int $bytes): string {
    if ($bytes >= 1048576) {
        return number_format($bytes / 1048576, 1) . ' MB';
    }
    return number_format(max(1, $bytes) / 1024, 1) . ' KB';
};

render('header', ['title' => 'Store Data', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'store']); ?>
    <div class="content">
        <h1>Store Data in MongoDB</h1>
        <p class="text-muted">Pick collected files, or choose your own <code>.txt</code> (one JSON document per line) or
            <code>.json</code> files, and load them into a collection. Storing a file twice adds its documents twice.
        </p>

        <?php if ($result): ?>
            <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>" role="alert">
                <?= e($result['message']) ?>
                <?php if ($result['ok']): ?> &middot; <a
                        href="mongo.php?db=<?= e(rawurlencode($database)) ?>&amp;collection=<?= e(rawurlencode($collection)) ?>">
                        view</a><?php endif; ?>
            </div>
        <?php elseif ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php endif; ?>

        <form method="post" action="store.php" enctype="multipart/form-data" id="store-form">
            <?= Csrf::field() ?>
            <div class="form-inline analytics-form">
                <label for="database">Database</label>
                <select class="form-control" id="database" name="database" data-store-db>
                    <?php foreach ($overview as $name => $collections): ?>
                        <option value="<?= e((string)$name) ?>"<?= selected($name === $database) ?>><?= e((string)$name) ?></option>
                    <?php endforeach; ?>
                    <option value="new"<?= selected(!isset($overview[$database])) ?>>+ New database...</option>
                </select>
                <input class="form-control" id="new_database" name="new_database" aria-label="New database name"
                       type="text" maxlength="64"
                       placeholder="new database name" value="<?= e($newDatabase) ?>" data-store-new-db>
                <label for="collection">Collection</label>
                <select class="form-control" id="collection" name="collection" data-store-collection>
                    <?php foreach ($overview as $name => $collections): ?>
                        <?php foreach ($collections as $c => $count): ?>
                            <option value="<?= e((string)$c) ?>"
                                    data-db="<?= e((string)$name) ?>"<?= selected($name === $database && $c === $collection) ?>><?= e((string)$c) ?>
                                (<?= (int)$count ?>)
                            </option>
                        <?php endforeach; ?>
                    <?php endforeach; ?>
                    <option value="new" data-db="*"<?= selected(!isset($overview[$database][$collection])) ?>>+
                        New collection...
                    </option>
                </select>
                <input class="form-control" id="new_collection" name="new_collection" aria-label="New collection name"
                       type="text" maxlength="64"
                       placeholder="new collection name" value="<?= e($newCollection) ?>" data-store-new-collection>
                <button type="submit" class="btn btn-primary">Store selected</button>
            </div>
            <div class="form-group">
                <label for="uploads">Or choose files from your computer (<code>.txt</code> or
                    <code>.json</code>)</label>
                <input class="form-control" id="uploads" name="uploads[]" type="file" accept=".txt,.json" multiple>
            </div>
            <?php if ($files === []): ?>
                <p>No data files yet. Files appear here after you collect tweets or stream, or when you put
                    <code>.txt</code> or <code>.json</code> files in <code>data_folders</code> or
                    <code>x_profile_data</code>.</p>
            <?php else: ?>
                <table class="table profiles-table">
                    <thead>
                    <tr>
                        <th><input type="checkbox" id="store-all" aria-label="Select all files"></th>
                        <th>File</th>
                        <th>Folder</th>
                        <th>Size</th>
                    </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($files as $file): ?>
                        <tr>
                            <td><input type="checkbox" class="file-check" name="files[]"
                                       value="<?= e((string)$file['id']) ?>"
                                       aria-label="Select <?= e((string)$file['name']) ?>"<?= in_array($file['id'], $chosen, true) ? ' checked' : '' ?>>
                            </td>
                            <td><?= e((string)$file['name']) ?></td>
                            <td><?= e((string)$file['folder']) ?></td>
                            <td><?= e($size((int)$file['size'])) ?></td>
                        </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </form>
    </div>
</div>
<?php render('footer'); ?>
