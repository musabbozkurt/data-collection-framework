<?php

declare(strict_types=1);

require_once __DIR__ . '/bootstrap.php';

use App\Auth;
use App\CommandCatalog;
use App\Csrf;
use App\PythonServerClient;

const MAX_KEYWORDS = 5;
const SCRAPE_TIMEOUT_SECONDS = 180;
const DEFAULT_KEYWORDS = ['Data Science', 'MongoDB Atlas', 'Python Web Scraping', 'OpenAI API'];

$user = Auth::user();
if (!$user) {
    redirect('login.php');
}

$result = null;
$error = null;
$keywords = implode("\n", DEFAULT_KEYWORDS);
$limit = 3;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $keywords = is_string($_POST['keywords'] ?? null) ? trim($_POST['keywords']) : '';
    $limit = filter_var($_POST['limit'] ?? null, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 5]]);
    $list = array_values(array_unique(array_filter(array_map('trim', preg_split('/[,\r\n]+/', $keywords) ?: []))));

    if (!Csrf::valid()) {
        http_response_code(403);
        $error = 'Invalid or expired form token. Please try again.';
    } elseif ($list === [] || count($list) > MAX_KEYWORDS) {
        $error = 'Enter between 1 and ' . MAX_KEYWORDS . ' keywords (one per line or comma separated).';
    } elseif ($limit === false) {
        $error = 'Pages per keyword must be a number between 1 and 5.';
    } else {
        $result = PythonServerClient::fromEnv()->send(
                'scrapexbatch',
                ['keywords' => implode(',', $list), 'limit' => $limit],
                SCRAPE_TIMEOUT_SECONDS,
        );
    }
}

render('header', ['title' => 'X Scraper', 'active' => '']);
?>
<div class="app-shell">
    <?php render('menu', ['groupNames' => array_keys(CommandCatalog::groups()), 'current' => 'scraper']); ?>
    <div class="content">
        <h1>X Scraper</h1>
        <p>Collects public X pages for your keywords through web search and stores them in MongoDB
            (<code>x_batch_db.tweets_by_keywords</code>). It needs no X API credits. A run takes several seconds
            per page, so please wait for the result.</p>

        <?php if ($error): ?>
            <div class="alert alert-danger" role="alert"><?= e($error) ?></div>
        <?php elseif ($result): ?>
            <div class="alert alert-<?= $result['ok'] ? 'success' : 'danger' ?>" role="alert">
                <pre class="scraper-result"><?= e($result['message']) ?></pre>
            </div>
        <?php endif; ?>

        <form method="post" action="scraper.php" class="command-form">
            <?= Csrf::field() ?>
            <div class="form-group">
                <label for="keywords">Keywords (one per line or comma separated, up to <?= MAX_KEYWORDS ?>)</label>
                <textarea class="form-control" id="keywords" name="keywords" rows="4" maxlength="400"
                          required><?= e($keywords) ?></textarea>
            </div>
            <div class="form-group">
                <label for="limit">Pages per keyword</label>
                <input class="form-control" id="limit" name="limit" type="number" min="1" max="5"
                       value="<?= e((string)($limit === false ? 3 : $limit)) ?>" required>
            </div>
            <button type="submit" class="btn btn-primary" id="scrape-submit">Collect</button>
        </form>
    </div>
</div>
<?php render('footer'); ?>
