<?php
require dirname(__DIR__) . '/app/bootstrap.php';

$orgs = db() ? orgs_all() : [];
$top = db() ? zones_top() : [];
$zt = db() ? zones_total() : ['total' => 0, 'taken' => 0];
$maxZones = $top ? max(1, $top[0]['zones']) : 1;
$legal = array_filter($orgs, fn($o) => !$o['illegal']);
$illegal = array_filter($orgs, fn($o) => $o['illegal']);

$pageTitle = 'Organizacije';
$active = 'orgs';
require APP_DIR . '/views/header.php';
?>
<main>
  <section class="page-head">
    <div class="wrap">
      <span class="kicker">♣ Grad je podeljen</span>
      <h1>Organizacije</h1>
      <p>Ko drži ulice? Rang lista organizacija po broju zauzetih zona — ažurira se direktno iz baze servera.</p>
    </div>
  </section>

  <div class="wrap">
    <?php if (!db()): ?>
      <div class="alert alert-info">Baza trenutno nije dostupna.</div>
    <?php else: ?>

    <div class="zone-summary">
      <div class="zs"><span><?= icon('map') ?> Ukupno zona</span><b><?= (int)$zt['total'] ?></b></div>
      <div class="zs"><span><?= icon('gun') ?> Zauzeto</span><b><?= (int)$zt['taken'] ?></b></div>
      <div class="zs"><span><?= icon('star') ?> Slobodno</span><b><?= max(0, $zt['total'] - $zt['taken']) ?></b></div>
      <div class="zs"><span><?= icon('org') ?> Organizacija</span><b><?= count($orgs) ?></b></div>
    </div>

    <section class="panel top-zones">
      <h3><?= icon('crown') ?> Top <?= (int)cfg('zones.top', 10) ?> — zauzete zone</h3>
      <?php if (!$top): ?>
        <p class="muted">Još nijedna zona nije zauzeta.</p>
      <?php else: ?>
      <ol class="tz-list">
        <?php foreach ($top as $i => $o): $pos = $i + 1; ?>
        <li class="tz pos-<?= $pos ?>" style="--c: <?= e($o['color']) ?>">
          <span class="tz-pos"><?= $pos <= 3 ? ['', '♠', '♥', '♦'][$pos] : $pos ?></span>
          <a class="tz-name" href="<?= url('organizacija.php?id=' . (int)$o['id']) ?>">
            <i class="sw"></i><?= e($o['name']) ?>
            <?php if ($o['type']): ?><small><?= e($o['type']) ?></small><?php endif; ?>
          </a>
          <span class="tz-bar"><i style="width: <?= round($o['zones'] / $maxZones * 100) ?>%"></i></span>
          <span class="tz-num"><b><?= (int)$o['zones'] ?></b> <?= zone_word((int)$o['zones']) ?></span>
        </li>
        <?php endforeach; ?>
      </ol>
      <?php endif; ?>
    </section>

    <?php foreach (['Ilegalne organizacije' => $illegal, 'Legalne organizacije' => $legal] as $title => $list): if (!$list) continue; ?>
    <section class="org-block">
      <h2 class="h-sec"><?= e($title) ?></h2>
      <div class="org-grid">
        <?php foreach ($list as $o): ?>
        <a class="org-card" href="<?= url('organizacija.php?id=' . $o['id']) ?>" style="--c: <?= e($o['color']) ?>">
          <div class="org-top">
            <span class="org-badge"><?= e(mb_strtoupper(mb_substr($o['name'], 0, 2))) ?></span>
            <div>
              <h3><?= e($o['name']) ?></h3>
              <?php if ($o['type']): ?><span class="tag"><?= e($o['type']) ?></span><?php endif; ?>
            </div>
          </div>
          <dl class="org-meta">
            <div><dt>Članova</dt><dd><?= (int)$o['members'] ?></dd></div>
            <div><dt>Zona</dt><dd><?= (int)$o['zones'] ?></dd></div>
            <div><dt>Lider</dt><dd><?= e($o['leader'] ?: '—') ?></dd></div>
          </dl>
        </a>
        <?php endforeach; ?>
      </div>
    </section>
    <?php endforeach; ?>

    <?php if (!$orgs): ?>
      <div class="alert alert-info">Organizacije još nisu podešene (tabela <code><?= e(cfg('orgs.table')) ?></code> ne postoji).</div>
    <?php endif; ?>
    <?php endif; ?>
  </div>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
