<?php
require dirname(__DIR__) . '/app/bootstrap.php';

if (is_logged_in()) {
    redirect('ucp/');
}

$errors = [];
$name = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim((string)($_POST['name'] ?? ''));
    $pass = (string)($_POST['password'] ?? '');
    $ipKey = 'login-ip:' . client_ip();
    $nameKey = 'login-name:' . strtolower($name);
    $max = (int)cfg('security.login_max', 5);
    $win = (int)cfg('security.login_window', 900);

    if (!csrf_check()) {
        $errors[] = 'Sesija je istekla. Osveži stranicu i pokušaj ponovo.';
    } elseif ($name === '' || $pass === '') {
        $errors[] = 'Unesi ime i lozinku.';
    } elseif (!rate_hit($ipKey, $max * 3, $win, false) || !rate_hit($nameKey, $max, $win, false)) {
        $errors[] = 'Previše neuspešnih pokušaja. Sačekaj ' . (int)ceil($win / 60) . ' minuta pa pokušaj ponovo.';
    } elseif (!db()) {
        $errors[] = 'Baza trenutno nije dostupna. Pokušaj kasnije.';
    } else {
        try {
            $acc = account_find_by_name($name);
            $saltCol = cfg('account.salt');
            $ok = $acc && pass_verify($pass, (string)$acc[cfg('account.password')], $saltCol ? (string)($acc[$saltCol] ?? '') : null);
            if (!$acc) {
                // izjednaci vreme odgovora
                password_verify($pass, '$2y$12$.qKVYkDwV.V4NIGi4kmkiOQb4VS6Y8HAtbWWHhyK9LR0ZcNSKdsFe');
            }
            if ($ok) {
                rate_clear($nameKey);
                login_user($acc);
                flash('success', 'Dobrodošao nazad, ' . $acc[cfg('account.name')] . '!');
                redirect('ucp/');
            }
            rate_hit($ipKey, PHP_INT_MAX, $win);
            rate_hit($nameKey, PHP_INT_MAX, $win);
            $errors[] = 'Pogrešno ime ili lozinka.';
        } catch (Throwable $ex) {
            error_log('[BJ-UCP] login: ' . $ex->getMessage());
            $errors[] = cfg('site.debug') ? $ex->getMessage() : 'Došlo je do greške. Pokušaj ponovo.';
        }
    }
}

$pageTitle = 'Prijava';
$active = 'login';
$bodyClass = 'page-auth';
require APP_DIR . '/views/header.php';
?>
<main class="auth">
  <div class="auth-card">
    <div class="auth-side">
      <img src="<?= asset('img/logo.png') ?>" alt="" width="507" height="668">
      <h2>User Control Panel</h2>
      <p>Prijavi se istim imenom i lozinkom koje koristiš u igri.</p>
      <ul class="auth-perks">
        <li><?= icon('star') ?> Statistika tvog karaktera</li>
        <li><?= icon('bank') ?> Novac, banka i zlato</li>
        <li><?= icon('lock') ?> Promena lozinke i emaila</li>
      </ul>
    </div>
    <form class="auth-form" method="post" novalidate>
      <span class="kicker">♠ Dobrodošao nazad</span>
      <h1>Prijava</h1>
      <?php foreach ($errors as $er): ?><div class="alert alert-error"><?= e($er) ?></div><?php endforeach; ?>
      <?= csrf_field() ?>
      <label class="field">
        <span>Ime_Prezime</span>
        <div class="input"><?= icon('user') ?><input type="text" name="name" value="<?= e($name) ?>" placeholder="npr. Marko_Petrovic" autocomplete="username" maxlength="24" required autofocus></div>
      </label>
      <label class="field">
        <span>Lozinka</span>
        <div class="input"><?= icon('lock') ?><input type="password" name="password" placeholder="••••••••" autocomplete="current-password" required><button type="button" class="eye" aria-label="Prikaži lozinku">👁</button></div>
      </label>
      <button class="btn btn-lg btn-block" type="submit">Prijavi se</button>
      <p class="auth-alt">Nemaš nalog? <a href="<?= url('register.php') ?>">Registruj se</a></p>
      <p class="auth-note">Zaboravio si lozinku? Javi se staffu na <a href="<?= e(cfg('site.discord')) ?>" target="_blank" rel="noopener">Discordu</a>.</p>
    </form>
  </div>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
