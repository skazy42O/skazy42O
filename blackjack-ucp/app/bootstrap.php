<?php
declare(strict_types=1);

define('APP_DIR', __DIR__);
define('STORAGE_DIR', APP_DIR . '/storage');

$cfgFile = APP_DIR . '/config.php';
if (!is_file($cfgFile)) {
    $cfgFile = APP_DIR . '/config.sample.php';
}
$GLOBALS['CFG'] = require $cfgFile;

if (cfg('site.debug')) {
    ini_set('display_errors', '1');
    error_reporting(E_ALL);
} else {
    ini_set('display_errors', '0');
}

date_default_timezone_set('Europe/Belgrade');

require APP_DIR . '/db.php';
require APP_DIR . '/auth.php';
require APP_DIR . '/samp_query.php';

/* ---------------------------------------------------------------
 | Sesija
 * ------------------------------------------------------------- */
$secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
session_name('BJUCP');
session_set_cookie_params([
    'lifetime' => 0,
    'path'     => cfg('site.base_url', '/'),
    'secure'   => $secure,
    'httponly' => true,
    'samesite' => 'Lax',
]);
session_start();

header('X-Frame-Options: SAMEORIGIN');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: strict-origin-when-cross-origin');

/* ---------------------------------------------------------------
 | Helperi
 * ------------------------------------------------------------- */
function cfg(string $path, $default = null)
{
    $v = $GLOBALS['CFG'];
    foreach (explode('.', $path) as $k) {
        if (!is_array($v) || !array_key_exists($k, $v)) {
            return $default;
        }
        $v = $v[$k];
    }
    return $v;
}

function e($s): string
{
    return htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function url(string $path = ''): string
{
    return rtrim(cfg('site.base_url', '/'), '/') . '/' . ltrim($path, '/');
}

function asset(string $path): string
{
    $file = dirname(APP_DIR) . '/public/assets/' . ltrim($path, '/');
    $v = is_file($file) ? filemtime($file) : 1;
    return url('assets/' . ltrim($path, '/')) . '?v=' . $v;
}

function redirect(string $path): void
{
    header('Location: ' . url($path));
    exit;
}

function client_ip(): string
{
    return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
}

function flash(string $type, string $msg): void
{
    $_SESSION['flash'][] = ['type' => $type, 'msg' => $msg];
}

function take_flashes(): array
{
    $f = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $f;
}

/* CSRF */
function csrf_token(): string
{
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}

function csrf_field(): string
{
    return '<input type="hidden" name="_csrf" value="' . e(csrf_token()) . '">';
}

function csrf_check(): bool
{
    $t = $_POST['_csrf'] ?? '';
    return is_string($t) && hash_equals(csrf_token(), $t);
}

/* Rate limit (fajl, radi i na Windowsu bez dodatnih tabela) */
function rate_hit(string $key, int $max, int $window, bool $record = true): bool
{
    $file = STORAGE_DIR . '/ratelimit/' . sha1($key) . '.json';
    $now = time();
    $hits = [];
    if (is_file($file)) {
        $hits = json_decode((string)@file_get_contents($file), true) ?: [];
    }
    $hits = array_values(array_filter($hits, fn($t) => $t > $now - $window));
    if (count($hits) >= $max) {
        return false;
    }
    if ($record) {
        $hits[] = $now;
        @file_put_contents($file, json_encode($hits), LOCK_EX);
    }
    return true;
}

function rate_clear(string $key): void
{
    @unlink(STORAGE_DIR . '/ratelimit/' . sha1($key) . '.json');
}

/* Formatiranje */
function fmt_value($v, array $stat): string
{
    if ($v === null) {
        return '—';
    }
    switch ($stat['fmt'] ?? 'text') {
        case 'int':
            return number_format((int)$v, 0, ',', '.');
        case 'money':
            return number_format((int)$v, 0, ',', '.') . ' $';
        case 'gold':
            return number_format((int)$v, 0, ',', '.') . ' G';
        case 'hours':
            return number_format((int)$v, 0, ',', '.') . ' h';
        case 'bool':
            return $v ? 'Da' : 'Ne';
        case 'datetime':
            $ts = is_numeric($v) ? (int)$v : strtotime((string)$v);
            return $ts ? date('d.m.Y H:i', $ts) : '—';
        case 'map':
            return (string)($stat['map'][(int)$v] ?? $v);
        default:
            return (string)$v;
    }
}

function skin_url(?int $skin): string
{
    $skin = max(0, min(311, (int)$skin));
    return asset('img/skins/' . $skin . '.png');
}

function icon(string $name): string
{
    static $i = [
        'star'  => '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
        'cash'  => '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/><path d="M6 9v6M18 9v6"/>',
        'bank'  => '<path d="M3 9.5L12 4l9 5.5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>',
        'gold'  => '<path d="M3 18l3-7h5l3 7zM10 18l3-7h5l3 7zM7 11l2.5-5h5L17 11"/>',
        'clock' => '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        'up'    => '<path d="M4 17l6-6 4 4 6-7M14 8h6v6"/>',
        'job'   => '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 12h18"/>',
        'org'   => '<circle cx="9" cy="8" r="3.2"/><circle cx="17" cy="9.5" r="2.4"/><path d="M3 19c.6-3.4 3-5 6-5s5.4 1.6 6 5M15 14.3c2.8-.4 5 1 5.8 4"/>',
        'vip'   => '<path d="M3 8l4.5 4L12 5l4.5 7L21 8l-2 11H5z"/>',
        'warn'  => '<path d="M12 3l10 18H2zM12 10v4.5M12 17.5v.5"/>',
        'user'  => '<circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4.4 4-7 8-7s7.2 2.6 8 7"/>',
        'lock'  => '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 018 0v3"/>',
        'mail'  => '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6l8.5 7 8.5-7"/>',
        'logout'=> '<path d="M15 4h4a1 1 0 011 1v14a1 1 0 01-1 1h-4M10 17l5-5-5-5M15 12H3"/>',
        'home'  => '<path d="M3 11l9-7 9 7M5 9.5V20h14V9.5"/>',
        'cog'   => '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
        'copy'  => '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 00-1-1H5a1 1 0 00-1 1v10a1 1 0 001 1h3"/>',
        'play'  => '<path d="M7 4.5v15l12-7.5z"/>',
        'shield'=> '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/>',
        'car'   => '<path d="M4 16v-4l2-5h12l2 5v4M3 16h18v3h-3v-1H6v1H3zM7 13h.01M17 13h.01"/>',
        'gun'   => '<path d="M3 8h17l1 3h-6l-1 2h-3l-1 5H6l1-5H3z"/>',
        'chat'  => '<path d="M4 5h16v11H9l-5 4z"/>',
        'cal'   => '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
        'id'    => '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.5 16c.6-1.6 1.9-2.4 3.5-2.4s2.9.8 3.5 2.4M15 10h3.5M15 13.5h3.5"/>',
    ];
    $p = $i[$name] ?? $i['star'];
    return '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' . $p . '</svg>';
}
