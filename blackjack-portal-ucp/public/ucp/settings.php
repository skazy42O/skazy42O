<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';

$acc = require_login();
$ucpTab = 'settings';
$id = (int)$acc[cfg('account.id')];
$emailCol = cfg('account.email');
$minPass = (int)cfg('security.min_password', 6);
$errors = ['pass' => [], 'email' => []];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = (string)($_POST['action'] ?? '');
    $current = (string)($_POST['current'] ?? '');
    $saltCol = cfg('account.salt');
    $verified = pass_verify($current, (string)$acc[cfg('account.password')], $saltCol ? (string)($acc[$saltCol] ?? '') : null);
    $bucket = $action === 'email' ? 'email' : 'pass';
    $rk = 'settings:' . $id;

    if (!csrf_check()) {
        $errors[$bucket][] = 'Sesija je istekla. Osveži stranicu.';
    } elseif (!rate_hit($rk, 10, 900, false)) {
        $errors[$bucket][] = 'Previše pokušaja. Sačekaj 15 minuta.';
    } elseif (!$verified) {
        rate_hit($rk, PHP_INT_MAX, 900);
        $errors[$bucket][] = 'Trenutna lozinka nije tačna.';
    } elseif ($action === 'password') {
        $new = (string)($_POST['new'] ?? '');
        $new2 = (string)($_POST['new2'] ?? '');
        if (strlen($new) < $minPass || strlen($new) > 64) {
            $errors['pass'][] = "Nova lozinka mora imati između $minPass i 64 znaka.";
        } elseif ($new !== $new2) {
            $errors['pass'][] = 'Nove lozinke se ne poklapaju.';
        } elseif ($new === $current) {
            $errors['pass'][] = 'Nova lozinka mora biti drugačija od stare.';
        } else {
            account_set_password($id, $new);
            session_regenerate_id(true);
            flash('success', 'Lozinka je promenjena. Od sada je koristiš i u igri.');
            redirect('ucp/settings.php');
        }
    } elseif ($action === 'email' && has_col($emailCol)) {
        $email = trim((string)($_POST['email'] ?? ''));
        if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 100) {
            $errors['email'][] = 'Unesi ispravnu email adresu.';
        } elseif (strcasecmp($email, (string)$acc[$emailCol]) !== 0 && account_email_taken($email)) {
            $errors['email'][] = 'Ova email adresa je već iskorišćena.';
        } else {
            account_update($id, [$emailCol => $email]);
            flash('success', 'Email adresa je sačuvana.');
            redirect('ucp/settings.php');
        }
    }
}

$pageTitle = 'Podešavanja';
$active = 'ucp';
$bodyClass = 'page-ucp';
require APP_DIR . '/views/header.php';
?>
<main class="wrap ucp">
  <?php require APP_DIR . '/views/ucp_nav.php'; ?>

  <section class="ucp-main">
    <div class="ucp-hello">
      <div>
        <span class="kicker">♣ Nalog</span>
        <h1>Podešavanja</h1>
        <p>Promene važe odmah i u igri. Ako si trenutno u igri, izađi pa uđi ponovo.</p>
      </div>
    </div>

    <div class="panel-grid">
      <form class="panel" method="post" novalidate>
        <h3><?= icon('lock') ?> Promena lozinke</h3>
        <?php foreach ($errors['pass'] as $er): ?><div class="alert alert-error"><?= e($er) ?></div><?php endforeach; ?>
        <?= csrf_field() ?>
        <input type="hidden" name="action" value="password">
        <label class="field"><span>Trenutna lozinka</span>
          <div class="input"><?= icon('lock') ?><input type="password" name="current" autocomplete="current-password" required></div></label>
        <label class="field"><span>Nova lozinka</span>
          <div class="input"><?= icon('lock') ?><input type="password" name="new" autocomplete="new-password" minlength="<?= $minPass ?>" maxlength="64" required data-strength></div></label>
        <div class="strength" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
        <label class="field"><span>Ponovi novu lozinku</span>
          <div class="input"><?= icon('lock') ?><input type="password" name="new2" autocomplete="new-password" maxlength="64" required></div></label>
        <button class="btn" type="submit">Sačuvaj lozinku</button>
      </form>

      <?php if (has_col($emailCol)): ?>
      <form class="panel" method="post" novalidate>
        <h3><?= icon('mail') ?> Email adresa</h3>
        <?php foreach ($errors['email'] as $er): ?><div class="alert alert-error"><?= e($er) ?></div><?php endforeach; ?>
        <?= csrf_field() ?>
        <input type="hidden" name="action" value="email">
        <label class="field"><span>Email</span>
          <div class="input"><?= icon('mail') ?><input type="email" name="email" value="<?= e($acc[$emailCol] ?? '') ?>" maxlength="100" required></div></label>
        <label class="field"><span>Trenutna lozinka (potvrda)</span>
          <div class="input"><?= icon('lock') ?><input type="password" name="current" autocomplete="current-password" required></div></label>
        <button class="btn" type="submit">Sačuvaj email</button>
        <p class="muted">Email služi za obaveštenja i buduću obnovu lozinke.</p>
      </form>
      <?php endif; ?>
    </div>
  </section>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
