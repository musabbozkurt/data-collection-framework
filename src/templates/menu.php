<?php
/** @var string[] $groupNames */
/** @var string $current 'home', 'scraper', 'profile', 'discover', 'mongo', 'store', 'analytics' or 'crossval' */
$onHome = $current === 'home';
$active = static fn(string $page): string => $current === $page ? ' active' : '';
?>
<div class="panel-menu">
    <?php if ($onHome): ?>
        <button type="button" class="menu-item<?= $active('home') ?>" data-tab="main">Main Page</button>
        <?php foreach ($groupNames as $i => $group): ?>
            <button type="button" class="menu-item" data-tab="tab<?= $i ?>"><?= e($group) ?></button>
        <?php endforeach; ?>
    <?php else: ?>
        <a class="menu-item" href="index.php">Main Page</a>
        <?php foreach ($groupNames as $i => $group): ?>
            <a class="menu-item" href="index.php?tab=tab<?= $i ?>"><?= e($group) ?></a>
        <?php endforeach; ?>
    <?php endif; ?>
    <a class="menu-item<?= $active('scraper') ?>" href="scraper.php">X Scraper</a>
    <a class="menu-item<?= $active('profile') ?>" href="profile.php">X Profile Scraper</a>
    <a class="menu-item<?= $active('discover') ?>" href="discover.php">Discover Profiles</a>
    <a class="menu-item<?= $active('mongo') ?>" href="mongo.php">MongoDB Data</a>
    <a class="menu-item<?= $active('store') ?>" href="store.php">Store Data in MongoDB</a>
    <a class="menu-item<?= $active('analytics') ?>" href="analytics.php">Analytics &amp; Charts</a>
    <a class="menu-item<?= $active('crossval') ?>" href="crossval.php">Cross Validation
        (MongoDB)</a>
    <a class="menu-item<?= $active('terms') ?>" href="terms.php">Term Frequency (MongoDB)</a>
    <?php if (\App\Auth::isAdmin()): ?>
        <a class="menu-item<?= $active('settings') ?>" href="settings.php">Settings</a>
    <?php endif; ?>
</div>
