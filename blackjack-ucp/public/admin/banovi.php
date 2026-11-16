<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$admin = require_admin();
$admTab = 'bans';
$a = cfg('account');
$myLvl = admin_level($admin);
$canBan = $myLvl >= (int)cfg('admin_panel.ban_level') && bans_enabled();
$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = (string)($_POST['action'] ?? '');
    if (!csrf_check()) {
        $errors[] = 'Sesija je istekla. Osveži stranicu.';
    } elseif (!$canBan) {
        $errors[] = 'Nemaš dozvolu za banovanje.';
    } elseif ($action === 'unban') {
        $row = ban_remove((int)($_POST['id'] ?? 0));
        if ($row) {
            admin_log($admin, 'unban', $row['name'], 'Skinut ban: ' . $row['reason']);
            flash('success', 'Ban za ' . $row['name'] . ' je skinut.');
        } else {
            flash('error', 'Ban nije pronađen.');
        }
        redirect('admin/banovi.php');
    } elseif ($action === 'ban') {
        $name = trim((string)($_POST['name'] ?? ''));
        $reason = trim(mb_substr((string)($_POST['reason'] ?? ''), 0, 120));
        $days = (int)($_POST['days'] ?? 0);
        $ip = trim((string)($_POST['ip'] ?? ''));
        $t = $name !== '' ? account_find_by_name($name) : null;
        if (!$t) {
            $errors[] = 'Nalog „' . $name . '“ ne postoji.';
        } elseif ((int)$t[$a['id']] === (int)$admin[$a['id']]) {
            $errors[] = 'Ne možeš banovati sebe.';
        } elseif (admin_level($t) >= $myLvl && $myLvl < (int)cfg('admin_panel.owner_level')) {
            $errors[] = 'Ne možeš banovati admina istog ili većeg nivoa.';
        } elseif ($reason === '') {
            $errors[] = 'Unesi razlog bana.';
        } elseif ($days < 0 || $days > 3650) {
            $errors[] = 'Neispravno trajanje.';
        } elseif ($ip !== '' && !filter_var($ip, FILTER_VALIDATE_IP)) {
            $errors[] = 'Neispravna IP adresa.';
        } else {
            ban_add((string)$t[$a['name']], $reason, $days, (string)$admin[$a['name']], $ip);
            admin_log($admin, 'ban', (string)$t[$a['name']], $reason . ' (' . ($days ? $days . ' dana' : 'trajno') . ')' . ($ip ? ' IP ' . $ip : ''));
            flash('success', $t[$a['name']] . ' je banovan.');
            redirect('admin/banovi.php');
        }
    }
}

$q = trim(mb_substr((string)($_GET['q'] ?? ''), 0, 24));
$data = bans_enabled() ? bans_list($q, (int)($_GET['p'] ?? 1)) : null;

$pageTitle = 'Banovi · Admin';
$active = 'admin';
$bodyClass = 'page-ucp page-admin';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/admin_nav.php'; ?>
  <section class="ucp-main">
    <div class="ucp-hello adm-hello"><div><span class="kicker">♠ Admin</span><h1>Banovi</h1><p>Ban upisan ovde važi u igri od sledećeg ulaska igrača.</p></div></div>
    <?php foreach ($errors as $er): ?><div class="alert alert-error"><?= e($er) ?></div><?php endforeach; ?>

    <?php if (!$data): ?>
      <div class="alert alert-info">Tabela banova nije podešena (<code><?= e(cfg('bans.table')) ?></code>).</div>
    <?php else: ?>

    <?php if ($canBan): ?>
    <form class="panel panel-danger" method="post" data-confirm="Potvrdi ban?">
      <h3><?= icon('ban') ?> Novi ban</h3>
      <?= csrf_field() ?><input type="hidden" name="action" value="ban">
      <div class="ban-form">
        <label class="field"><span>Igrač</span><div class="input"><input type="text" name="name" maxlength="24" placeholder="Ime_Prezime" value="<?= e($_POST['name'] ?? '') ?>" required></div></label>
        <label class="field"><span>Razlog</span><div class="input"><input type="text" name="reason" maxlength="120" placeholder="Razlog" value="<?= e($_POST['reason'] ?? '') ?>" required></div></label>
        <label class="field"><span>Trajanje</span><div class="input"><select name="days">
          <option value="1">1 dan</option><option value="3">3 dana</option><option value="7">7 dana</option><option value="14">14 dana</option><option value="30">30 dana</option><option value="0">Trajno</option>
        </select></div></label>
        <?php if (tcol(cfg('bans.table'), cfg('bans.ip'))): ?>
        <label class="field"><span>IP (opciono)</span><div class="input"><input type="text" name="ip" maxlength="45" placeholder="0.0.0.0"></div></label>
        <?php endif; ?>
        <button class="btn btn-danger" type="submit">Banuj</button>
      </div>
    </form>
    <?php endif; ?>

    <form class="toolbar" method="get">
      <div class="input"><?= icon('search') ?><input type="search" name="q" value="<?= e($q) ?>" placeholder="Pretraži po imenu…" maxlength="24"></div>
      <button class="btn" type="submit">Traži</button>
      <span class="muted"><?= (int)$data['total'] ?> banova</span>
    </form>
    <div class="table-wrap">
      <table class="tbl">
        <thead><tr><th>Igrač</th><th>Razlog</th><th>Admin</th><th>Datum</th><th>Ističe</th><th>IP</th><th>Status</th><th></th></tr></thead>
        <tbody>
        <?php if (!$data['rows']): ?><tr><td colspan="8" class="empty">Nema banova.</td></tr><?php endif; ?>
        <?php foreach ($data['rows'] as $b): ?>
          <tr>
            <td data-l="Igrač"><b><?= e($b['name']) ?></b></td>
            <td data-l="Razlog"><?= e($b['reason']) ?></td>
            <td data-l="Admin"><?= e($b['admin']) ?></td>
            <td data-l="Datum" class="nowrap"><?= e($b['date']) ?></td>
            <td data-l="Ističe" class="nowrap"><?= $b['perm'] ? '<span class="perm">Trajno</span>' : e($b['expires']) ?></td>
            <td data-l="IP"><code><?= e($b['ip'] ?: '—') ?></code></td>
            <td data-l="Status"><span class="pill <?= $b['active'] ? 'pill-red' : 'pill-muted' ?>"><?= $b['active'] ? 'Aktivan' : 'Istekao' ?></span></td>
            <td class="r">
              <?php if ($canBan): ?>
              <form method="post" data-confirm="Skinuti ban za <?= e($b['name']) ?>?">
                <?= csrf_field() ?><input type="hidden" name="action" value="unban"><input type="hidden" name="id" value="<?= (int)$b['id'] ?>">
                <button class="btn btn-sm btn-ghost" type="submit">Unban</button>
              </form>
              <?php endif; ?>
            </td>
          </tr>
        <?php endforeach; ?>
        </tbody>
      </table>
    </div>
    <?= pager($data['page'], $data['pages'], ['q' => $q]) ?>
    <?php endif; ?>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
