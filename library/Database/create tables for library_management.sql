drop database library_management;
create database if not exists library_management;
use library_management;

-- 1. Role table
CREATE TABLE `role` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
);

-- 2. Member table
CREATE TABLE `member` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` INT,
  `firstname` varchar(45) NOT NULL,
  `familyname` varchar(45) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `gender` ENUM('Male', 'Female', 'Other') NOT NULL,
  `dateofbirth` date DEFAULT NULL,
  `phone_number` VARCHAR(20) NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`role_id`) REFERENCES role (`id`)
);

-- 3. Admin table
CREATE TABLE `admin` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `role_id` INT,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `gender` ENUM('Male', 'Female', 'Other') NOT NULL,
  `date_of_birth` DATE NOT NULL,
  `phone_number` VARCHAR(20) NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  FOREIGN KEY (`role_id`) REFERENCES `role`(`id`),
  PRIMARY KEY (`id`)
);
 -- 4. Book table
CREATE TABLE `books` (
  `bookid` int NOT NULL AUTO_INCREMENT,
  `booktitle` varchar(45) DEFAULT NULL,
  `author` varchar(45) DEFAULT NULL,
  `category` varchar(15) DEFAULT NULL,
  `yearofpublication` int DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`bookid`)
);

-- 5. bookcopy table
CREATE TABLE `bookcopies` (
  `bookcopyid` int NOT NULL AUTO_INCREMENT,
  `bookid` int NOT NULL,
  `format` varchar(12) NOT NULL,
  PRIMARY KEY (`bookcopyid`),
  KEY `bookid_idx` (`bookid`),
  CONSTRAINT `bookid` FOREIGN KEY (`bookid`) REFERENCES `books` (`bookid`) ON DELETE CASCADE
);

-- 6.loan table
CREATE TABLE `loans` (
  `loanid` int NOT NULL AUTO_INCREMENT,
  `bookcopyid` int NOT NULL,
  `memberid` int NOT NULL,
  `loandate` date NOT NULL,
  `returned` tinyint DEFAULT NULL,
  PRIMARY KEY (`loanid`),
  FOREIGN KEY (`bookcopyid`) REFERENCES `bookcopies` (`bookcopyid`),
  FOREIGN KEY (`memberid`) REFERENCES `member` (`id`)
);