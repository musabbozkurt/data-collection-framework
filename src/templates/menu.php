<?php
/** @var string[] $groupNames */
/** @var string $current 'home', 'scraper', 'profile' or 'mongo' */
$onHome = $current === 'home';
?>
<div class="panel-menu">
    <?php if ($onHome): ?>
        <button type="button" class="menu-item active" data-tab="main">Main Page</button>
        <?php foreach ($groupNames as $i => $group): ?>
            <button type="button" class="menu-item" data-tab="tab<?= $i ?>"><?= e($group) ?></button>
        <?php endforeach; ?>
    <?php else: ?>
        <a class="menu-item" href="index.php">Main Page</a>
        <?php foreach ($groupNames as $i => $group): ?>
            <a class="menu-item" href="index.php?tab=tab<?= $i ?>"><?= e($group) ?></a>
        <?php endforeach; ?>
    <?php endif; ?>
    <a class="menu-item<?= $current === 'scraper' ? ' active' : '' ?>" href="scraper.php">X Scraper</a>
    <a class="menu-item<?= $current === 'profile' ? ' active' : '' ?>" href="profile.php">X Profile Scraper</a>
    <a class="menu-item<?= $current === 'mongo' ? ' active' : '' ?>" href="mongo.php">MongoDB Data</a>
</div>
