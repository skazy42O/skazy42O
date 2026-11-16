<?php
/** @var array $admin */
/** @var string $admTab */
$lvl = admin_level($admin);
?>
<aside class="ucp-side adm-side">
  <div class="adm-brand">
    <span class="adm-shield"><?= icon('shield') ?></span>
    <div><b>Admin panel</b><small><?= e($admin[cfg('account.name')]) ?> · <?= e(admin_title($admin) ?? 'Admin ' . $lvl) ?></small></div>
  </div>
  <nav class="ucp-menu">
    <a href="<?= url('admin/') ?>" class="<?= $admTab === 'home' ? 'on' : '' ?>"><?= icon('home') ?> Pregled</a>
    <a href="<?= url('admin/igraci.php') ?>" class="<?= $admTab === 'players' ? 'on' : '' ?>"><?= icon('user') ?> Igrači</a>
    <a href="<?= url('admin/banovi.php') ?>" class="<?= $admTab === 'bans' ? 'on' : '' ?>"><?= icon('ban') ?> Banovi</a>
    <a href="<?= url('admin/log.php') ?>" class="<?= $admTab === 'log' ? 'on' : '' ?>"><?= icon('list') ?> Log akcija</a>
    <a href="<?= url('ucp/') ?>"><?= icon('logout') ?> Nazad na UCP</a>
  </nav>
  <div class="adm-perms">
    <span>Tvoja prava</span>
    <ul>
      <li class="<?= $lvl >= (int)cfg('admin_panel.ban_level') ? 'ok' : '' ?>">Ban / unban</li>
      <li class="<?= $lvl >= (int)cfg('admin_panel.edit_level') ? 'ok' : '' ?>">Izmena igrača</li>
      <li class="<?= $lvl >= (int)cfg('admin_panel.owner_level') ? 'ok' : '' ?>">Admin nivoi</li>
    </ul>
  </div>
</aside>
