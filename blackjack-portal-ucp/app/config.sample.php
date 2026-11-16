<?php
/**
 * BLACK JACK RolePlay - Portal & UCP konfiguracija
 *
 * Kopiraj ovaj fajl u "config.php" (u istom folderu) i popuni podatke.
 * config.php se NE komituje na git (lozinke od baze).
 */
return [

    /* ---------------------------------------------------------------
     | Osnovno
     * ------------------------------------------------------------- */
    'site' => [
        'name'     => 'BLACK JACK RolePlay',
        'short'    => 'BLACK JACK',
        'tagline'  => 'Online Gaming Community',
        // URL putanja do "public" foldera. Ako je sajt na rootu domena: '/'
        // Ako je u podfolderu (npr. http://ip/blackjack/): '/blackjack/'
        'base_url' => '/',
        'discord'  => 'https://discord.gg/blackjack',
        'website'  => 'www.blackjack-rpg.com',
        'debug'    => false,   // true samo dok testiras - prikazuje SQL greske
    ],

    /* ---------------------------------------------------------------
     | SA-MP server (za live online / IP box)
     * ------------------------------------------------------------- */
    'server' => [
        'host'      => '127.0.0.1', // IP ili domen servera
        'port'      => 7777,
        'record'    => 600,         // rekord igraca (prikaz na portalu)
        'cache_sec' => 30,          // koliko cesto se server query-uje
    ],

    /* ---------------------------------------------------------------
     | MySQL baza (ista baza koju koristi gamemode)
     * ------------------------------------------------------------- */
    'db' => [
        'host'    => '127.0.0.1',
        'port'    => 3306,
        'name'    => 'blackjack',
        'user'    => 'root',
        'pass'    => '',
        'charset' => 'utf8mb4',
    ],

    /* ---------------------------------------------------------------
     | Tabela naloga - mapiranje kolona
     | Kad posaljes SQL dump, ovde samo uskladimo imena kolona.
     * ------------------------------------------------------------- */
    'account' => [
        'table'    => 'users',
        'id'       => 'id',
        'name'     => 'name',
        'password' => 'password',
        'salt'     => null,        // ime kolone za salt (samo za sha256_salt), inace null
        'email'    => 'email',     // null ako nema email kolone
        'skin'     => 'skin',      // null ako nema
        'admin'    => 'admin',     // null ako nema

        /*
         | Nacin hashovanja lozinke - MORA biti isti kao u gamemode-u:
         |   bcrypt      -> samp-bcrypt plugin ($2y$ / $2a$)
         |   whirlpool   -> Whirlpool plugin (128 hex znakova)
         |   sha256_salt -> SHA256_PassHash(lozinka, salt)
         |   md5         -> stari serveri (ne preporucuje se)
         */
        'hash'        => 'bcrypt',
        'bcrypt_cost' => 12,

        // Format RP imena (Ime_Prezime)
        'name_regex' => '/^[A-Z][a-zA-Z]{1,15}_[A-Z][a-zA-Z]{1,15}$/',

        // Dodatne kolone koje se upisuju pri registraciji preko UCP-a.
        // {NOW} = trenutno vreme (DATETIME), {UNIX} = unix timestamp, {IP} = IP adresa
        'register_defaults' => [
            'level'      => 1,
            'money'      => 5000,
            'skin'       => 26,
            'registered' => '{NOW}',
            'reg_ip'     => '{IP}',
        ],
    ],

    /* ---------------------------------------------------------------
     | Statistika na UCP dashboardu
     | fmt: int | money | gold | hours | bool | text | datetime | map
     * ------------------------------------------------------------- */
    'stats' => [
        ['label' => 'Level',        'col' => 'level',   'fmt' => 'int',   'icon' => 'star'],
        ['label' => 'Novac',        'col' => 'money',   'fmt' => 'money', 'icon' => 'cash'],
        ['label' => 'Banka',        'col' => 'bank',    'fmt' => 'money', 'icon' => 'bank'],
        ['label' => 'Zlato',        'col' => 'gold',    'fmt' => 'gold',  'icon' => 'gold'],
        ['label' => 'Sati igre',    'col' => 'hours',   'fmt' => 'hours', 'icon' => 'clock'],
        ['label' => 'Respekt',      'col' => 'respect', 'fmt' => 'int',   'icon' => 'up'],
        ['label' => 'Posao',        'col' => 'job',     'fmt' => 'map',   'icon' => 'job',
            'map' => [0 => 'Nezaposlen', 1 => 'Mesar', 2 => 'Stočar', 3 => 'Kamiondžija', 4 => 'Taksista']],
        ['label' => 'Organizacija', 'col' => 'org',     'fmt' => 'map',   'icon' => 'org',
            'map' => [0 => 'Civil', 1 => 'Chicago Police Department', 2 => 'Grove Street', 3 => 'Bandera Sreće']],
        ['label' => 'VIP',          'col' => 'vip',     'fmt' => 'map',   'icon' => 'vip',
            'map' => [0 => 'Nema', 1 => 'Bronze', 2 => 'Silver', 3 => 'Gold', 4 => 'Platinum', 5 => 'Diamond']],
        ['label' => 'Opomene',      'col' => 'warns',   'fmt' => 'int',   'icon' => 'warn'],
    ],

    // Nazivi admin nivoa (kolona 'admin')
    'admin_levels' => [
        0 => null, 1 => 'Helper', 2 => 'Admin', 3 => 'Senior Admin', 4 => 'Head Admin', 5 => 'Direktor', 6 => 'Vlasnik',
    ],

    /* ---------------------------------------------------------------
     | High Command (portal) - skin = SA-MP skin ID
     | Rank kartice: A = vlasnik, K = co-owner, J = skripter
     * ------------------------------------------------------------- */
    'staff' => [
        ['name' => 'Howo',       'role' => 'Vlasnik',  'card' => 'A', 'suit' => '♠','skin' => 294],
        ['name' => 'Elvedin',    'role' => 'Vlasnik',  'card' => 'A', 'suit' => '♣','skin' => 165],
        ['name' => 'Bato Rider', 'role' => 'Co-Owner', 'card' => 'K', 'suit' => '♠','skin' => 299],
        ['name' => 'RomaN',      'role' => 'Skripter', 'card' => 'J', 'suit' => '♣','skin' => 187],
    ],

    /* ---------------------------------------------------------------
     | Organizacije + zone (teritorije)
     | Clanovi se citaju iz tabele naloga (member_col / rank_col).
     * ------------------------------------------------------------- */
    'orgs' => [
        'table'      => 'organizations',
        'id'         => 'id',
        'name'       => 'name',
        'type'       => 'type',          // null ako nema
        'types'      => [0 => 'Legalna', 1 => 'Ilegalna'],
        'leader'     => 'leader',        // ime lidera (tekst) ili null -> uzima clana sa najvecim rankom
        'color'      => 'color',         // 'FF0000' / '#FF0000' / '0xFF0000AA' / int ili null
        'member_col' => 'org',           // kolona u tabeli naloga = ID organizacije
        'rank_col'   => 'org_rank',      // null ako nema
        'rank_names' => [1 => 'Član', 2 => 'Iskusni član', 3 => 'Desna ruka', 4 => 'Savetnik', 5 => 'Zamenik', 6 => 'Lider'],
    ],
    'zones' => [
        'table' => 'gangzones',
        'id'    => 'id',
        'name'  => 'name',               // null ako zone nemaju ime
        'owner' => 'owner',              // ID organizacije (0 = slobodna)
        'top'   => 10,
    ],

    /* ---------------------------------------------------------------
     | Ban lista
     * ------------------------------------------------------------- */
    'bans' => [
        'table'       => 'bans',
        'id'          => 'id',
        'name'        => 'name',
        'admin'       => 'admin',
        'reason'      => 'reason',
        'date'        => 'date',
        'expires'     => 'expires',      // 0 / NULL = trajni ban; null ako nema kolone
        'ip'          => 'ip',           // vidi samo admin; null ako nema
        'date_format' => 'datetime',     // 'datetime' ili 'unix' - kako gamemode cuva vreme
        'unban'       => 'delete',       // unban = brisanje reda (tako radi gamemode)
        'active_col'  => null,
        'per_page'    => 25,
    ],

    /* ---------------------------------------------------------------
     | Imovina igraca (UCP + admin)
     | owner_by: 'name' (vlasnik upisan kao ime) ili 'id' (ID naloga)
     * ------------------------------------------------------------- */
    'property' => [
        'houses' => [
            'label' => 'Kuće', 'icon' => 'home',
            'table' => 'houses', 'id' => 'id', 'owner' => 'owner', 'owner_by' => 'name',
            'title' => 'address',
            'fields' => [
                ['label' => 'Vrednost', 'col' => 'price',  'fmt' => 'money'],
                ['label' => 'Level',    'col' => 'level',  'fmt' => 'int'],
                ['label' => 'Zaključana', 'col' => 'locked', 'fmt' => 'bool'],
            ],
        ],
        'businesses' => [
            'label' => 'Firme', 'icon' => 'bank',
            'table' => 'businesses', 'id' => 'id', 'owner' => 'owner', 'owner_by' => 'name',
            'title' => 'name',
            'fields' => [
                ['label' => 'Vrednost', 'col' => 'price', 'fmt' => 'money'],
                ['label' => 'Kasa',     'col' => 'till',  'fmt' => 'money'],
                ['label' => 'Tip',      'col' => 'type',  'fmt' => 'map', 'map' => [0 => 'Prodavnica', 1 => 'Pumpa', 2 => 'Restoran', 3 => 'Klub']],
            ],
        ],
        'vehicles' => [
            'label' => 'Vozila', 'icon' => 'car',
            'table' => 'vehicles', 'id' => 'id', 'owner' => 'owner', 'owner_by' => 'name',
            'model' => 'model',              // SA-MP model ID (400-611) -> slika i ime
            'title' => 'plate',
            'fields' => [
                ['label' => 'Tablice',  'col' => 'plate', 'fmt' => 'text'],
                ['label' => 'Gorivo',   'col' => 'fuel',  'fmt' => 'percent'],
                ['label' => 'Kilometri', 'col' => 'km',   'fmt' => 'km'],
            ],
        ],
    ],

    /* ---------------------------------------------------------------
     | Web admin panel (prema koloni account.admin)
     * ------------------------------------------------------------- */
    'admin_panel' => [
        'min_level'   => 3,   // ulaz u panel
        'ban_level'   => 3,   // ban / unban
        'edit_level'  => 4,   // izmena statistike igraca
        'owner_level' => 6,   // menja admin nivoe drugima
        'online_col'  => 'online', // kolona u tabeli naloga: 1 = igrac je u igri (upozorenje pri izmeni). null ako nema
        // Polja koja admin moze da menja (col mora postojati u tabeli naloga)
        'editable' => [
            ['label' => 'Level',        'col' => 'level',   'min' => 0, 'max' => 1000],
            ['label' => 'Novac',        'col' => 'money',   'min' => 0, 'max' => 2000000000],
            ['label' => 'Banka',        'col' => 'bank',    'min' => 0, 'max' => 2000000000],
            ['label' => 'Zlato',        'col' => 'gold',    'min' => 0, 'max' => 1000000],
            ['label' => 'Respekt',      'col' => 'respect', 'min' => 0, 'max' => 100000],
            ['label' => 'Skin',         'col' => 'skin',    'min' => 0, 'max' => 311],
            ['label' => 'Posao',        'col' => 'job',     'min' => 0, 'max' => 50],
            ['label' => 'Organizacija', 'col' => 'org',     'min' => 0, 'max' => 100],
            ['label' => 'Rank u org.',  'col' => 'org_rank','min' => 0, 'max' => 10],
            ['label' => 'VIP',          'col' => 'vip',     'min' => 0, 'max' => 5],
            ['label' => 'Opomene',      'col' => 'warns',   'min' => 0, 'max' => 3],
        ],
    ],

    /* ---------------------------------------------------------------
     | Zastita
     * ------------------------------------------------------------- */
    'security' => [
        'login_max'       => 5,     // pokusaja
        'login_window'    => 900,   // u sekundama (15 min)
        'register_max'    => 3,     // registracija po IP-u
        'register_window' => 3600,  // 1h
        'min_password'    => 6,
        'registration_open' => true,
    ],
];
