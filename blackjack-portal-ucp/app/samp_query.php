<?php
declare(strict_types=1);

/**
 * SA-MP query ('i' paket) - vraca online / max / hostname.
 * Rezultat se kesira u storage/cache da ne bi svaki posetilac slao UDP upit.
 */
function samp_status(): array
{
    $cacheFile = STORAGE_DIR . '/cache/server.json';
    $ttl = (int)cfg('server.cache_sec', 30);
    if (is_file($cacheFile) && filemtime($cacheFile) > time() - $ttl) {
        $c = json_decode((string)file_get_contents($cacheFile), true);
        if (is_array($c)) {
            return $c;
        }
    }

    $res = ['online' => false, 'players' => 0, 'max' => 0, 'hostname' => '', 'gamemode' => '', 'updated' => time()];
    $host = (string)cfg('server.host');
    $port = (int)cfg('server.port', 7777);
    $ip = filter_var($host, FILTER_VALIDATE_IP) ? $host : gethostbyname($host);

    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
        $sock = @fsockopen('udp://' . $ip, $port, $errno, $errstr, 2);
        if ($sock) {
            stream_set_timeout($sock, 2);
            $packet = 'SAMP';
            foreach (explode('.', $ip) as $oct) {
                $packet .= chr((int)$oct);
            }
            $packet .= chr($port & 0xFF) . chr(($port >> 8) & 0xFF) . 'i';
            fwrite($sock, $packet);
            $data = fread($sock, 2048);
            fclose($sock);

            if (is_string($data) && strlen($data) > 11 + 5) {
                $o = 11;
                $o += 1; // password flag
                $players = unpack('v', substr($data, $o, 2))[1]; $o += 2;
                $max     = unpack('v', substr($data, $o, 2))[1]; $o += 2;
                $len = unpack('V', substr($data, $o, 4))[1]; $o += 4;
                $hostname = substr($data, $o, $len); $o += $len;
                $len = unpack('V', substr($data, $o, 4))[1] ?? 0; $o += 4;
                $gm = substr($data, $o, $len);

                $res = [
                    'online'   => true,
                    'players'  => (int)$players,
                    'max'      => (int)$max,
                    'hostname' => samp_to_utf8($hostname),
                    'gamemode' => samp_to_utf8($gm),
                    'updated'  => time(),
                ];
            }
        }
    }

    @file_put_contents($cacheFile, json_encode($res), LOCK_EX);
    return $res;
}

/** SA-MP salje tekst u Windows-1250 (balkanski znakovi). */
function samp_to_utf8(string $s): string
{
    if (preg_match('//u', $s)) {
        return $s;
    }
    $out = function_exists('iconv') ? @iconv('CP1250', 'UTF-8//IGNORE', $s) : false;
    return $out !== false ? $out : mb_convert_encoding($s, 'UTF-8', 'ISO-8859-2');
}
