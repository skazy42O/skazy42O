<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$admin = require_admin();
$admTab = 'log';
$q = trim(mb_substr((string)($_GET['q'] ?? ''), 0, 32));
$page = max(1, (int)($_GET['p'] ?? 1));
$per = 50;
$logRows = admin_log_recent($per + 1, ($page - 1) * $per, $q);
$hasMore = count($logRows) > $per;
$logRows = array_slice($logRows, 0, $per);

$pageTitle = 'Log · Admin';
$active = 'admin';
$bodyClass = 'page-ucp page-admin';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/admin_nav.php'; ?>
  <section class="ucp-main">
    <div class="ucp-hello adm-hello"><div><span class="kicker">♣ Admin</span><h1>Log akcija</h1><p>Svaka izmena, ban i unban iz web panela.</p></div></div>
    <form class="toolbar" method="get">
      <div class="input"><?= icon('search') ?><input type="search" name="q" value="<?= e($q) ?>" placeholder="Admin, igrač ili akcija" maxlength="32"></div>
      <button class="btn" type="submit">Traži</button>
    </form>
    <?php require APP_DIR . '/views/admin_log_table.php'; ?>
    <nav class="pager">
      <?php if ($page > 1): ?><a href="?<?= e(http_build_query(['q' => $q, 'p' => $page - 1])) ?>">‹ Novije</a><?php endif; ?>
      <?php if ($hasMore): ?><a href="?<?= e(http_build_query(['q' => $q, 'p' => $page + 1])) ?>">Starije ›</a><?php endif; ?>
    </nav>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
