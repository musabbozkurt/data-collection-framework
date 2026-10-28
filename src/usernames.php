<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;

const MAX_UPLOAD_BYTES = 40000;

/** Validates an uploaded .txt file and sends it to the Python server as the new username list. */
function loadFile(PythonServerClient $client, array $file): array
{
    if ($file['error'] !== UPLOAD_ERR_OK) {
        return ['ok' => false, 'message' => 'The file could not be uploaded.'];
    }
    if (strtolower(pathinfo((string)$file['name'], PATHINFO_EXTENSION)) !== 'txt' || (int)$file['size'] > MAX_UPLOAD_BYTES) {
        return ['ok' => false, 'message' => 'Only .txt files up to ' . MAX_UPLOAD_BYTES . ' bytes are supported.'];
    }
    return $client->send('saveusernames', ['data' => base64_encode((string)file_get_contents($file['tmp_name']))]);
}

if (!Auth::user()) {
    redirect('login.php');
}

$client = PythonServerClient::fromEnv();

if (isset($_GET['template'])) {
    $reply = $client->send('usernamestemplate', []);
    if ($reply['ok']) {
        header('Content-Type: text/plain; charset=utf-8');
        header('Content-Disposition: attachment; filename="usernames.template.txt"');
        echo $reply['message'];
        exit;
    }
}

const ACTIONS = ['load' => null, 'tweets' => 'collecttweetfromuserlist', 'followers' => 'collectfollowerfromuserlist'];
const RUN_TIMEOUT_SECONDS = 3600;

$result = null;
$tweetCount = filter_var($_POST['tweet_count'] ?? 100, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 3200, 'default' => 100]]);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = is_string($_POST['action'] ?? null) && array_key_exists($_POST['action'], ACTIONS) ? $_POST['action'] : 'load';
    $file = $_FILES['usernames'] ?? null;
    $hasFile = is_array($file) && ($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE;
    if (!Csrf::valid()) {
        http_response_code(403);
        $result = ['ok' => false, 'message' => 'Invalid or expired form token. Please try again.'];
    } elseif ($action === 'load' && !$hasFile) {
        $result = ['ok' => false, 'message' => 'Choose a .txt file to load.'];
    } else {
        if ($hasFile) {
            $result = loadFile($client, $file);
        }
        if (ACTIONS[$action] !== null && (!$result || $result['ok'])) {
            $args = $action === 'tweets' ? ['tweet_count' => $tweetCount] : [];
            $run = $client->send(ACTIONS[$action], $args, RUN_TIMEOUT_SECONDS);
            $result = ['ok' => $run['ok'], 'message' => trim(($result['message'] ?? '') . ' ' . $run['message'])];
        }
    }
}

$names = [];
$reply = $client->send('listusernames', []);
$decoded = $reply['ok'] ? json_decode($reply['message'], true) : null;
if (is_array($decoded)) {
    $names = $decoded;
} elseif (!$result || $result['ok']) {
    $result = ['ok' => false, 'message' => $reply['ok'] ? 'Unexpected reply from the Python server.' : $reply['message']];
}

render('header', ['title' => 'Username list', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'usernames']); ?>
    <div class="content">
        <h1>Username list</h1>
        <p class="text-muted">Used by "Collect tweets/followers from the user list". Loading a file replaces the
            current list (other <code>.txt</code> files in that folder are renamed to <code>.txt.bak</code>).</p>

        <?php if ($result): ?>
            <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>"
                 role="alert"><?= e($result['message']) ?></div>
        <?php endif; ?>

        <form method="post" action="usernames.php" enctype="multipart/form-data" class="analytics-form">
            <?= Csrf::field() ?>
            <div class="form-group">
                <label for="usernames">Load a file (<code>.txt</code>, one or more usernames per line)</label>
                <input class="form-control" id="usernames" name="usernames" type="file" accept=".txt">
            </div>
            <div class="form-group">
                <label for="tweet_count">Tweets per user</label>
                <input class="form-control" id="tweet_count" name="tweet_count" type="number" min="1" max="3200"
                       value="<?= (int)$tweetCount ?>">
            </div>
            <button type="submit" name="action" value="load" class="btn btn-primary">Load file</button>
            <button type="submit" name="action" value="tweets" class="btn btn-success">Collect tweets</button>
            <button type="submit" name="action" value="followers" class="btn btn-success">Collect followers</button>
            <a class="btn btn-default" href="usernames.php?template=1">Download example template</a>
            <p class="help-block">Collect tweets / followers uses the chosen file when there is one, otherwise the
                current list.</p>
        </form>

        <h3>Current list <small><?= count($names) ?> usernames</small></h3>
        <?php if ($names === []): ?>
            <p>No usernames yet.</p>
        <?php else: ?>
            <p><?php foreach ($names as $name): ?><span class="label label-default">
                    @<?= e((string)$name) ?></span> <?php endforeach; ?></p>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
