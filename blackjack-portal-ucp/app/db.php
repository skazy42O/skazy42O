<?php
declare(strict_types=1);

/**
 * PDO konekcija (lazy). Vraca null ako baza nije dostupna.
 */
function db(): ?PDO
{
    static $pdo = false;
    if ($pdo !== false) {
        return $pdo;
    }
    $c = cfg('db');
    $dsn = sprintf('mysql:host=%s;port=%d;dbname=%s;charset=%s', $c['host'], (int)$c['port'], $c['name'], $c['charset'] ?? 'utf8mb4');
    try {
        $pdo = new PDO($dsn, $c['user'], $c['pass'], [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
            PDO::ATTR_TIMEOUT            => 3,
        ]);
    } catch (PDOException $ex) {
        error_log('[BJ-UCP] DB konekcija nije uspela: ' . $ex->getMessage());
        $GLOBALS['DB_ERROR'] = $ex->getMessage();
        $pdo = null;
    }
    return $pdo;
}

/** Bezbedno citiranje imena kolone/tabele iz konfiguracije. */
function qi(string $ident): string
{
    if (!preg_match('/^[A-Za-z0-9_]+$/', $ident)) {
        throw new InvalidArgumentException('Neispravno ime kolone/tabele: ' . $ident);
    }
    return '`' . $ident . '`';
}

/** Kolone bilo koje tabele (kesirano po zahtevu). Prazan niz = tabela ne postoji. */
function table_columns(?string $table): array
{
    static $cache = [];
    if ($table === null || $table === '') {
        return [];
    }
    if (isset($cache[$table])) {
        return $cache[$table];
    }
    $cols = [];
    $pdo = db();
    if ($pdo) {
        try {
            foreach ($pdo->query('SHOW COLUMNS FROM ' . qi($table)) as $r) {
                $cols[$r['Field']] = true;
            }
        } catch (PDOException $ex) {
            // tabela ne postoji - modul se samo sakriva
        }
    }
    return $cache[$table] = $cols;
}

function table_ok(?string $table): bool
{
    return table_columns($table) !== [];
}

function tcol(?string $table, ?string $col): bool
{
    return $col !== null && $col !== '' && isset(table_columns($table)[$col]);
}

/** Postojece kolone tabele naloga, da UCP ne puca ako neke kolone nema. */
function account_columns(): array
{
    return table_columns(cfg('account.table'));
}

function has_col(?string $col): bool
{
    return $col !== null && isset(account_columns()[$col]);
}

/** Broj registrovanih naloga (kes 5 min). */
function stat_registered(): ?int
{
    $cache = STORAGE_DIR . '/cache/registered.json';
    if (is_file($cache) && filemtime($cache) > time() - 300) {
        return (int)file_get_contents($cache);
    }
    $pdo = db();
    if (!$pdo) {
        return null;
    }
    try {
        $n = (int)$pdo->query('SELECT COUNT(*) FROM ' . qi(cfg('account.table')))->fetchColumn();
        @file_put_contents($cache, (string)$n, LOCK_EX);
        return $n;
    } catch (PDOException $ex) {
        error_log('[BJ-UCP] ' . $ex->getMessage());
        return null;
    }
}
