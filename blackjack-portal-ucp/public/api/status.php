<?php
require dirname(__DIR__, 2) . '/app/bootstrap.php';
session_write_close();
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: public, max-age=15');
$s = samp_status();
echo json_encode([
    'online'  => $s['online'],
    'players' => $s['players'],
    'max'     => $s['max'],
    'record'  => (int)cfg('server.record'),
    'updated' => $s['updated'],
]);
