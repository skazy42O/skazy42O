<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$admin = require_admin();
$admTab = 'home';
$a = cfg('account');
$status = samp_status();
$staffCount = has_col($a['admin']) ? (int)db()->query('SELECT COUNT(*) FROM ' . qi($a['table']) . ' WHERE ' . qi($a['admin']) . ' > 0')->fetchColumn() : 0;
$activeBans = 0;
if (bans_enabled()) {
    $b = cfg('bans');
    $activeBans = (int)db()->query('SELECT COUNT(*) FROM ' . qi($b['table']))->fetchColumn();
}
$newest = players_search('', 6);
$logRows = admin_log_recent(10);

$pageTitle = 'Admin panel';
$active = 'admin';
$bodyClass = 'page-ucp page-admin';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/admin_nav.php'; ?>
  <section class="ucp-main">
    <div class="ucp-hello adm-hello">
      <div>
        <span class="kicker">♠ High Command</span>
        <h1>Admin panel</h1>
        <p>Sve akcije u panelu se beleže u log sa imenom admina i IP adresom.</p>
      </div>
    </div>

    <div class="ucp-stats">
      <div class="ustat"><div class="ustat-ico"><?= icon('user') ?></div><div><span>Online</span><b><?= $status['online'] ? (int)$status['players'] . ' / ' . (int)$status['max'] : 'Offline' ?></b></div></div>
      <div class="ustat"><div class="ustat-ico"><?= icon('id') ?></div><div><span>Naloga</span><b><?= number_format((int)stat_registered(), 0, ',', '.') ?></b></div></div>
      <div class="ustat"><div class="ustat-ico"><?= icon('shield') ?></div><div><span>Staff</span><b><?= $staffCount ?></b></div></div>
      <div class="ustat"><div class="ustat-ico"><?= icon('ban') ?></div><div><span>Banova</span><b><?= $activeBans ?></b></div></div>
    </div>

    <div class="panel-grid">
      <section class="panel">
        <h3><?= icon('id') ?> Najnoviji nalozi</h3>
        <ul class="mini-list">
          <?php foreach ($newest as $p): ?>
          <li><a href="<?= url('admin/igrac.php?id=' . (int)$p['id']) ?>"><b><?= e($p['name']) ?></b><span>#<?= (int)$p['id'] ?><?= isset($p['level']) ? ' · lvl ' . (int)$p['level'] : '' ?></span></a></li>
          <?php endforeach; ?>
        </ul>
      </section>
      <section class="panel">
        <h3><?= icon('search') ?> Brza pretraga</h3>
        <form class="toolbar" method="get" action="<?= url('admin/igraci.php') ?>">
          <div class="input"><?= icon('user') ?><input type="search" name="q" placeholder="Ime ili ID igrača" maxlength="24"></div>
          <button class="btn" type="submit">Traži</button>
        </form>
        <form class="toolbar" method="get" action="<?= url('admin/banovi.php') ?>">
          <div class="input"><?= icon('ban') ?><input type="search" name="q" placeholder="Pretraži banove" maxlength="24"></div>
          <button class="btn btn-ghost" type="submit">Banovi</button>
        </form>
      </section>
    </div>

    <section class="panel">
      <h3><?= icon('list') ?> Poslednje akcije</h3>
      <?php require APP_DIR . '/views/admin_log_table.php'; ?>
    </section>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
