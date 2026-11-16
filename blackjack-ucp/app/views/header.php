<?php
/** @var string $pageTitle */
/** @var string $active */
$pageTitle = $pageTitle ?? cfg('site.name');
$active = $active ?? '';
$bodyClass = $bodyClass ?? '';
?><!doctype html>
<html lang="sr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= e($pageTitle) ?> · <?= e(cfg('site.short')) ?></title>
<meta name="description" content="<?= e(cfg('site.name')) ?> - SA-MP RolePlay server. Registracija, User Control Panel, statistika naloga.">
<meta name="theme-color" content="#0a1622">
<link rel="icon" type="image/png" href="<?= asset('img/favicon.png') ?>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&family=UnifrakturMaguntia&display=swap" rel="stylesheet">
<link rel="stylesheet" href="<?= asset('css/style.css') ?>">
</head>
<body class="<?= e($bodyClass) ?>">
<div class="bg-suits" aria-hidden="true"></div>

<header class="nav" id="top">
  <div class="wrap nav-in">
    <a class="brand" href="<?= url('') ?>">
      <img src="<?= asset('img/logo-sm.png') ?>" alt="Black Jack logo" width="38" height="50">
      <span class="brand-txt"><b>BLACK</b>JACK<small>RolePlay</small></span>
    </a>
    <button class="nav-toggle" aria-label="Meni" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="nav-links">
      <a href="<?= url('') ?>#server" class="<?= $active === 'home' ? 'on' : '' ?>">Server</a>
      <a href="<?= url('') ?>#high-command">High Command</a>
      <a href="<?= url('') ?>#galerija">Galerija</a>
      <a href="<?= e(cfg('site.discord')) ?>" target="_blank" rel="noopener">Discord</a>
      <?php if (is_logged_in()): ?>
        <a class="btn btn-sm btn-ghost <?= $active === 'ucp' ? 'on' : '' ?>" href="<?= url('ucp/') ?>"><?= icon('user') ?> <?= e($_SESSION['uname']) ?></a>
        <a class="btn btn-sm" href="<?= url('logout.php') ?>"><?= icon('logout') ?> Odjava</a>
      <?php else: ?>
        <a class="btn btn-sm btn-ghost <?= $active === 'login' ? 'on' : '' ?>" href="<?= url('login.php') ?>">Prijava</a>
        <a class="btn btn-sm" href="<?= url('register.php') ?>">Registracija</a>
      <?php endif; ?>
    </nav>
  </div>
</header>

<?php $flashes = take_flashes(); if ($flashes): ?>
<div class="wrap flashes">
  <?php foreach ($flashes as $f): ?>
    <div class="alert alert-<?= e($f['type']) ?>"><?= e($f['msg']) ?></div>
  <?php endforeach; ?>
</div>
<?php endif; ?>
