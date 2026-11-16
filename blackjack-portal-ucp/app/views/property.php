<?php
/** @var array $props  rezultat property_of() */
/** @var bool  $propCompact */
$propCompact = $propCompact ?? false;
if (!$props): ?>
  <div class="alert alert-info">Imovina još nije podešena (tabele iz <code>config.php → property</code> ne postoje).</div>
<?php endif;
foreach ($props as $key => $grp): $p = $grp['cfg']; ?>
<section class="panel prop-group">
  <h3><?= icon($p['icon'] ?? 'home') ?> <?= e($p['label']) ?> <span class="count"><?= count($grp['items']) ?></span></h3>
  <?php if (!$grp['items']): ?>
    <p class="muted">Nema <?= e(mb_strtolower($p['label'])) ?>.</p>
  <?php else: ?>
  <div class="prop-grid <?= $key === 'vehicles' ? 'is-veh' : '' ?>">
    <?php foreach ($grp['items'] as $it): $img = vehicle_img($it['model']); ?>
    <article class="prop">
      <?php if ($key === 'vehicles'): ?>
        <div class="prop-img"><?php if ($img): ?><img src="<?= e($img) ?>" alt="" loading="lazy" width="204" height="125"><?php endif; ?></div>
        <h4><?= e($it['model'] !== null ? vehicle_name($it['model']) : ($it['title'] ?? 'Vozilo')) ?></h4>
        <span class="prop-id">ID #<?= (int)$it['id'] ?><?= $it['model'] !== null ? ' · model ' . (int)$it['model'] : '' ?></span>
      <?php else: ?>
        <div class="prop-ico"><?= icon($p['icon'] ?? 'home') ?></div>
        <h4><?= e($it['title'] !== null && $it['title'] !== '' ? $it['title'] : $p['label'] . ' #' . $it['id']) ?></h4>
        <span class="prop-id">ID #<?= (int)$it['id'] ?></span>
      <?php endif; ?>
      <?php if ($it['fields']): ?>
      <dl>
        <?php foreach ($it['fields'] as $f): ?><div><dt><?= e($f['label']) ?></dt><dd><?= e($f['value']) ?></dd></div><?php endforeach; ?>
      </dl>
      <?php endif; ?>
    </article>
    <?php endforeach; ?>
  </div>
  <?php endif; ?>
</section>
<?php endforeach;
