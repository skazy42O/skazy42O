<?php
require dirname(__DIR__) . '/app/bootstrap.php';

$q = trim(mb_substr((string)($_GET['q'] ?? ''), 0, 24));
$page = (int)($_GET['p'] ?? 1);
$data = bans_enabled() ? bans_list($q, $page) : null;

$pageTitle = 'Ban lista';
$active = 'bans';
require APP_DIR . '/views/header.php';
?>
<main>
  <section class="page-head">
    <div class="wrap">
      <span class="kicker">♠ Fer igra</span>
      <h1>Ban lista</h1>
      <p>Javni spisak banovanih igrača. Misliš da je ban nepravedan? Podnesi žalbu upravi na Discordu.</p>
    </div>
  </section>

  <div class="wrap">
    <?php if (!$data): ?>
      <div class="alert alert-info">Ban lista trenutno nije dostupna.</div>
    <?php else: ?>
    <form class="toolbar" method="get">
      <div class="input"><?= icon('search') ?><input type="search" name="q" value="<?= e($q) ?>" placeholder="Pretraži po imenu…" maxlength="24"></div>
      <button class="btn" type="submit">Traži</button>
      <span class="muted"><?= number_format($data['total'], 0, ',', '.') ?> <?= $q !== '' ? 'rezultata' : 'banova ukupno' ?></span>
    </form>

    <div class="table-wrap">
      <table class="tbl">
        <thead><tr><th>Igrač</th><th>Razlog</th><th>Admin</th><th>Datum</th><th>Ističe</th><th>Status</th></tr></thead>
        <tbody>
        <?php if (!$data['rows']): ?>
          <tr><td colspan="6" class="empty">Nema banova<?= $q !== '' ? ' za „' . e($q) . '“' : '' ?>.</td></tr>
        <?php endif; ?>
        <?php foreach ($data['rows'] as $b): ?>
          <tr>
            <td data-l="Igrač"><b><?= e($b['name']) ?></b></td>
            <td data-l="Razlog"><?= e($b['reason']) ?></td>
            <td data-l="Admin"><?= e($b['admin']) ?></td>
            <td data-l="Datum"><?= e($b['date']) ?></td>
            <td data-l="Ističe"><?= $b['perm'] ? '<span class="perm">Trajno</span>' : e($b['expires']) ?></td>
            <td data-l="Status"><span class="pill <?= $b['active'] ? 'pill-red' : 'pill-muted' ?>"><?= $b['active'] ? 'Aktivan' : 'Istekao' ?></span></td>
          </tr>
        <?php endforeach; ?>
        </tbody>
      </table>
    </div>
    <?= pager($data['page'], $data['pages'], ['q' => $q]) ?>
    <?php endif; ?>
  </div>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
