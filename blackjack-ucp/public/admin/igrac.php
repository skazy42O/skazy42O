<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$admin = require_admin();
$admTab = 'players';
$a = cfg('account');
$ap = cfg('admin_panel');
$id = (int)($_GET['id'] ?? 0);
$target = $id ? account_find_by_id($id) : null;
if (!$target) {
    flash('error', 'Igrač nije pronađen.');
    redirect('admin/igraci.php');
}

$myLvl = admin_level($admin);
$tLvl = admin_level($target);
$isSelf = (int)$admin[$a['id']] === $id;
$isOwner = $myLvl >= (int)$ap['owner_level'];
// Ne mozes dirati nekog sa istim ili vecim admin nivoom (osim vlasnik)
$outranked = !$isSelf && $tLvl >= $myLvl && !$isOwner;
$canEdit = $myLvl >= (int)$ap['edit_level'] && !$outranked;
$canBan = $myLvl >= (int)$ap['ban_level'] && !$isSelf && !$outranked && bans_enabled();
$canAdmin = $isOwner && !$isSelf && has_col($a['admin']);
$editable = array_values(array_filter($ap['editable'] ?? [], fn($f) => has_col($f['col'])));
$tName = (string)$target[$a['name']];
$online = !empty($ap['online_col']) && has_col($ap['online_col']) && (int)$target[$ap['online_col']] === 1;
$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = (string)($_POST['action'] ?? '');
    if (!csrf_check()) {
        $errors[] = 'Sesija je istekla. Osveži stranicu.';
    } elseif ($action === 'edit' && $canEdit) {
        $changes = [];
        $log = [];
        foreach ($editable as $f) {
            if (!isset($_POST['f'][$f['col']])) {
                continue;
            }
            $raw = trim((string)$_POST['f'][$f['col']]);
            if (!preg_match('/^-?\d+$/', $raw)) {
                $errors[] = $f['label'] . ': mora biti ceo broj.';
                continue;
            }
            $v = (int)$raw;
            if ($v < $f['min'] || $v > $f['max']) {
                $errors[] = $f['label'] . ": dozvoljeno {$f['min']} – {$f['max']}.";
                continue;
            }
            if ((string)$target[$f['col']] !== (string)$v) {
                $changes[$f['col']] = $v;
                $log[] = $f['label'] . ': ' . $target[$f['col']] . ' → ' . $v;
            }
        }
        if (!$errors && $changes) {
            account_update($id, $changes);
            admin_log($admin, 'edit', $tName, implode('; ', $log));
            flash('success', 'Sačuvano: ' . implode(', ', $log));
            redirect('admin/igrac.php?id=' . $id);
        } elseif (!$errors) {
            flash('info', 'Nema promena.');
            redirect('admin/igrac.php?id=' . $id);
        }
    } elseif ($action === 'admin' && $canAdmin) {
        $new = (int)($_POST['level'] ?? 0);
        if ($new < 0 || $new > (int)$ap['owner_level']) {
            $errors[] = 'Neispravan admin nivo.';
        } elseif ($new !== $tLvl) {
            account_update($id, [$a['admin'] => $new]);
            $lv = cfg('admin_levels', []);
            admin_log($admin, 'admin', $tName, 'Admin nivo: ' . ($lv[$tLvl] ?? $tLvl) . ' → ' . ($lv[$new] ?? $new));
            flash('success', 'Admin nivo za ' . $tName . ' je promenjen.');
            redirect('admin/igrac.php?id=' . $id);
        }
    } elseif ($action === 'ban' && $canBan) {
        $reason = trim(mb_substr((string)($_POST['reason'] ?? ''), 0, 120));
        $days = (int)($_POST['days'] ?? 0);
        if ($reason === '') {
            $errors[] = 'Unesi razlog bana.';
        } elseif ($days < 0 || $days > 3650) {
            $errors[] = 'Trajanje mora biti 0 (trajno) do 3650 dana.';
        } else {
            ban_add($tName, $reason, $days, (string)$admin[$a['name']]);
            admin_log($admin, 'ban', $tName, $reason . ' (' . ($days ? $days . ' dana' : 'trajno') . ')');
            flash('success', $tName . ' je banovan.');
            redirect('admin/igrac.php?id=' . $id);
        }
    } else {
        $errors[] = 'Nemaš dozvolu za ovu akciju.';
    }
}

$stats = array_values(array_filter(cfg('stats', []), fn($s) => has_col($s['col'])));
$props = property_of($target);
$bans = bans_enabled() ? array_filter(bans_list($tName, 1)['rows'], fn($b) => strcasecmp($b['name'], $tName) === 0) : [];
$skin = has_col($a['skin']) ? (int)$target[$a['skin']] : 0;

$pageTitle = $tName . ' · Admin';
$active = 'admin';
$bodyClass = 'page-ucp page-admin';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/admin_nav.php'; ?>
  <section class="ucp-main">
    <div class="ucp-hello adm-hello player-head">
      <div class="ph-skin"><div class="hc-chip"></div><img src="<?= e(skin_url($skin)) ?>" alt="" width="165" height="300"></div>
      <div class="ph-info">
        <a class="back" href="<?= url('admin/igraci.php') ?>">‹ Igrači</a>
        <h1><?= e($tName) ?></h1>
        <div class="ucp-tags left">
          <span class="tag">ID #<?= $id ?></span>
          <?php if ($t = admin_title($target)): ?><span class="tag tag-admin"><?= e($t) ?></span><?php endif; ?>
          <?php if (array_filter($bans, fn($b) => $b['active'])): ?><span class="tag tag-ban">Banovan</span><?php endif; ?>
          <?php if (has_col($a['email']) && $target[$a['email']]): ?><span class="tag"><?= e($target[$a['email']]) ?></span><?php endif; ?>
        </div>
      </div>
    </div>

    <?php foreach ($errors as $er): ?><div class="alert alert-error"><?= e($er) ?></div><?php endforeach; ?>
    <?php if ($online): ?><div class="alert alert-info">Igrač je trenutno u igri — gamemode može pregaziti izmene kad izađe. Najbolje menjaj dok je offline.</div><?php endif; ?>
    <?php if ($outranked): ?><div class="alert alert-info">Ovaj nalog ima isti ili veći admin nivo od tvog — možeš samo da gledaš.</div><?php endif; ?>

    <?php if ($stats): ?>
    <div class="ucp-stats">
      <?php foreach ($stats as $s): ?>
      <div class="ustat"><div class="ustat-ico"><?= icon($s['icon'] ?? 'star') ?></div><div><span><?= e($s['label']) ?></span><b><?= e(fmt_value($target[$s['col']], $s)) ?></b></div></div>
      <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <div class="panel-grid">
      <?php if ($canEdit && $editable): ?>
      <form class="panel" method="post">
        <h3><?= icon('edit') ?> Izmena naloga</h3>
        <?= csrf_field() ?><input type="hidden" name="action" value="edit">
        <div class="edit-grid">
          <?php foreach ($editable as $f): ?>
          <label class="field"><span><?= e($f['label']) ?></span>
            <div class="input"><input type="number" name="f[<?= e($f['col']) ?>]" value="<?= e($target[$f['col']]) ?>" min="<?= (int)$f['min'] ?>" max="<?= (int)$f['max'] ?>" step="1"></div></label>
          <?php endforeach; ?>
        </div>
        <button class="btn" type="submit">Sačuvaj izmene</button>
      </form>
      <?php endif; ?>

      <div class="stack">
        <?php if ($canBan): ?>
        <form class="panel panel-danger" method="post" data-confirm="Sigurno banovati <?= e($tName) ?>?">
          <h3><?= icon('ban') ?> Banuj igrača</h3>
          <?= csrf_field() ?><input type="hidden" name="action" value="ban">
          <label class="field"><span>Razlog</span><div class="input"><input type="text" name="reason" maxlength="120" placeholder="npr. Cheat (aimbot)" required></div></label>
          <label class="field"><span>Trajanje</span>
            <div class="input"><select name="days">
              <option value="1">1 dan</option><option value="3">3 dana</option><option value="7">7 dana</option>
              <option value="14">14 dana</option><option value="30">30 dana</option><option value="0">Trajno</option>
            </select></div></label>
          <button class="btn btn-danger" type="submit">Banuj</button>
        </form>
        <?php endif; ?>

        <?php if ($canAdmin): ?>
        <form class="panel" method="post" data-confirm="Promeniti admin nivo za <?= e($tName) ?>?">
          <h3><?= icon('shield') ?> Admin nivo</h3>
          <?= csrf_field() ?><input type="hidden" name="action" value="admin">
          <div class="input"><select name="level">
            <?php for ($i = 0; $i <= (int)$ap['owner_level']; $i++): ?>
              <option value="<?= $i ?>" <?= $i === $tLvl ? 'selected' : '' ?>><?= $i ?> — <?= e(cfg('admin_levels')[$i] ?? 'Igrač') ?></option>
            <?php endfor; ?>
          </select></div>
          <button class="btn btn-ghost" type="submit">Postavi nivo</button>
        </form>
        <?php endif; ?>

        <?php if ($bans): ?>
        <section class="panel">
          <h3><?= icon('ban') ?> Istorija banova</h3>
          <ul class="mini-list">
            <?php foreach ($bans as $b): ?>
            <li><div><b><?= e($b['reason']) ?></b><span><?= e($b['date']) ?> · <?= e($b['admin']) ?> · <?= $b['perm'] ? 'trajno' : 'do ' . e($b['expires']) ?></span></div>
              <span class="pill <?= $b['active'] ? 'pill-red' : 'pill-muted' ?>"><?= $b['active'] ? 'Aktivan' : 'Istekao' ?></span></li>
            <?php endforeach; ?>
          </ul>
        </section>
        <?php endif; ?>
      </div>
    </div>

    <h2 class="h-sec">Imovina</h2>
    <?php require APP_DIR . '/views/property.php'; ?>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
