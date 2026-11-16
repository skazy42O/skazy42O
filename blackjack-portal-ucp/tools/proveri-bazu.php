<?php
/**
 * Provera da li config.php odgovara bazi.
 * Ispisuje samo imena tabela/kolona i broj redova - BEZ podataka igraca,
 * pa izlaz mozes bezbedno da posaljes.
 *
 *   php tools/proveri-bazu.php
 */
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';
require dirname(__DIR__) . '/app/bootstrap.php';

$ok = 0;
$bad = 0;
function line(bool $good, string $msg): void
{
    global $ok, $bad;
    $good ? $ok++ : $bad++;
    echo ($good ? '  [OK]   ' : '  [FALI] ') . $msg . PHP_EOL;
}

echo PHP_EOL . '=== BLACK JACK UCP - provera baze ===' . PHP_EOL;
if (!db()) {
    echo '  [GRESKA] Nema konekcije: ' . ($GLOBALS['DB_ERROR'] ?? '?') . PHP_EOL;
    echo '  Proveri db podatke u app/config.php' . PHP_EOL;
    exit(1);
}
echo '  Povezan na bazu "' . cfg('db.name') . '"' . PHP_EOL;

$check = function (string $title, ?string $table, array $cols) {
    echo PHP_EOL . "--- $title (tabela: " . ($table ?? '-') . ') ---' . PHP_EOL;
    if (!table_ok($table)) {
        line(false, "tabela '$table' ne postoji");
        return;
    }
    $n = (int)db()->query('SELECT COUNT(*) FROM ' . qi($table))->fetchColumn();
    line(true, "tabela '$table' ($n redova)");
    foreach ($cols as $label => $col) {
        if ($col === null || $col === '') {
            continue;
        }
        line(tcol($table, $col), "$label -> kolona '$col'");
    }
};

$a = cfg('account');
$check('Nalozi', $a['table'], ['id' => $a['id'], 'ime' => $a['name'], 'lozinka' => $a['password'], 'salt' => $a['salt'], 'email' => $a['email'], 'skin' => $a['skin'], 'admin' => $a['admin'], 'online' => cfg('admin_panel.online_col'), 'org' => cfg('orgs.member_col'), 'rank u org' => cfg('orgs.rank_col')]);

// format hash-a (bez otkrivanja lozinki)
if (table_ok($a['table']) && tcol($a['table'], $a['password'])) {
    $h = (string)db()->query('SELECT ' . qi($a['password']) . ' FROM ' . qi($a['table']) . ' WHERE ' . qi($a['password']) . " <> '' LIMIT 1")->fetchColumn();
    $guess = 'nepoznato';
    if (preg_match('/^\$2[aby]\$/', $h)) {
        $guess = 'bcrypt';
    } elseif (preg_match('/^[0-9a-f]{128}$/i', $h)) {
        $guess = 'whirlpool';
    } elseif (preg_match('/^[0-9a-f]{64}$/i', $h)) {
        $guess = 'sha256_salt (ili sha256 bez salta)';
    } elseif (preg_match('/^[0-9a-f]{32}$/i', $h)) {
        $guess = 'md5';
    }
    echo '  Hash lozinke izgleda kao: ' . $guess . ' (duzina ' . strlen($h) . ') | u configu: ' . $a['hash'] . PHP_EOL;
}
$st = [];
foreach (cfg('stats', []) as $s) {
    $st[$s['label']] = $s['col'];
}
$check('UCP statistika (kolone u tabeli naloga)', $a['table'], $st);
$ed = [];
foreach (cfg('admin_panel.editable', []) as $f) {
    $ed[$f['label']] = $f['col'];
}
$check('Admin izmena (kolone u tabeli naloga)', $a['table'], $ed);

$o = cfg('orgs');
$check('Organizacije', $o['table'], ['id' => $o['id'], 'ime' => $o['name'], 'tip' => $o['type'], 'lider' => $o['leader'], 'boja' => $o['color']]);
$z = cfg('zones');
$check('Zone', $z['table'], ['id' => $z['id'], 'ime' => $z['name'], 'vlasnik' => $z['owner']]);
$b = cfg('bans');
$check('Banovi', $b['table'], ['id' => $b['id'], 'ime' => $b['name'], 'admin' => $b['admin'], 'razlog' => $b['reason'], 'datum' => $b['date'], 'istice' => $b['expires'], 'ip' => $b['ip']]);
foreach (cfg('property', []) as $key => $p) {
    $cols = ['id' => $p['id'], 'vlasnik' => $p['owner'], 'naziv' => $p['title'] ?? null, 'model' => $p['model'] ?? null];
    foreach ($p['fields'] ?? [] as $f) {
        $cols[$f['label']] = $f['col'];
    }
    $check('Imovina: ' . $p['label'], $p['table'], $cols);
}

echo PHP_EOL . '--- Sve tabele u bazi ---' . PHP_EOL;
foreach (db()->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN) as $t) {
    $cols = implode(', ', array_keys(table_columns($t)));
    echo "  $t: $cols" . PHP_EOL;
}

echo PHP_EOL . "Rezultat: $ok OK, $bad fali." . PHP_EOL;
echo 'Posalji ovaj ispis (nema podataka igraca) pa uskladimo config.' . PHP_EOL . PHP_EOL;
