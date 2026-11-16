-- PRIMER tabele naloga - SAMO za lokalno testiranje UCP-a.
-- Na pravom serveru se koristi postojeca tabela iz gamemode-a
-- (kolone se mapiraju u app/config.php).
CREATE TABLE IF NOT EXISTS `users` (
  `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`       VARCHAR(24)  NOT NULL,
  `password`   VARCHAR(255) NOT NULL,
  `email`      VARCHAR(100) DEFAULT NULL,
  `level`      INT NOT NULL DEFAULT 1,
  `money`      INT NOT NULL DEFAULT 0,
  `bank`       INT NOT NULL DEFAULT 0,
  `gold`       INT NOT NULL DEFAULT 0,
  `hours`      INT NOT NULL DEFAULT 0,
  `respect`    INT NOT NULL DEFAULT 0,
  `skin`       SMALLINT NOT NULL DEFAULT 26,
  `job`        TINYINT NOT NULL DEFAULT 0,
  `org`        TINYINT NOT NULL DEFAULT 0,
  `org_rank`   TINYINT NOT NULL DEFAULT 0,
  `vip`        TINYINT NOT NULL DEFAULT 0,
  `warns`      TINYINT NOT NULL DEFAULT 0,
  `admin`      TINYINT NOT NULL DEFAULT 0,
  `registered` DATETIME DEFAULT NULL,
  `last_login` DATETIME DEFAULT NULL,
  `reg_ip`     VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `organizations` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(48) NOT NULL,
  `type` TINYINT NOT NULL DEFAULT 1,       -- 0 legalna, 1 ilegalna
  `leader` VARCHAR(24) DEFAULT NULL,
  `color` VARCHAR(10) DEFAULT NULL,         -- npr. 3A8CC6
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `gangzones` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(48) DEFAULT NULL,
  `owner` INT NOT NULL DEFAULT 0,           -- ID organizacije, 0 = slobodna
  PRIMARY KEY (`id`), KEY `owner` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `bans` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(24) NOT NULL,
  `admin` VARCHAR(24) DEFAULT NULL,
  `reason` VARCHAR(128) DEFAULT NULL,
  `date` DATETIME DEFAULT NULL,
  `expires` DATETIME DEFAULT NULL,          -- NULL = trajno
  `ip` VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY (`id`), KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `houses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `owner` VARCHAR(24) DEFAULT NULL,
  `address` VARCHAR(64) DEFAULT NULL,
  `price` INT NOT NULL DEFAULT 0,
  `level` INT NOT NULL DEFAULT 1,
  `locked` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`), KEY `owner` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `businesses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `owner` VARCHAR(24) DEFAULT NULL,
  `name` VARCHAR(64) DEFAULT NULL,
  `type` TINYINT NOT NULL DEFAULT 0,
  `price` INT NOT NULL DEFAULT 0,
  `till` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`), KEY `owner` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `vehicles` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `owner` VARCHAR(24) DEFAULT NULL,
  `model` SMALLINT NOT NULL,
  `plate` VARCHAR(16) DEFAULT NULL,
  `fuel` TINYINT NOT NULL DEFAULT 100,
  `km` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`), KEY `owner` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
