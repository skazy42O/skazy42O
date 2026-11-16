<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$acc = require_login();
$ucpTab = 'property';
$props = property_of($acc);

$pageTitle = 'Imovina';
$active = 'ucp';
$bodyClass = 'page-ucp';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/ucp_nav.php'; ?>
  <section class="ucp-main">
    <div class="ucp-hello">
      <div>
        <span class="kicker">♦ Tvoje vlasništvo</span>
        <h1>Imovina</h1>
        <p>Kuće, firme i vozila koja su upisana na tvoj nalog.</p>
      </div>
      <div class="prop-sum">
        <?php foreach ($props as $grp): ?>
          <div><b><?= count($grp['items']) ?></b><small><?= e($grp['cfg']['label']) ?></small></div>
        <?php endforeach; ?>
      </div>
    </div>
    <?php require APP_DIR . '/views/property.php'; ?>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
