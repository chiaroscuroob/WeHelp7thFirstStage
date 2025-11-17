# Week 5 — MySQL Assignment


## Task1

Enter password: ******
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 12
Server version: 8.4.7 MySQL Community Server - GPL

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

<img width="924" height="353" alt="task1_登入資料庫" src="https://github.com/user-attachments/assets/38f5c601-030b-4bc1-9c41-f25549651200" />

---

## Task2

### Create a new database named website

mysql> CREATE DATABASE website;
Query OK, 1 row affected (0.01 sec)

<img width="924" height="353" alt="task2_建立資料庫與資料表截圖" src="https://github.com/user-attachments/assets/5790d6b4-4985-4a97-969b-d3cfbfde0016" />


### Create a new table named member,in the  website  database,designed as below

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

<img width="936" height="653" alt="task2_成功截圖" src="https://github.com/user-attachments/assets/b0566e9f-41c6-471e-a0d4-fa82677c156f" />

---

## Task3

### INSERT a new row to the member table where name, email and password must be set to test , test@test.com , and test . INSERT additional 4 rows with arbitrary data

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

<img width="670" height="433" alt="task3_01建立test與任意4資料-2" src="https://github.com/user-attachments/assets/33f329bf-c5ab-4795-aa22-781d3b6f7af6" />


### SELECT all rows from the member table

mysql> SELECT * FROM member;

<img width="856" height="275" alt="task3_01建立test與任意4資料" src="https://github.com/user-attachments/assets/90cf698f-0a0a-4e84-bd77-7415f443bd4f" />


### SELECT all rows from the member table, in descending order of time

mysql> SELECT * FROM member
    -> ORDER BY time DESC;
    
<img width="863" height="522" alt="task3_03選擇資料表以時間遞減順序排列" src="https://github.com/user-attachments/assets/34e7c032-87f4-441c-8f25-b68be377536e" />


### SELECT total 3 rows, second to fourth, from the member table, in descending order of time. Note: it does not mean SELECT rows where id are 2, 3, or 4

mysql> SELECT * FROM member
    -> ORDER BY time DESC
    -> LIMIT 3 OFFSET 1;

<img width="865" height="276" alt="task3_04選擇3列資料從第2到4以時間遞減順序排列" src="https://github.com/user-attachments/assets/6446431f-b89c-4b26-90ce-5107afb28dcd" />


### SELECT rows where email equals to test@test.com

mysql> SELECT * FROM member
    -> WHERE email = 'test@test.com';

<img width="877" height="220" alt="task3_05查詢testemail" src="https://github.com/user-attachments/assets/b1c891c4-41f5-4774-893a-3d833da10449" />


### SELECT rows where name includes the es keyword

mysql> SELECT * FROM member
    -> WHERE name LIKE '%es%';
    
<img width="830" height="206" alt="task3_06查詢name_es" src="https://github.com/user-attachments/assets/82d37400-42cf-4456-bf3b-b319854e7591" />


### SELECT rows where email equals to test@test.com and password equals to test

mysql> SELECT * FROM member
    -> WHERE email = 'test@test.com'
    -> AND password = 'test';
    
<img width="860" height="227" alt="task3_07查詢emailtestpasswordtest" src="https://github.com/user-attachments/assets/04478f26-982b-4189-8e4d-38c931e292c7" />


### UPDATE data in name column to test2 where email equals to test@test.com

mysql> UPDATE member
    -> SET name = 'test2'
    -> WHERE email = 'test@test.com';

<img width="890" height="378" alt="task3_08更改emailtest的名稱為test2" src="https://github.com/user-attachments/assets/1f06a576-b388-43c7-ba77-2a05e2763a7b" />

---

## Task4

### SELECT how many rows from the member table
mysql> SELECT COUNT(*) FROM member;

<img width="471" height="207" alt="task4_01查詢有多少列" src="https://github.com/user-attachments/assets/ddab88be-8b2b-456f-a54b-771a3caafffd" />


### SELECT the sum of follower_count of all the rows from the member table

mysql> SELECT SUM(follower_count)
    -> FROM member;
    
<img width="1247" height="967" alt="task4_02計算追蹤者總和及更新追蹤數" src="https://github.com/user-attachments/assets/ee15f98d-5643-4a1b-a06a-6f77b7a74d68" />


### SELECT the average of follower_count of all the rows from the member table

mysql> SELECT AVG(follower_count)
    -> FROM member;
    
<img width="423" height="240" alt="task4_03計算追蹤者平均數" src="https://github.com/user-attachments/assets/16b595c5-1f92-471e-98da-0c662a218f99" />


### SELECT the average of follower_count of the first 2 rows, in descending order of follower_count, from the member table

mysql> SELECT AVG(follower_count)
    -> FROM (
    ->   SELECT follower_count
    ->   FROM member
    ->   ORDER BY follower_count DESC
    ->   LIMIT 2
    -> ) AS temp;

<img width="876" height="530" alt="task4_04遞減順序排列追蹤數選前兩列的平均" src="https://github.com/user-attachments/assets/ad5e6716-e39e-4b65-8791-121407248bad" />

---

## Task5

### Create a new table named message , in the website database. designed as below

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


### SELECT all messages, including sender names. We have to JOIN the member table to get that

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


### SELECT all messages, including sender names, where sender email equals to test@test.com . We have to JOIN the member table to filter and get that

SELECT
  m.*,
  mb.name AS sender_name
FROM message AS m
JOIN member AS mb
  ON m.member_id = mb.id
WHERE mb.email = 'test@test.com';

<img width="1047" height="397" alt="task5_03" src="https://github.com/user-attachments/assets/5790f031-01b3-4b69-9fff-cc72c336afac" />


### Use SELECT, SQL Aggregation Functions with JOIN statement, get the average like count of messages where sender email equals to test@test.com

mysql> SELECT
    -> AVG(m.like_count) AS avg_like
    -> FROM message AS m
    -> JOIN member AS mb
    -> ON m.member_id = mb.id
    -> WHERE mb.email = 'test@test.com';

<img width="590" height="343" alt="task5_04 emailtest的讚平均數" src="https://github.com/user-attachments/assets/5b57f366-35eb-414b-8175-697c0e3977cd" />


### Use SELECT, SQL Aggregation Functions with JOIN statement, get the average like count of messages GROUP BY sender email

mysql> SELECT
    -> mb.email,
    -> mb.name AS sender_name,
    -> AVG(m.like_count) AS avg_like
    -> FROM message AS m
    -> JOIN member AS mb
    -> ON m.member_id = mb.id
    -> GROUP BY mb.email,mb.name;
    
<img width="621" height="452" alt="task5_05 每個email自己的讚平均數" src="https://github.com/user-attachments/assets/a4348b73-b01e-454f-adaa-d6a7c01d9c78" />

