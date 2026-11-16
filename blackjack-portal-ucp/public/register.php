<?php
require dirname(__DIR__) . '/app/bootstrap.php';

if (is_logged_in()) {
    redirect('ucp/');
}

$errors = [];
$old = ['name' => '', 'email' => ''];
$open = (bool)cfg('security.registration_open', true);
$minPass = (int)cfg('security.min_password', 6);

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $open) {
    $old['name'] = $name = trim((string)($_POST['name'] ?? ''));
    $old['email'] = $email = trim((string)($_POST['email'] ?? ''));
    $pass = (string)($_POST['password'] ?? '');
    $pass2 = (string)($_POST['password2'] ?? '');
    $ipKey = 'register:' . client_ip();

    if (!csrf_check()) {
        $errors[] = 'Sesija je istekla. Osveži stranicu i pokušaj ponovo.';
    } elseif (!empty($_POST['website'])) {
        $errors[] = 'Registracija odbijena.'; // honeypot (botovi)
    } else {
        if (!preg_match(cfg('account.name_regex'), $name)) {
            $errors[] = 'Ime mora biti u RP formatu Ime_Prezime (npr. Marko_Petrovic), samo slova.';
        } elseif (strlen($name) > 24) {
            $errors[] = 'Ime može imati najviše 24 znaka.';
        }
        if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 100) {
            $errors[] = 'Unesi ispravnu email adresu.';
        }
        if (strlen($pass) < $minPass) {
            $errors[] = "Lozinka mora imati bar $minPass znakova.";
        } elseif (strlen($pass) > 64) {
            $errors[] = 'Lozinka može imati najviše 64 znaka.';
        } elseif ($pass !== $pass2) {
            $errors[] = 'Lozinke se ne poklapaju.';
        } elseif (strcasecmp($pass, $name) === 0) {
            $errors[] = 'Lozinka ne sme biti ista kao ime.';
        }
        if (empty($_POST['rules'])) {
            $errors[] = 'Moraš prihvatiti pravila servera.';
        }
    }

    if (!$errors) {
        if (!db()) {
            $errors[] = 'Baza trenutno nije dostupna. Pokušaj kasnije.';
        } elseif (!rate_hit($ipKey, (int)cfg('security.register_max', 3), (int)cfg('security.register_window', 3600), false)) {
            $errors[] = 'Napravio si previše naloga sa ove IP adrese. Pokušaj kasnije.';
        } else {
            try {
                if (account_find_by_name($name)) {
                    $errors[] = 'Ime ' . $name . ' je zauzeto.';
                } elseif (account_email_taken($email)) {
                    $errors[] = 'Ova email adresa je već iskorišćena.';
                } else {
                    $id = account_create($name, $email, $pass);
                    rate_hit($ipKey, PHP_INT_MAX, (int)cfg('security.register_window', 3600));
                    $acc = account_find_by_id($id);
                    if ($acc) {
                        login_user($acc);
                    }
                    flash('success', 'Nalog ' . $name . ' je napravljen! Uđi u igru istim imenom i lozinkom.');
                    redirect('ucp/');
                }
            } catch (Throwable $ex) {
                error_log('[BJ-UCP] register: ' . $ex->getMessage());
                $errors[] = cfg('site.debug') ? $ex->getMessage() : 'Došlo je do greške pri registraciji. Pokušaj ponovo.';
            }
        }
    }
}

$pageTitle = 'Registracija';
$active = 'register';
$bodyClass = 'page-auth';
require APP_DIR . '/views/header.php';
?>
<main class="auth">
  <div class="auth-card">
    <div class="auth-side">
      <img src="<?= asset('img/logo.png') ?>" alt="" width="507" height="668">
      <h2>Postani deo zajednice</h2>
      <p>Nalog koji napraviš ovde odmah važi i u igri — ista lozinka, isti karakter.</p>
      <ul class="auth-perks">
        <li><?= icon('id') ?> Ime u formatu <b>Ime_Prezime</b></li>
        <li><?= icon('cash') ?> Početni novac i paket za nove igrače</li>
        <li><?= icon('clock') ?> Happy Hours X3 do levela 10</li>
      </ul>
    </div>
    <form class="auth-form" method="post" novalidate>
      <span class="kicker">♥ Nova ruka</span>
      <h1>Registracija</h1>
      <?php if (!$open): ?>
        <div class="alert alert-info">Registracija preko sajta je trenutno zatvorena. Nalog napravi direktno u igri.</div>
      <?php endif; ?>
      <?php foreach ($errors as $er): ?><div class="alert alert-error"><?= e($er) ?></div><?php endforeach; ?>
      <?= csrf_field() ?>
      <div class="hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>

      <label class="field">
        <span>Ime_Prezime</span>
        <div class="input"><?= icon('user') ?><input type="text" name="name" value="<?= e($old['name']) ?>" placeholder="Marko_Petrovic" autocomplete="username" maxlength="24" pattern="[A-Z][a-zA-Z]{1,15}_[A-Z][a-zA-Z]{1,15}" required></div>
        <small class="hint" data-name-hint>Veliko početno slovo, donja crta između imena i prezimena.</small>
      </label>
      <label class="field">
        <span>Email</span>
        <div class="input"><?= icon('mail') ?><input type="email" name="email" value="<?= e($old['email']) ?>" placeholder="ti@primer.com" autocomplete="email" maxlength="100" required></div>
      </label>
      <div class="field-row">
        <label class="field">
          <span>Lozinka</span>
          <div class="input"><?= icon('lock') ?><input type="password" name="password" placeholder="min. <?= $minPass ?> znakova" autocomplete="new-password" minlength="<?= $minPass ?>" maxlength="64" required data-strength></div>
        </label>
        <label class="field">
          <span>Ponovi lozinku</span>
          <div class="input"><?= icon('lock') ?><input type="password" name="password2" placeholder="••••••••" autocomplete="new-password" maxlength="64" required></div>
        </label>
      </div>
      <div class="strength" aria-hidden="true"><i></i><i></i><i></i><i></i></div>

      <label class="check">
        <input type="checkbox" name="rules" value="1" required>
        <span>Pročitao sam i prihvatam pravila servera. Znam da je deljenje naloga zabranjeno.</span>
      </label>
      <button class="btn btn-lg btn-block" type="submit" <?= $open ? '' : 'disabled' ?>>Napravi nalog</button>
      <p class="auth-alt">Već imaš nalog? <a href="<?= url('login.php') ?>">Prijavi se</a></p>
    </form>
  </div>
</main>
<?php require APP_DIR . '/views/footer.php'; ?>
