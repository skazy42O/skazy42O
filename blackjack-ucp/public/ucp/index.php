<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$acc = require_login();
$ucpTab = 'home';

$stats = array_values(array_filter(cfg('stats', []), fn($s) => has_col($s['col'])));
$emailCol = cfg('account.email');
$extra = [];
foreach (['registered' => 'Registrovan', 'reg_date' => 'Registrovan', 'last_login' => 'Poslednja prijava', 'lastlogin' => 'Poslednja prijava'] as $col => $label) {
    if (has_col($col) && !isset($extra[$label])) {
        $extra[$label] = fmt_value($acc[$col], ['fmt' => 'datetime']);
    }
}
$status = samp_status();

$pageTitle = 'User Control Panel';
$active = 'ucp';
$bodyClass = 'page-ucp';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/ucp_nav.php'; ?>

  <section class="ucp-main">
    <div class="ucp-hello">
      <div>
        <span class="kicker">♠ User Control Panel</span>
        <h1>Zdravo, <?= e(explode('_', (string)$acc[cfg('account.name')])[0]) ?>!</h1>
        <p>Ovde vidiš stanje svog karaktera. Podaci se čitaju direktno iz baze servera.</p>
      </div>
      <div class="ucp-server <?= $status['online'] ? 'is-on' : '' ?>">
        <span class="dot <?= $status['online'] ? 'live' : '' ?>"></span>
        <div>
          <b><?= $status['online'] ? (int)$status['players'] . ' / ' . (int)$status['max'] : 'Offline' ?></b>
          <small>igrača na serveru</small>
        </div>
        <a class="btn btn-sm" href="samp://<?= e(cfg('server.host') . ':' . (int)cfg('server.port')) ?>"><?= icon('play') ?> Igraj</a>
      </div>
    </div>

    <?php if ($stats): ?>
    <div class="ucp-stats">
      <?php foreach ($stats as $s): ?>
      <div class="ustat">
        <div class="ustat-ico"><?= icon($s['icon'] ?? 'star') ?></div>
        <div>
          <span><?= e($s['label']) ?></span>
          <b><?= e(fmt_value($acc[$s['col']], $s)) ?></b>
        </div>
      </div>
      <?php endforeach; ?>
    </div>
    <?php else: ?>
      <div class="alert alert-info">Statistika još nije podešena — kolone iz <code>config.php → stats</code> ne postoje u tabeli naloga.</div>
    <?php endif; ?>

    <div class="panel">
      <h3><?= icon('id') ?> Informacije o nalogu</h3>
      <dl class="kv">
        <div><dt>Ime</dt><dd><?= e($acc[cfg('account.name')]) ?></dd></div>
        <?php if (has_col($emailCol)): ?>
        <div><dt>Email</dt><dd><?= $acc[$emailCol] ? e($acc[$emailCol]) : '<em>nije postavljen</em>' ?></dd></div>
        <?php endif; ?>
        <?php foreach ($extra as $label => $val): ?>
        <div><dt><?= e($label) ?></dt><dd><?= e($val) ?></dd></div>
        <?php endforeach; ?>
        <div><dt>Status</dt><dd><?= e(admin_title($acc) ?? 'Igrač') ?></dd></div>
      </dl>
    </div>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
