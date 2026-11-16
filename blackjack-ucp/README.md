# BLACK JACK RolePlay — Portal & UCP

Portal + User Control Panel za SA-MP server **Black Jack RolePlay**.
PHP 8 + MySQL (ista baza koju koristi gamemode), radi na Windows VPS-u (XAMPP / Laragon / IIS).

## Šta ima
- **Portal** — hero sa logom, IP box (kopiraj / `samp://` connect), live online brojač (SA-MP query), rekord, broj registrovanih naloga, sekcija o serveru, **High Command** kartice (SA-MP skinovi kao karte A/K/J), galerija sa lightbox-om.
- **Registracija** — RP format imena `Ime_Prezime` (uživo provera), email, jačina lozinke, honeypot protiv botova, limit naloga po IP-u. Nalog se upisuje direktno u tabelu gamemode-a, pa odmah važi u igri.
- **Prijava** — istim imenom/lozinkom kao u igri, zaštita od brute-force (limit po IP-u i po imenu).
- **UCP** — skin karaktera, admin rank, statistika (level, novac, banka, zlato, sati, posao, organizacija, VIP…), info o nalogu, promena lozinke i emaila.
- **Organizacije** — top 10 po broju zauzetih zona (rang lista sa bojama organizacija), sve legalne/ilegalne organizacije, stranica organizacije sa članovima (rank, skin) i zonama.
- **Ban lista** — javna, sa pretragom i paginacijom (IP adrese vidi samo admin).
- **Imovina u UCP-u** — kuće, firme i vozila igrača (slike i imena svih SA-MP vozila 400–611).
- **Admin panel** (`/admin`) — pregled, pretraga igrača, izmena statistike, admin nivoi, ban/unban, istorija banova, imovina igrača i **log svih akcija** (tabela `ucp_admin_log` se pravi sama).
  - Prava po nivou (`config → admin_panel`): ulaz od nivoa 3, ban od 3, izmena od 4, admin nivoi samo vlasnik (6).
  - Admin ne može da menja/banuje nekog sa istim ili većim nivoom.
- Bezbednost: PDO prepared statements, CSRF tokeni, `session_regenerate_id`, HttpOnly/SameSite kolačići, `app/` van web root-a.

## Struktura
```
app/            logika, config, view-ovi (NIJE javno)
  config.sample.php   -> kopiraj u config.php
  storage/            kes + rate-limit (mora biti upisiv)
public/         web root (index.php, login.php, register.php, ucp/, api/, assets/)
sql/            primer tabele za lokalni test
```

## Instalacija na Windows VPS (XAMPP)
1. Instaliraj XAMPP (PHP 8.1+), uključi `extension=pdo_mysql` i `extension=mbstring` u `php.ini`.
2. Kopiraj folder `blackjack-ucp` npr. u `C:\xampp\htdocs\blackjack-ucp`.
3. U `C:\xampp\apache\conf\httpd.conf` podesi:
   ```
   DocumentRoot "C:/xampp/htdocs/blackjack-ucp/public"
   <Directory "C:/xampp/htdocs/blackjack-ucp/public">
       AllowOverride All
       Require all granted
   </Directory>
   ```
   (Ako ne možeš da menjaš DocumentRoot, `.htaccess` u rootu preusmerava na `public/` i blokira `app/`.)
4. Kopiraj `app/config.sample.php` → `app/config.php` i upiši:
   - `db` — podaci baze servera
   - `server.host` / `port` — IP SA-MP servera
   - `account` — ime tabele, kolone i **način hashovanja (mora biti isti kao u gamemode-u)**
   - `stats` — koje kolone se prikazuju u UCP-u
5. Otvori port 80/443 u Windows Firewall-u. Za HTTPS preporuka: Cloudflare ili win-acme (Let's Encrypt).

**IIS:** fizička putanja sajta = `public\`, instaliraj PHP preko FastCGI, `web.config` je već tu.

## Hash lozinke
| Gamemode koristi | `account.hash` |
|---|---|
| samp-bcrypt plugin | `bcrypt` |
| Whirlpool plugin | `whirlpool` |
| `SHA256_PassHash(pass, salt)` | `sha256_salt` (+ `account.salt` kolona) |
| MD5 | `md5` |

## Mapiranje tabela
Svaki modul ima svoj blok u `config.php` (`orgs`, `zones`, `bans`, `property`, `admin_panel`). Ako neka tabela ili kolona ne postoji, modul se samo sakrije — sajt ne puca. Kad pošalješ SQL dump, uskladimo imena.

## Lokalni test
```
mysql -u root blackjack < sql/primer_users.sql
mysql -u root blackjack < sql/primer_demo_podaci.sql   # izmišljeni podaci, samo za test
cd public && php -S 127.0.0.1:8080
```

---
Vlasnici: **Howo**, **Elvedin** · Co-Owner: **Bato Rider** · Skripter: **RomaN**
