<?php
/** @var array $acc */
/** @var string $ucpTab */
$skinCol = cfg('account.skin');
$skin = has_col($skinCol) ? (int)$acc[$skinCol] : 0;
$adm = admin_title($acc);
?>
<aside class="ucp-side">
  <div class="ucp-profile">
    <div class="ucp-avatar">
      <div class="hc-chip"></div>
      <img src="<?= e(skin_url($skin)) ?>" alt="Skin <?= $skin ?>" width="165" height="300" onerror="this.style.visibility='hidden'">
    </div>
    <h2><?= e($acc[cfg('account.name')]) ?></h2>
    <div class="ucp-tags">
      <?php if ($adm): ?><span class="tag tag-admin"><?= e($adm) ?></span><?php endif; ?>
      <span class="tag">ID #<?= (int)$acc[cfg('account.id')] ?></span>
      <?php if (has_col($skinCol)): ?><span class="tag">Skin <?= $skin ?></span><?php endif; ?>
    </div>
  </div>
  <nav class="ucp-menu">
    <a href="<?= url('ucp/') ?>" class="<?= $ucpTab === 'home' ? 'on' : '' ?>"><?= icon('home') ?> Pregled</a>
    <a href="<?= url('ucp/imovina.php') ?>" class="<?= $ucpTab === 'property' ? 'on' : '' ?>"><?= icon('car') ?> Imovina</a>
    <a href="<?= url('ucp/settings.php') ?>" class="<?= $ucpTab === 'settings' ? 'on' : '' ?>"><?= icon('cog') ?> Podešavanja</a>
    <?php if (is_staff($acc)): ?><a href="<?= url('admin/') ?>"><?= icon('shield') ?> Admin panel</a><?php endif; ?>
    <a href="<?= url('') ?>"><?= icon('star') ?> Portal</a>
    <a href="<?= url('logout.php') ?>"><?= icon('logout') ?> Odjava</a>
  </nav>
</aside>
