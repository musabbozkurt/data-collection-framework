<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;

const SECTIONS = [
        'config' => ['Application settings (config.ini)', 'Read by the Python server: database connection, Twitter API keys, streaming keywords and data folders.'],
        'env' => ['Environment (.env)', 'Read by Docker Compose and `make server`: ports, token and database passwords.'],
];
const UNEXPECTED = 'Unexpected reply from the Python server.';

if (!Auth::user()) {
    redirect('login.php');
}
if (!Auth::isAdmin()) {
    http_response_code(403);
    render('header', ['title' => 'Settings', 'active' => '']);
    echo '<div class="container"><div class="alert alert-danger" role="alert">Only the first registered account can change the settings.</div></div>';
    render('footer');
    exit;
}

$client = PythonServerClient::fromEnv();

/** Loads the current settings from the Python server; secrets only tell whether they are set. */
function loadSettings(PythonServerClient $client): array
{
    $reply = $client->send('getsettings', []);
    $rows = $reply['ok'] ? json_decode($reply['message'], true) : null;
    if (is_array($rows)) {
        return ['ok' => true, 'rows' => $rows];
    }
    return ['ok' => false, 'message' => $reply['ok'] ? UNEXPECTED : $reply['message']];
}

/** Sends only what changed: edited plain values, newly typed secrets and secrets marked to be cleared. */
function saveSettings(PythonServerClient $client, array $rows): array
{
    $values = [];
    $clear = [];
    $posted = is_array($_POST['value'] ?? null) ? $_POST['value'] : [];
    $cleared = is_array($_POST['clear'] ?? null) ? $_POST['clear'] : [];
    foreach ($rows as $row) {
        $key = $row['key'];
        $new = is_string($posted[$key] ?? null) ? trim($posted[$key]) : '';
        if ($row['secret'] && isset($cleared[$key])) {
            $clear[] = $key;
        } elseif ($new !== '' && $new !== $row['value']) {
            $values[$key] = $new;
        }
    }
    $payload = base64_encode(json_encode(['values' => (object)$values, 'clear' => $clear], JSON_THROW_ON_ERROR));
    $reply = $client->send('savesettings', ['data' => $payload]);
    if (!$reply['ok']) {
        return ['ok' => false, 'message' => $reply['message']];
    }
    $message = 'Saved. Restart the Python server to apply the changes.';
    if (in_array('env', json_decode($reply['message'], true) ?: [], true)) {
        $message = 'Saved. Restart the Python server and run "docker compose up -d" to apply the changes.';
    }
    return ['ok' => true, 'message' => $message];
}

$result = null;
$loaded = loadSettings($client);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!Csrf::valid()) {
        http_response_code(403);
        $result = ['ok' => false, 'message' => 'Invalid or expired form token. Please try again.'];
    } elseif ($loaded['ok']) {
        $result = saveSettings($client, $loaded['rows']);
        $loaded = loadSettings($client);
    }
}
if (!$loaded['ok']) {
    $result = ['ok' => false, 'message' => $loaded['message']];
}

render('header', ['title' => 'Settings', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'settings']); ?>
    <div class="content">
        <h1>Settings</h1>
        <p class="text-muted">Edit <code>config.ini</code> and <code>.env</code> from the browser. Saved secrets are
            never
            shown again: leave a secret empty to keep it, type a new value to replace it, or tick <em>clear</em> to
            remove it. Changes are written to the files and take effect after the Python server is restarted.</p>

        <?php if ($result): ?>
            <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>"
                 role="alert"><?= e($result['message']) ?></div>
        <?php endif; ?>

        <?php if ($loaded['ok']): ?>
            <form method="post" action="settings.php" class="analytics-form" autocomplete="off">
                <?= Csrf::field() ?>
                <?php foreach (SECTIONS as $file => [$title, $description]): ?>
                    <?php if (!in_array($file, array_column($loaded['rows'], 'file'), true)) {
                        continue;
                    } ?>
                    <h3><?= e($title) ?></h3>
                    <p class="text-muted"><?= e($description) ?></p>
                    <?php foreach ($loaded['rows'] as $row): ?>
                        <?php if ($row['file'] !== $file) {
                            continue;
                        } ?>
                        <?php $id = 'f_' . $row['key']; ?>
                        <div class="form-group">
                            <label for="<?= e($id) ?>"><?= e($row['label']) ?>
                                <small><code><?= e($row['key']) ?></code></small></label>
                            <?php if ($row['secret']): ?>
                                <input class="form-control" id="<?= e($id) ?>" name="value[<?= e($row['key']) ?>]"
                                       type="password" autocomplete="new-password"
                                       placeholder="<?= $row['is_set'] ? 'Saved - type to replace' : 'Not set' ?>">
                                <?php if ($row['is_set']): ?>
                                    <label class="checkbox-inline"><input type="checkbox"
                                                                          name="clear[<?= e($row['key']) ?>]"
                                                                          value="1"> clear the saved value</label>
                                <?php endif; ?>
                            <?php else: ?>
                                <input class="form-control" id="<?= e($id) ?>" name="value[<?= e($row['key']) ?>]"
                                       type="text" value="<?= e($row['value']) ?>">
                            <?php endif; ?>
                            <?php if ($row['help'] !== ''): ?>
                                <p class="help-block"><?= e($row['help']) ?></p>
                            <?php endif; ?>
                        </div>
                    <?php endforeach; ?>
                <?php endforeach; ?>
                <button type="submit" class="btn btn-primary">Save settings</button>
            </form>
        <?php endif; ?>
    </div>
</div>
<?php render('footer'); ?>
