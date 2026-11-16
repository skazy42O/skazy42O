<?php
declare(strict_types=1);

/* ---------------------------------------------------------------
 | Hashovanje - mora odgovarati gamemode-u
 * ------------------------------------------------------------- */
function pass_hash(string $plain, ?string &$salt = null): string
{
    switch (cfg('account.hash')) {
        case 'whirlpool':
            return strtoupper(hash('whirlpool', $plain));
        case 'sha256_salt':
            if ($salt === null || $salt === '') {
                $salt = bin2hex(random_bytes(8));
            }
            return strtoupper(hash('sha256', $plain . $salt));
        case 'md5':
            return md5($plain);
        case 'bcrypt':
        default:
            return password_hash($plain, PASSWORD_BCRYPT, ['cost' => (int)cfg('account.bcrypt_cost', 12)]);
    }
}

function pass_verify(string $plain, string $hash, ?string $salt = null): bool
{
    switch (cfg('account.hash')) {
        case 'whirlpool':
            return hash_equals(strtoupper($hash), strtoupper(hash('whirlpool', $plain)));
        case 'sha256_salt':
            return hash_equals(strtoupper($hash), strtoupper(hash('sha256', $plain . (string)$salt)));
        case 'md5':
            return hash_equals(strtolower($hash), md5($plain));
        case 'bcrypt':
        default:
            // samp-bcrypt zna da koristi $2a$ prefiks - PHP ga razume
            return password_verify($plain, $hash);
    }
}

/* ---------------------------------------------------------------
 | Nalozi
 * ------------------------------------------------------------- */
function account_find_by_name(string $name): ?array
{
    $a = cfg('account');
    $st = db()->prepare('SELECT * FROM ' . qi($a['table']) . ' WHERE ' . qi($a['name']) . ' = ? LIMIT 1');
    $st->execute([$name]);
    return $st->fetch() ?: null;
}

function account_find_by_id(int $id): ?array
{
    $a = cfg('account');
    $st = db()->prepare('SELECT * FROM ' . qi($a['table']) . ' WHERE ' . qi($a['id']) . ' = ? LIMIT 1');
    $st->execute([$id]);
    return $st->fetch() ?: null;
}

function account_email_taken(string $email): bool
{
    $a = cfg('account');
    if (!has_col($a['email'] ?? null)) {
        return false;
    }
    $st = db()->prepare('SELECT 1 FROM ' . qi($a['table']) . ' WHERE ' . qi($a['email']) . ' = ? LIMIT 1');
    $st->execute([$email]);
    return (bool)$st->fetchColumn();
}

function account_create(string $name, string $email, string $plain): int
{
    $a = cfg('account');
    $salt = null;
    $hash = pass_hash($plain, $salt);

    $data = [$a['name'] => $name, $a['password'] => $hash];
    if (!empty($a['salt']) && $salt !== null) {
        $data[$a['salt']] = $salt;
    }
    if (has_col($a['email'] ?? null)) {
        $data[$a['email']] = $email;
    }
    foreach (($a['register_defaults'] ?? []) as $col => $val) {
        if (!has_col($col) || array_key_exists($col, $data)) {
            continue;
        }
        if ($val === '{NOW}') {
            $val = date('Y-m-d H:i:s');
        } elseif ($val === '{UNIX}') {
            $val = time();
        } elseif ($val === '{IP}') {
            $val = client_ip();
        }
        $data[$col] = $val;
    }

    $cols = implode(', ', array_map('qi', array_keys($data)));
    $ph = implode(', ', array_fill(0, count($data), '?'));
    $st = db()->prepare('INSERT INTO ' . qi($a['table']) . " ($cols) VALUES ($ph)");
    $st->execute(array_values($data));
    @unlink(STORAGE_DIR . '/cache/registered.json');
    return (int)db()->lastInsertId();
}

function account_update(int $id, array $data): void
{
    $a = cfg('account');
    $set = implode(', ', array_map(fn($c) => qi($c) . ' = ?', array_keys($data)));
    $st = db()->prepare('UPDATE ' . qi($a['table']) . " SET $set WHERE " . qi($a['id']) . ' = ? LIMIT 1');
    $st->execute([...array_values($data), $id]);
}

function account_set_password(int $id, string $plain): void
{
    $a = cfg('account');
    $salt = null;
    $data = [$a['password'] => pass_hash($plain, $salt)];
    if (!empty($a['salt']) && $salt !== null) {
        $data[$a['salt']] = $salt;
    }
    account_update($id, $data);
}

/* ---------------------------------------------------------------
 | Sesija korisnika
 * ------------------------------------------------------------- */
function login_user(array $acc): void
{
    session_regenerate_id(true);
    $_SESSION['uid'] = (int)$acc[cfg('account.id')];
    $_SESSION['uname'] = (string)$acc[cfg('account.name')];
    $_SESSION['login_at'] = time();
    $_SESSION['staff'] = is_staff($acc);
}

function logout_user(): void
{
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 3600, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();
}

function is_logged_in(): bool
{
    return !empty($_SESSION['uid']);
}

/** Za UCP stranice: vraca trenutni nalog ili preusmerava na login. */
function require_login(): array
{
    if (!is_logged_in()) {
        flash('info', 'Prijavi se da bi pristupio User Control Panelu.');
        redirect('login.php');
    }
    if (!db()) {
        http_response_code(503);
        exit('Baza trenutno nije dostupna. Pokusaj kasnije.');
    }
    $acc = account_find_by_id((int)$_SESSION['uid']);
    if (!$acc) {
        logout_user();
        redirect('login.php');
    }
    $_SESSION['staff'] = is_staff($acc);
    return $acc;
}

function admin_title(array $acc): ?string
{
    $col = cfg('account.admin');
    if (!has_col($col)) {
        return null;
    }
    $lvl = (int)$acc[$col];
    return cfg('admin_levels')[$lvl] ?? ($lvl > 0 ? 'Admin ' . $lvl : null);
}
