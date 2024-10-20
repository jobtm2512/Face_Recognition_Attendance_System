CREATE DATABASE face_recognition_system;
USE face_recognition_system;

CREATE TABLE users (
    emp_name VARCHAR(100) NOT NULL,
    emp_id VARCHAR(50) NOT NULL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    joining_date DATE NOT NULL
);

CREATE TABLE face_embeddings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50),
    embedding BLOB,
    FOREIGN KEY (emp_id) REFERENCES users(emp_id)
);

CREATE TABLE attendance (
    emp_id VARCHAR(50),  
    attendance_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES users(emp_id)
);
ALTER TABLE attendance
ADD COLUMN event_id VARCHAR(50),
ADD FOREIGN KEY (event_id) REFERENCES events(event_id);


CREATE TABLE events (
    event_id VARCHAR(50) NOT NULL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_location VARCHAR(255),
    event_date DATE,
    event_description TEXT
);
INSERT INTO events (event_id, event_name, event_location, event_date, event_description)
VALUES ("E123", "Directorate AI Meeting", "Hospital", '2024-09-10', "nice event");

select * from users
select * from face_embeddings
select * from attendance
select * from events

SET SQL_SAFE_UPDATES = 0;
delete from users where emp_id = '1234'
delete from users
drop table events
drop table users




