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
  `vip`        TINYINT NOT NULL DEFAULT 0,
  `warns`      TINYINT NOT NULL DEFAULT 0,
  `admin`      TINYINT NOT NULL DEFAULT 0,
  `registered` DATETIME DEFAULT NULL,
  `last_login` DATETIME DEFAULT NULL,
  `reg_ip`     VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
