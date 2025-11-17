# task2


Enter password: ******
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 12
Server version: 8.4.7 MySQL Community Server - GPL

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> CREATE DATABASE website;
Query OK, 1 row affected (0.01 sec)

mysql> USE website;
Database changed

mysql> CREATE TABLE member (
    ->   id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ->   name VARCHAR(255) NOT NULL,
    ->   email VARCHAR(255) NOT NULL,
    ->   password VARCHAR(255) NOT NULL,
    ->   follower_count INT UNSIGNED NOT NULL DEFAULT 0,
    ->   time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ->   PRIMARY KEY (id)
    -> );
Query OK, 0 rows affected (0.04 sec)

<img width="1920" height="1020" alt="task2_建立資料庫與資料表截圖" src="https://github.com/user-attachments/assets/8a7e60f7-d64b-40b3-9ee2-f322e5d978f4" />

<img width="1920" height="1020" alt="task2_成功截圖" src="https://github.com/user-attachments/assets/5e2c65db-63cb-4a32-969c-60749ed82794" />


--------------------------------------------------------------------------------------


# task3


01+02

mysql> INSERT INTO member (name, email, password)
    -> VALUES ('test', 'test@test.com', 'test');
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO member (name, email, password)
    -> VALUES ('abc', 'abc@abc.com', 'abc');
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO member (name, email, password)
    -> VALUES ('love', 'love@love.com', 'love');
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO member (name, email, password)
    -> VALUES ('happy', 'happy@happy.com', 'happy');
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO member (name, email, password)
    -> VALUES ('world', 'world@world.com', 'world');
Query OK, 1 row affected (0.01 sec)

mysql> SELECT * FROM member;

<img width="1920" height="1020" alt="task3_01建立test與任意4資料" src="https://github.com/user-attachments/assets/eacd3765-59c4-45db-9d4b-45c9557dbf8a" />


03

mysql> SELECT * FROM member
    -> ORDER BY time DESC;
    
<img width="863" height="522" alt="task3_03選擇資料表以時間遞減順序排列" src="https://github.com/user-attachments/assets/34e7c032-87f4-441c-8f25-b68be377536e" />


04

mysql> SELECT * FROM member
    -> ORDER BY time DESC
    -> LIMIT 3 OFFSET 1;

<img width="865" height="276" alt="task3_04選擇3列資料從第2到4以時間遞減順序排列" src="https://github.com/user-attachments/assets/6446431f-b89c-4b26-90ce-5107afb28dcd" />


05

mysql> SELECT * FROM member
    -> WHERE email = 'test@test.com';

<img width="877" height="220" alt="task3_05查詢testemail" src="https://github.com/user-attachments/assets/b1c891c4-41f5-4774-893a-3d833da10449" />


06

mysql> SELECT * FROM member
    -> WHERE name LIKE '%es%';
    
<img width="830" height="206" alt="task3_06查詢name_es" src="https://github.com/user-attachments/assets/82d37400-42cf-4456-bf3b-b319854e7591" />


07

mysql> SELECT * FROM member
    -> WHERE email = 'test@test.com'
    -> AND password = 'test';
    
<img width="860" height="227" alt="task3_07查詢emailtestpasswordtest" src="https://github.com/user-attachments/assets/04478f26-982b-4189-8e4d-38c931e292c7" />


08

mysql> UPDATE member
    -> SET name = 'test2'
    -> WHERE email = 'test@test.com';

<img width="890" height="378" alt="task3_08更改emailtest的名稱為test2" src="https://github.com/user-attachments/assets/1f06a576-b388-43c7-ba77-2a05e2763a7b" />


--------------------------------------------------------------------------------------


# task4


01

mysql> SELECT COUNT(*) FROM member;

<img width="471" height="207" alt="task4_01查詢有多少列" src="https://github.com/user-attachments/assets/ddab88be-8b2b-456f-a54b-771a3caafffd" />


02

mysql> SELECT SUM(follower_count)
    -> FROM member;
    
<img width="1247" height="967" alt="task4_02計算追蹤者總和及更新追蹤數" src="https://github.com/user-attachments/assets/ee15f98d-5643-4a1b-a06a-6f77b7a74d68" />


03

mysql> SELECT AVG(follower_count)
    -> FROM member;
    
<img width="423" height="240" alt="task4_03計算追蹤者平均數" src="https://github.com/user-attachments/assets/16b595c5-1f92-471e-98da-0c662a218f99" />


04

mysql> SELECT AVG(follower_count)
    -> FROM (
    ->   SELECT follower_count
    ->   FROM member
    ->   ORDER BY follower_count DESC
    ->   LIMIT 2
    -> ) AS temp;

<img width="876" height="530" alt="task4_04遞減順序排列追蹤數選前兩列的平均" src="https://github.com/user-attachments/assets/ad5e6716-e39e-4b65-8791-121407248bad" />


--------------------------------------------------------------------------------------


# task5


01

mysql> CREATE TABLE message (
    ->   id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ->   member_id INT UNSIGNED NOT NULL,
    ->   content TEXT NOT NULL,
    ->   like_count INT UNSIGNED NOT NULL DEFAULT 0,
    ->   time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ->   PRIMARY KEY (id),
    ->   FOREIGN KEY (member_id) REFERENCES member(id)
    -> );
Query OK, 0 rows affected (0.14 sec)


02

SELECT
  m.id,
  mb.name AS sender_name,
  m.content,
  m.like_count,
  m.time
FROM message AS m
JOIN member AS mb
  ON m.member_id = mb.id;

<img width="651" height="542" alt="task5_01 02" src="https://github.com/user-attachments/assets/f56697c4-67e5-467c-b2ca-d95cf12b5b06" />


03

SELECT
  m.*,
  mb.name AS sender_name
FROM message AS m
JOIN member AS mb
  ON m.member_id = mb.id
WHERE mb.email = 'test@test.com';

<img width="1047" height="397" alt="task5_03" src="https://github.com/user-attachments/assets/5790f031-01b3-4b69-9fff-cc72c336afac" />


04

mysql> SELECT
    -> AVG(m.like_count) AS avg_like
    -> FROM message AS m
    -> JOIN member AS mb
    -> ON m.member_id = mb.id
    -> WHERE mb.email = 'test@test.com';

<img width="590" height="343" alt="task5_04 emailtest的讚平均數" src="https://github.com/user-attachments/assets/5b57f366-35eb-414b-8175-697c0e3977cd" />


05

mysql> SELECT
    -> mb.email,
    -> mb.name AS sender_name,
    -> AVG(m.like_count) AS avg_like
    -> FROM message AS m
    -> JOIN member AS mb
    -> ON m.member_id = mb.id
    -> GROUP BY mb.email,mb.name;
    
<img width="621" height="452" alt="task5_05 每個email自己的讚平均數" src="https://github.com/user-attachments/assets/a4348b73-b01e-454f-adaa-d6a7c01d9c78" />

