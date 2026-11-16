<?php
require dirname(__DIR__) . '/app/bootstrap.php';

$id = (int)($_GET['id'] ?? 0);
$orgs = db() ? orgs_all() : [];
$org = $orgs[$id] ?? null;
if (!$org) {
    http_response_code(404);
    flash('error', 'Organizacija nije pronađena.');
    redirect('organizacije.php');
}
$members = org_members($id);
$zones = org_zones($id);
$leader = $org['leader'] ?: ($members[0]['name'] ?? null);
$rankPos = array_search($id, array_keys(zones_by_owner()), true);

$pageTitle = $org['name'];
$active = 'orgs';
require APP_DIR . '/views/header.php';
?>
<main>
  <section class="page-head org-head" style="--c: <?= e($org['color']) ?>">
    <div class="wrap org-head-in">
      <span class="org-badge big"><?= e(mb_strtoupper(mb_substr($org['name'], 0, 2))) ?></span>
      <div>
        <a class="back" href="<?= url('organizacije.php') ?>">‹ Sve organizacije</a>
        <h1><?= e($org['name']) ?></h1>
        <div class="ucp-tags left">
          <?php if ($org['type']): ?><span class="tag"><?= e($org['type']) ?></span><?php endif; ?>
          <?php if ($rankPos !== false): ?><span class="tag tag-admin">#<?= $rankPos + 1 ?> po zonama</span><?php endif; ?>
        </div>
      </div>
    </div>
  </section>

  <div class="wrap">
    <div class="zone-summary">
      <div class="zs"><span><?= icon('org') ?> Članova</span><b><?= count($members) ?></b></div>
      <div class="zs"><span><?= icon('map') ?> Zona</span><b><?= count($zones) ?></b></div>
      <div class="zs wide"><span><?= icon('crown') ?> Lider</span><b><?= e($leader ?: '—') ?></b></div>
    </div>

    <div class="org-detail">
      <section class="panel">
        <h3><?= icon('org') ?> Članovi</h3>
        <?php if (!$members): ?>
          <p class="muted">Organizacija trenutno nema članova.</p>
        <?php else: ?>
        <ul class="member-list">
          <?php foreach ($members as $m): ?>
          <li>
            <?php if ($m['skin'] !== null): ?><img src="<?= e(skin_url($m['skin'])) ?>" alt="" loading="lazy" width="40" height="73"><?php endif; ?>
            <span class="mn"><?= e($m['name']) ?></span>
            <?php if ($m['rank_name']): ?><span class="tag rank-<?= (int)$m['rank'] ?>"><?= e($m['rank_name']) ?></span><?php endif; ?>
          </li>
          <?php endforeach; ?>
        </ul>
        <?php endif; ?>
      </section>

      <section class="panel">
        <h3><?= icon('map') ?> Zauzete zone</h3>
        <?php if (!$zones): ?>
          <p class="muted">Organizacija ne drži nijednu zonu.</p>
        <?php else: ?>
        <ul class="zone-chips">
          <?php foreach ($zones as $z): ?><li><i class="sw"></i><?= e($z) ?></li><?php endforeach; ?>
        </ul>
        <?php endif; ?>
      </section>
    </div>
  </div>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
