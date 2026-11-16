-- IZMISLJENI demo podaci SAMO za lokalni test izgleda (ne ide na pravi server).
INSERT INTO organizations (id,name,type,leader,color) VALUES
 (1,'Chicago Police Department',0,'Howo_Boss','3A8CC6'),(2,'Grove Street Families',1,NULL,'2FBF4A'),
 (3,'Bandera Srece',1,'Neca_Brat','F0C35A'),(4,'Los Santos Vagos',1,NULL,'FACC15'),
 (5,'Ballas',1,NULL,'A855F7'),(6,'Sinaloa Kartel',1,NULL,'E0485B'),(7,'Yakuza',1,NULL,'F97316'),
 (8,'Russian Mafia',1,NULL,'94A3B8'),(9,'La Cosa Nostra',1,NULL,'0EA5E9'),(10,'Black Kings',1,NULL,'111827'),
 (11,'Hitna Pomoc',0,NULL,'EC4899'),(12,'Aztecas',1,NULL,'22D3EE');
INSERT INTO gangzones (name,owner)
 SELECT CONCAT(ELT(1+MOD(seq,8),'Ganton','Idlewood','Jefferson','East LS','Willowfield','Playa','Glen Park','El Corona'),' ',seq), 
   ELT(1+MOD(seq*7,30), 2,2,2,2,2,2,3,3,3,3,3,4,4,4,4,5,5,5,6,6,6,7,7,8,8,9,10,12,0,0)
 FROM (SELECT @r:=@r+1 AS seq FROM information_schema.columns, (SELECT @r:=0) x LIMIT 60) t;
UPDATE users SET org=1, org_rank=6 WHERE name='Howo_Boss';
INSERT INTO users (name,password,level,skin,org,org_rank,admin) VALUES
 ('Neca_Brat','x',22,105,3,6,0),('Roki_Tyson','x',15,106,3,4,0),('Djole_Stevic','x',18,107,3,3,2),
 ('Dzale_Dzambas','x',9,102,3,1,0),('Skinny_Sooknew','x',30,280,1,4,0),('Omer_Sinanoski','x',12,281,1,2,0),
 ('Tarik_Shuta','x',7,105,2,5,0),('Jack_Luceno','x',11,106,2,1,0),('Mislav_Stunkovic','x',4,26,0,0,0);
INSERT INTO bans (name,admin,reason,date,expires,ip) VALUES
 ('Cheater_Pro','Howo_Boss','Aimbot / cheat','2026-11-10 21:14:00',NULL,'85.12.33.4'),
 ('Lazni_Policajac','Elvedin_Admin','Non-RP, vredjanje','2026-11-14 18:02:00','2026-11-21 18:02:00','93.86.1.20'),
 ('Brzi_Gonzales','Howo_Boss','Speed hack','2026-10-02 12:00:00','2026-10-09 12:00:00',NULL),
 ('Marko_Spamer','Djole_Stevic','Reklamiranje drugog servera','2026-11-15 22:45:00',NULL,'178.1.2.3');
INSERT INTO houses (owner,address,price,level,locked) VALUES ('Howo_Boss','Vinewood Hills 12',2500000,20,1),('Howo_Boss','Santa Maria Beach 4',780000,8,0);
INSERT INTO businesses (owner,name,type,price,till) VALUES ('Howo_Boss','24/7 Idlewood',0,950000,48230);
INSERT INTO vehicles (owner,model,plate,fuel,km) VALUES ('Howo_Boss',411,'BJ-001',87,12450),('Howo_Boss',560,'BJ-777',54,40120),('Howo_Boss',522,'BJ-RIDE',100,3010),('Howo_Boss',487,'BJ-HELI',72,890);
