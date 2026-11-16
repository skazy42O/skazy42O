<?php
declare(strict_types=1);

/* =================================================================
 | ORGANIZACIJE & ZONE
 * ================================================================= */

/** Sve organizacije, indeksirane po ID-u, sa brojem clanova i zona. */
function orgs_all(): array
{
    static $out = null;
    if ($out !== null) {
        return $out;
    }
    $out = [];
    $o = cfg('orgs');
    if (!db() || !table_ok($o['table'])) {
        return $out;
    }
    $t = $o['table'];
    $rows = db()->query('SELECT * FROM ' . qi($t) . ' ORDER BY ' . qi($o['id']))->fetchAll();
    foreach ($rows as $r) {
        $id = (int)$r[$o['id']];
        $out[$id] = [
            'id'      => $id,
            'name'    => (string)$r[$o['name']],
            'type'    => tcol($t, $o['type']) ? ($o['types'][(int)$r[$o['type']]] ?? (string)$r[$o['type']]) : null,
            'illegal' => tcol($t, $o['type']) ? (int)$r[$o['type']] === 1 : false,
            'leader'  => tcol($t, $o['leader']) ? (string)$r[$o['leader']] : null,
            'color'   => org_color(tcol($t, $o['color']) ? $r[$o['color']] : null, $id),
            'members' => 0,
            'zones'   => 0,
        ];
    }

    $acc = cfg('account.table');
    if (has_col($o['member_col'])) {
        $st = db()->query('SELECT ' . qi($o['member_col']) . ' AS oid, COUNT(*) AS c FROM ' . qi($acc) . ' WHERE ' . qi($o['member_col']) . ' > 0 GROUP BY ' . qi($o['member_col']));
        foreach ($st as $r) {
            if (isset($out[(int)$r['oid']])) {
                $out[(int)$r['oid']]['members'] = (int)$r['c'];
            }
        }
    }
    foreach (zones_by_owner() as $oid => $c) {
        if (isset($out[$oid])) {
            $out[$oid]['zones'] = $c;
        }
    }
    return $out;
}

/** [org_id => broj zona] */
function zones_by_owner(): array
{
    static $out = null;
    if ($out !== null) {
        return $out;
    }
    $out = [];
    $z = cfg('zones');
    if (!db() || !tcol($z['table'], $z['owner'])) {
        return $out;
    }
    $st = db()->query('SELECT ' . qi($z['owner']) . ' AS oid, COUNT(*) AS c FROM ' . qi($z['table']) . ' WHERE ' . qi($z['owner']) . ' > 0 GROUP BY ' . qi($z['owner']) . ' ORDER BY c DESC');
    foreach ($st as $r) {
        $out[(int)$r['oid']] = (int)$r['c'];
    }
    return $out;
}

function zones_total(): array
{
    $z = cfg('zones');
    if (!db() || !table_ok($z['table'])) {
        return ['total' => 0, 'taken' => 0];
    }
    $total = (int)db()->query('SELECT COUNT(*) FROM ' . qi($z['table']))->fetchColumn();
    return ['total' => $total, 'taken' => array_sum(zones_by_owner())];
}

/** Top N organizacija po broju zauzetih zona. */
function zones_top(): array
{
    $orgs = orgs_all();
    $top = [];
    foreach (zones_by_owner() as $oid => $c) {
        $top[] = $orgs[$oid] ?? ['id' => $oid, 'name' => 'Organizacija #' . $oid, 'color' => org_color(null, $oid), 'type' => null, 'illegal' => true, 'members' => 0, 'leader' => null, 'zones' => $c];
        if (count($top) >= (int)cfg('zones.top', 10)) {
            break;
        }
    }
    return $top;
}

function zone_word(int $n): string
{
    $d = $n % 10;
    $dd = $n % 100;
    return ($d >= 2 && $d <= 4 && ($dd < 12 || $dd > 14)) ? 'zone' : 'zona';
}

function org_zones(int $orgId): array
{
    $z = cfg('zones');
    if (!db() || !tcol($z['table'], $z['owner'])) {
        return [];
    }
    $st = db()->prepare('SELECT * FROM ' . qi($z['table']) . ' WHERE ' . qi($z['owner']) . ' = ? ORDER BY ' . qi($z['id']));
    $st->execute([$orgId]);
    $out = [];
    foreach ($st as $r) {
        $out[] = tcol($z['table'], $z['name']) && $r[$z['name']] !== '' ? (string)$r[$z['name']] : 'Zona #' . $r[$z['id']];
    }
    return $out;
}

function org_members(int $orgId): array
{
    $o = cfg('orgs');
    $a = cfg('account');
    if (!db() || !has_col($o['member_col'])) {
        return [];
    }
    $sel = [qi($a['name']) . ' AS name'];
    $rank = has_col($o['rank_col']);
    if ($rank) {
        $sel[] = qi($o['rank_col']) . ' AS rnk';
    }
    if (has_col($a['skin'])) {
        $sel[] = qi($a['skin']) . ' AS skin';
    }
    $sql = 'SELECT ' . implode(', ', $sel) . ' FROM ' . qi($a['table']) . ' WHERE ' . qi($o['member_col']) . ' = ? ORDER BY ' . ($rank ? qi($o['rank_col']) . ' DESC, ' : '') . qi($a['name']) . ' LIMIT 300';
    $st = db()->prepare($sql);
    $st->execute([$orgId]);
    $out = [];
    foreach ($st as $r) {
        $lvl = (int)($r['rnk'] ?? 0);
        $out[] = [
            'name' => $r['name'],
            'rank' => $lvl,
            'rank_name' => $rank ? ($o['rank_names'][$lvl] ?? 'Rank ' . $lvl) : null,
            'skin' => isset($r['skin']) ? (int)$r['skin'] : null,
        ];
    }
    return $out;
}

/** Pretvara SA-MP / hex boju u CSS boju. Bez boje -> stabilna boja po ID-u. */
function org_color($raw, int $id = 0): string
{
    $c = org_color_raw($raw, $id);
    [$r, $g, $b] = sscanf($c, '#%02x%02x%02x');
    // previse tamne boje se ne vide na tamnoj pozadini -> posvetli
    if (0.2126 * $r + 0.7152 * $g + 0.0722 * $b < 60) {
        $r = (int)($r + (255 - $r) * .45);
        $g = (int)($g + (255 - $g) * .45);
        $b = (int)($b + (255 - $b) * .45);
        return sprintf('#%02x%02x%02x', $r, $g, $b);
    }
    return $c;
}

function org_color_raw($raw, int $id): string
{
    if (is_int($raw) || (is_string($raw) && ctype_digit($raw) && strlen($raw) > 6)) {
        $hex = str_pad(dechex((int)$raw & 0xFFFFFFFF), 8, '0', STR_PAD_LEFT);
        return '#' . substr($hex, 0, 6);
    }
    if (is_string($raw)) {
        $h = preg_replace('/^(0x|#|\{)/i', '', trim($raw, '{} '));
        if (preg_match('/^[0-9a-f]{6}([0-9a-f]{2})?$/i', $h)) {
            return '#' . strtolower(substr($h, 0, 6));
        }
    }
    $pal = ['#3a8cc6', '#e0485b', '#36d399', '#f0c35a', '#a78bfa', '#f97316', '#22d3ee', '#ec4899', '#84cc16', '#94a3b8'];
    return $pal[$id % count($pal)];
}

/* =================================================================
 | BANOVI
 * ================================================================= */

function bans_enabled(): bool
{
    return db() && table_ok(cfg('bans.table'));
}

/** Lista banova sa pretragom i paginacijom. */
function bans_list(string $q, int $page): array
{
    $b = cfg('bans');
    $t = $b['table'];
    $per = max(5, (int)$b['per_page']);
    $where = '';
    $args = [];
    if ($q !== '') {
        $where = ' WHERE ' . qi($b['name']) . ' LIKE ?';
        $args[] = '%' . str_replace(['\\', '%', '_'], ['\\\\', '\%', '\_'], $q) . '%';
    }
    $cnt = db()->prepare('SELECT COUNT(*) FROM ' . qi($t) . $where);
    $cnt->execute($args);
    $total = (int)$cnt->fetchColumn();
    $pages = max(1, (int)ceil($total / $per));
    $page = min(max(1, $page), $pages);
    $order = tcol($t, $b['date']) ? qi($b['date']) : qi($b['id']);
    $st = db()->prepare('SELECT * FROM ' . qi($t) . $where . " ORDER BY $order DESC, " . qi($b['id']) . ' DESC LIMIT ' . $per . ' OFFSET ' . (($page - 1) * $per));
    $st->execute($args);
    $rows = array_map('ban_row', $st->fetchAll());
    return ['rows' => $rows, 'total' => $total, 'page' => $page, 'pages' => $pages];
}

function ban_row(array $r): array
{
    $b = cfg('bans');
    $t = $b['table'];
    $exp = tcol($t, $b['expires']) ? $r[$b['expires']] : null;
    $expTs = null;
    if ($exp !== null && $exp !== '' && $exp !== '0' && $exp !== 0 && strpos((string)$exp, '0000') !== 0) {
        $expTs = is_numeric($exp) ? (int)$exp : (strtotime((string)$exp) ?: null);
    }
    $active = $expTs === null || $expTs > time();
    if (!empty($b['active_col']) && tcol($t, $b['active_col'])) {
        $active = $active && (int)$r[$b['active_col']] === 1;
    }
    return [
        'id'      => (int)$r[$b['id']],
        'name'    => (string)$r[$b['name']],
        'admin'   => tcol($t, $b['admin']) ? (string)$r[$b['admin']] : '—',
        'reason'  => tcol($t, $b['reason']) ? (string)$r[$b['reason']] : '—',
        'date'    => tcol($t, $b['date']) ? fmt_value($r[$b['date']], ['fmt' => 'datetime']) : '—',
        'expires' => $expTs === null ? 'Trajno' : date('d.m.Y H:i', $expTs),
        'perm'    => $expTs === null,
        'active'  => $active,
        'ip'      => tcol($t, $b['ip']) ? (string)$r[$b['ip']] : null,
    ];
}

function ban_time_value(?int $ts)
{
    if (cfg('bans.date_format') === 'unix') {
        return $ts ?? 0;
    }
    return $ts === null ? null : date('Y-m-d H:i:s', $ts);
}

function ban_add(string $name, string $reason, int $days, string $admin, string $ip = ''): void
{
    $b = cfg('bans');
    $t = $b['table'];
    $data = [$b['name'] => $name];
    if (tcol($t, $b['reason'])) {
        $data[$b['reason']] = $reason;
    }
    if (tcol($t, $b['admin'])) {
        $data[$b['admin']] = $admin;
    }
    if (tcol($t, $b['date'])) {
        $data[$b['date']] = ban_time_value(time());
    }
    if (tcol($t, $b['expires'])) {
        $data[$b['expires']] = ban_time_value($days > 0 ? time() + $days * 86400 : null);
    }
    if ($ip !== '' && tcol($t, $b['ip'])) {
        $data[$b['ip']] = $ip;
    }
    if (!empty($b['active_col']) && tcol($t, $b['active_col'])) {
        $data[$b['active_col']] = 1;
    }
    $cols = implode(', ', array_map('qi', array_keys($data)));
    $ph = implode(', ', array_fill(0, count($data), '?'));
    db()->prepare('INSERT INTO ' . qi($t) . " ($cols) VALUES ($ph)")->execute(array_values($data));
}

function ban_remove(int $id): ?array
{
    $b = cfg('bans');
    $t = $b['table'];
    $st = db()->prepare('SELECT * FROM ' . qi($t) . ' WHERE ' . qi($b['id']) . ' = ?');
    $st->execute([$id]);
    $row = $st->fetch();
    if (!$row) {
        return null;
    }
    if ($b['unban'] === 'active' && !empty($b['active_col']) && tcol($t, $b['active_col'])) {
        db()->prepare('UPDATE ' . qi($t) . ' SET ' . qi($b['active_col']) . ' = 0 WHERE ' . qi($b['id']) . ' = ?')->execute([$id]);
    } else {
        db()->prepare('DELETE FROM ' . qi($t) . ' WHERE ' . qi($b['id']) . ' = ? LIMIT 1')->execute([$id]);
    }
    return ban_row($row);
}

/* =================================================================
 | IMOVINA
 * ================================================================= */

/** Imovina naloga: [kljuc => ['cfg' => ..., 'items' => [...]]] samo za postojece tabele. */
function property_of(array $acc): array
{
    $out = [];
    foreach (cfg('property', []) as $key => $p) {
        if (!db() || !tcol($p['table'], $p['owner'])) {
            continue;
        }
        $ownerVal = ($p['owner_by'] ?? 'name') === 'id' ? (int)$acc[cfg('account.id')] : (string)$acc[cfg('account.name')];
        $st = db()->prepare('SELECT * FROM ' . qi($p['table']) . ' WHERE ' . qi($p['owner']) . ' = ? ORDER BY ' . qi($p['id']) . ' LIMIT 100');
        $st->execute([$ownerVal]);
        $items = [];
        foreach ($st as $r) {
            $it = ['id' => (int)$r[$p['id']], 'title' => null, 'model' => null, 'fields' => []];
            if (!empty($p['model']) && tcol($p['table'], $p['model'])) {
                $it['model'] = (int)$r[$p['model']];
            }
            if (!empty($p['title']) && tcol($p['table'], $p['title'])) {
                $it['title'] = (string)$r[$p['title']];
            }
            foreach ($p['fields'] ?? [] as $f) {
                if (tcol($p['table'], $f['col'])) {
                    $it['fields'][] = ['label' => $f['label'], 'value' => fmt_value($r[$f['col']], $f)];
                }
            }
            $items[] = $it;
        }
        $out[$key] = ['cfg' => $p, 'items' => $items];
    }
    return $out;
}

function vehicle_name(int $model): string
{
    static $names = [
        'Landstalker','Bravura','Buffalo','Linerunner','Perennial','Sentinel','Dumper','Firetruck','Trashmaster','Stretch',
        'Manana','Infernus','Voodoo','Pony','Mule','Cheetah','Ambulance','Leviathan','Moonbeam','Esperanto',
        'Taxi','Washington','Bobcat','Mr Whoopee','BF Injection','Hunter','Premier','Enforcer','Securicar','Banshee',
        'Predator','Bus','Rhino','Barracks','Hotknife','Trailer','Previon','Coach','Cabbie','Stallion',
        'Rumpo','RC Bandit','Romero','Packer','Monster','Admiral','Squalo','Seasparrow','Pizzaboy','Tram',
        'Trailer','Turismo','Speeder','Reefer','Tropic','Flatbed','Yankee','Caddy','Solair','Berkley\'s RC Van',
        'Skimmer','PCJ-600','Faggio','Freeway','RC Baron','RC Raider','Glendale','Oceanic','Sanchez','Sparrow',
        'Patriot','Quad','Coastguard','Dinghy','Hermes','Sabre','Rustler','ZR-350','Walton','Regina',
        'Comet','BMX','Burrito','Camper','Marquis','Baggage','Dozer','Maverick','News Chopper','Rancher',
        'FBI Rancher','Virgo','Greenwood','Jetmax','Hotring','Sandking','Blista Compact','Police Maverick','Boxville','Benson',
        'Mesa','RC Goblin','Hotring Racer A','Hotring Racer B','Bloodring Banger','Rancher','Super GT','Elegant','Journey','Bike',
        'Mountain Bike','Beagle','Cropduster','Stunt','Tanker','Roadtrain','Nebula','Majestic','Buccaneer','Shamal',
        'Hydra','FCR-900','NRG-500','HPV1000','Cement Truck','Tow Truck','Fortune','Cadrona','FBI Truck','Willard',
        'Forklift','Tractor','Combine','Feltzer','Remington','Slamvan','Blade','Freight','Streak','Vortex',
        'Vincent','Bullet','Clover','Sadler','Firetruck LA','Hustler','Intruder','Primo','Cargobob','Tampa',
        'Sunrise','Merit','Utility','Nevada','Yosemite','Windsor','Monster A','Monster B','Uranus','Jester',
        'Sultan','Stratum','Elegy','Raindance','RC Tiger','Flash','Tahoma','Savanna','Bandito','Freight Flat',
        'Streak Carriage','Kart','Mower','Duneride','Sweeper','Broadway','Tornado','AT-400','DFT-30','Huntley',
        'Stafford','BF-400','Newsvan','Tug','Trailer','Emperor','Wayfarer','Euros','Hotdog','Club',
        'Freight Carriage','Trailer','Andromada','Dodo','RC Cam','Launch','Police Car (LSPD)','Police Car (SFPD)','Police Car (LVPD)','Police Ranger',
        'Picador','S.W.A.T.','Alpha','Phoenix','Glendale','Sadler','Luggage Trailer','Luggage Trailer','Stair Trailer','Boxville',
        'Farm Plow','Utility Trailer',
    ];
    return $names[$model - 400] ?? 'Vozilo #' . $model;
}

function vehicle_img(?int $model): ?string
{
    if ($model === null || $model < 400 || $model > 611) {
        return null;
    }
    return asset('img/vehicles/' . $model . '.jpg');
}

/* =================================================================
 | ADMIN
 * ================================================================= */

function admin_level(array $acc): int
{
    $col = cfg('account.admin');
    return has_col($col) ? (int)$acc[$col] : 0;
}

function is_staff(array $acc): bool
{
    return admin_level($acc) >= (int)cfg('admin_panel.min_level', 3);
}

/** Za admin stranice: vraca nalog admina ili 403. */
function require_admin(int $minLevel = 0): array
{
    $acc = require_login();
    $need = max($minLevel, (int)cfg('admin_panel.min_level', 3));
    if (admin_level($acc) < $need) {
        http_response_code(403);
        $pageTitle = 'Zabranjeno';
        require APP_DIR . '/views/header.php';
        echo '<main class="wrap" style="padding:80px 0;text-align:center"><h1 class="h-big">403</h1><p class="muted">Nemaš pristup ovom delu panela.</p><a class="btn" href="' . e(url('ucp/')) . '">Nazad na UCP</a></main>';
        require APP_DIR . '/views/footer.php';
        exit;
    }
    return $acc;
}

function admin_log_ensure(): void
{
    static $done = false;
    if ($done || !db()) {
        return;
    }
    db()->exec('CREATE TABLE IF NOT EXISTS `ucp_admin_log` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `admin_id` INT NOT NULL,
        `admin_name` VARCHAR(32) NOT NULL,
        `action` VARCHAR(32) NOT NULL,
        `target` VARCHAR(32) DEFAULT NULL,
        `details` TEXT,
        `ip` VARCHAR(45) DEFAULT NULL,
        `created_at` DATETIME NOT NULL,
        PRIMARY KEY (`id`), KEY `admin_id` (`admin_id`), KEY `created_at` (`created_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4');
    $done = true;
}

function admin_log(array $admin, string $action, ?string $target, string $details): void
{
    try {
        admin_log_ensure();
        db()->prepare('INSERT INTO `ucp_admin_log` (admin_id, admin_name, action, target, details, ip, created_at) VALUES (?,?,?,?,?,?,?)')
            ->execute([(int)$admin[cfg('account.id')], (string)$admin[cfg('account.name')], $action, $target, $details, client_ip(), date('Y-m-d H:i:s')]);
    } catch (Throwable $ex) {
        error_log('[BJ-UCP] admin_log: ' . $ex->getMessage());
    }
}

function admin_log_recent(int $limit = 50, int $offset = 0, string $q = ''): array
{
    try {
        admin_log_ensure();
        $where = '';
        $args = [];
        if ($q !== '') {
            $where = ' WHERE admin_name LIKE ? OR target LIKE ? OR action LIKE ?';
            $like = '%' . str_replace(['\\', '%', '_'], ['\\\\', '\%', '\_'], $q) . '%';
            $args = [$like, $like, $like];
        }
        $st = db()->prepare('SELECT * FROM `ucp_admin_log`' . $where . ' ORDER BY id DESC LIMIT ' . (int)$limit . ' OFFSET ' . (int)$offset);
        $st->execute($args);
        return $st->fetchAll();
    } catch (Throwable $ex) {
        return [];
    }
}

/** Pretraga igraca po imenu (admin). */
function players_search(string $q, int $limit = 50): array
{
    $a = cfg('account');
    $sel = [qi($a['id']) . ' AS id', qi($a['name']) . ' AS name'];
    foreach (['level' => 'level', 'admin' => $a['admin'], 'skin' => $a['skin']] as $alias => $col) {
        if (has_col($col)) {
            $sel[] = qi($col) . ' AS ' . $alias;
        }
    }
    $sql = 'SELECT ' . implode(', ', $sel) . ' FROM ' . qi($a['table']);
    $args = [];
    if ($q !== '') {
        if (ctype_digit($q)) {
            $sql .= ' WHERE ' . qi($a['id']) . ' = ? OR ' . qi($a['name']) . ' LIKE ?';
            $args = [(int)$q, '%' . $q . '%'];
        } else {
            $sql .= ' WHERE ' . qi($a['name']) . ' LIKE ?';
            $args[] = '%' . str_replace(['\\', '%', '_'], ['\\\\', '\%', '\_'], $q) . '%';
        }
    }
    $sql .= ' ORDER BY ' . qi($a['id']) . ' DESC LIMIT ' . (int)$limit;
    $st = db()->prepare($sql);
    $st->execute($args);
    return $st->fetchAll();
}

/** Pagination linkovi. */
function pager(int $page, int $pages, array $query): string
{
    if ($pages <= 1) {
        return '';
    }
    $h = '<nav class="pager">';
    $mk = function (int $p, string $label, bool $on = false) use ($query) {
        $query['p'] = $p;
        return '<a class="' . ($on ? 'on' : '') . '" href="?' . e(http_build_query($query)) . '">' . $label . '</a>';
    };
    if ($page > 1) {
        $h .= $mk($page - 1, '‹');
    }
    for ($i = max(1, $page - 2); $i <= min($pages, $page + 2); $i++) {
        $h .= $mk($i, (string)$i, $i === $page);
    }
    if ($page < $pages) {
        $h .= $mk($page + 1, '›');
    }
    return $h . '</nav>';
}
