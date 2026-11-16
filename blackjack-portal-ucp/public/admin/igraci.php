<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$admin = require_admin();
$admTab = 'players';
$q = trim(mb_substr((string)($_GET['q'] ?? ''), 0, 24));
$rows = players_search($q, 100);
$levels = cfg('admin_levels', []);

$pageTitle = 'Igrači';
$active = 'admin';
$bodyClass = 'page-ucp page-admin';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/admin_nav.php'; ?>
  <section class="ucp-main">
    <div class="ucp-hello adm-hello"><div><span class="kicker">♣ Admin</span><h1>Igrači</h1><p>Pretraga po imenu ili ID-u. Prikazuje se najviše 100 rezultata.</p></div></div>
    <form class="toolbar" method="get">
      <div class="input"><?= icon('search') ?><input type="search" name="q" value="<?= e($q) ?>" placeholder="Ime_Prezime ili ID" maxlength="24" autofocus></div>
      <button class="btn" type="submit">Traži</button>
      <span class="muted"><?= count($rows) ?> rezultata</span>
    </form>
    <div class="table-wrap">
      <table class="tbl">
        <thead><tr><th>ID</th><th>Igrač</th><th>Level</th><th>Status</th><th></th></tr></thead>
        <tbody>
        <?php if (!$rows): ?><tr><td colspan="5" class="empty">Nema rezultata.</td></tr><?php endif; ?>
        <?php foreach ($rows as $p): $al = (int)($p['admin'] ?? 0); ?>
          <tr>
            <td data-l="ID">#<?= (int)$p['id'] ?></td>
            <td data-l="Igrač" class="pl-cell"><?php if (isset($p['skin'])): ?><img src="<?= e(skin_url((int)$p['skin'])) ?>" alt="" width="22" height="40" loading="lazy"><?php endif; ?><b><?= e($p['name']) ?></b></td>
            <td data-l="Level"><?= isset($p['level']) ? (int)$p['level'] : '—' ?></td>
            <td data-l="Status"><?php if ($al > 0): ?><span class="pill pill-gold"><?= e($levels[$al] ?? 'Admin ' . $al) ?></span><?php else: ?><span class="pill pill-muted">Igrač</span><?php endif; ?></td>
            <td class="r"><a class="btn btn-sm btn-ghost" href="<?= url('admin/igrac.php?id=' . (int)$p['id']) ?>"><?= icon('edit') ?> Otvori</a></td>
          </tr>
        <?php endforeach; ?>
        </tbody>
      </table>
    </div>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
