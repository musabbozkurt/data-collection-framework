<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;

const PROFILE_TIMEOUT_SECONDS = 600;
const MAX_TWEETS = 500;

if (!Auth::user()) {
    redirect('login.php');
}

$result = null;
$error = null;
$username = '';
$maxTweets = 50;
$resume = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = is_string($_POST['username'] ?? null) ? ltrim(trim($_POST['username']), '@') : '';
    $maxTweets = filter_var($_POST['max_tweets'] ?? null, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => MAX_TWEETS]]);
    $resume = isset($_POST['resume']);

    if (!Csrf::valid()) {
        http_response_code(403);
        $error = 'Invalid or expired form token. Please try again.';
    } elseif (preg_match('/^[A-Za-z0-9_]{1,15}$/', $username) !== 1) {
        $error = 'Enter a valid X username (letters, digits and underscores, up to 15 characters).';
    } elseif ($maxTweets === false) {
        $error = 'New tweets must be a number between 1 and ' . MAX_TWEETS . '.';
    } else {
        $result = PythonServerClient::fromEnv()->send(
                'scrapexprofile',
                ['username' => $username, 'max_tweets' => $maxTweets, 'resume' => $resume ? 'yes' : 'no'],
                PROFILE_TIMEOUT_SECONDS,
        );
    }
}

render('header', ['title' => 'X Profile Scraper', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'profile']); ?>
    <div class="content">
        <h1>X Profile Scraper</h1>
        <p>Collects the latest public posts of an X profile without any login (usually the newest handful). Results
            are saved as JSON and CSV with a checkpoint, and as MongoDB documents in
            <code>x_profile_db.profile_tweets</code>. Optional: run <code>make x-login</code> once to let the server
            scroll deeper with a saved session.</p>

        <?php if ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php elseif ($result): ?>
            <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>" role="alert">
                <pre class="scraper-result"><?= e($result['message']) ?></pre>
            </div>
        <?php endif; ?>

        <form method="post" action="profile.php" class="command-form">
            <?= Csrf::field() ?>
            <div class="form-group">
                <label for="username">X username</label>
                <input class="form-control" id="username" name="username" type="text" maxlength="16"
                       pattern="@?[A-Za-z0-9_]{1,15}" placeholder="NASA" value="<?= e($username) ?>" required>
            </div>
            <div class="form-group">
                <label for="max_tweets">New tweets to collect (1&ndash;<?= MAX_TWEETS ?>)</label>
                <input class="form-control" id="max_tweets" name="max_tweets" type="number" min="1"
                       max="<?= MAX_TWEETS ?>" value="<?= e((string)($maxTweets === false ? 50 : $maxTweets)) ?>"
                       required>
            </div>
            <div class="checkbox">
                <label><input type="checkbox" name="resume" value="1"<?= $resume ? ' checked' : '' ?>>
                    Keep earlier results and add only new tweets (resume)</label>
            </div>
            <button type="submit" class="btn btn-primary" id="profile-submit">Scrape profile</button>
        </form>
    </div>
</div>
<?php render('footer'); ?>
