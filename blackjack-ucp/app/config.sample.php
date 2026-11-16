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
            'map' => [0 => 'Nezaposlen', 1 => 'Mesar', 2 => 'Stocar', 3 => 'Kamiondzija', 4 => 'Taksista']],
        ['label' => 'Organizacija', 'col' => 'org',     'fmt' => 'map',   'icon' => 'org',
            'map' => [0 => 'Civil', 1 => 'Chicago Police Department', 2 => 'Grove Street', 3 => 'Bandera Srece']],
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
