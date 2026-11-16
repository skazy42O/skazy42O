<?php
require dirname(__DIR__) . '/app/bootstrap.php';
logout_user();
session_start();
flash('success', 'Uspešno si se odjavio. Vidimo se u gradu!');
redirect('login.php');
