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

mysql> SHOW TABLES;
+-------------------+
| Tables_in_website |
+-------------------+
| member            |
+-------------------+
1 row in set (0.01 sec)

mysql> DESC member;
+----------------+--------------+------+-----+-------------------+-------------------+
| Field          | Type         | Null | Key | Default           | Extra             |
+----------------+--------------+------+-----+-------------------+-------------------+
| id             | int unsigned | NO   | PRI | NULL              | auto_increment    |
| name           | varchar(255) | NO   |     | NULL              |                   |
| email          | varchar(255) | NO   |     | NULL              |                   |
| password       | varchar(255) | NO   |     | NULL              |                   |
| follower_count | int unsigned | NO   |     | 0                 |                   |
| time           | datetime     | NO   |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED |
+----------------+--------------+------+-----+-------------------+-------------------+
6 rows in set (0.00 sec)

<img width="1920" height="1020" alt="task2_建立資料庫與資料表截圖" src="https://github.com/user-attachments/assets/8a7e60f7-d64b-40b3-9ee2-f322e5d978f4" />

<img width="1920" height="1020" alt="task2_成功截圖" src="https://github.com/user-attachments/assets/5e2c65db-63cb-4a32-969c-60749ed82794" />

--------------------------------------------------------------------------------------


# task3

01

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
+----+-------+-----------------+----------+----------------+---------------------+
| id | name  | email           | password | follower_count | time                |
+----+-------+-----------------+----------+----------------+---------------------+
|  1 | test  | test@test.com   | test     |              0 | 2025-11-16 20:24:39 |
|  2 | abc   | abc@abc.com     | abc      |              0 | 2025-11-16 20:29:42 |
|  3 | love  | love@love.com   | love     |              0 | 2025-11-16 20:30:09 |
|  4 | happy | happy@happy.com | happy    |              0 | 2025-11-16 20:30:31 |
|  5 | world | world@world.com | world    |              0 | 2025-11-16 20:30:56 |
+----+-------+-----------------+----------+----------------+---------------------+
5 rows in set (0.00 sec)

<img width="1920" height="1020" alt="task3_01建立test與任意4資料" src="https://github.com/user-attachments/assets/eacd3765-59c4-45db-9d4b-45c9557dbf8a" />

02

