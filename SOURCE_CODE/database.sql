create database BTL_MMT

use BTL_MMT

CREATE TABLE Users(
	UserName varchar(50) PRIMARY KEY,
	Pass varchar(50) NOT NULL
)

CREATE TABLE Files (
    LocalFileName CHAR(100),
    SharedFileName CHAR(100),
    PRIMARY KEY (LocalFileName, SharedFileName)
);

CREATE TABLE UserFiles (
    UserName varchar(50),
    LocalFileName CHAR(100),
    SharedFileName CHAR(100),
    CONSTRAINT FK_UserFiles_Users FOREIGN KEY (UserName) REFERENCES Users(UserName),
    CONSTRAINT FK_UserFiles_Files FOREIGN KEY (LocalFileName, SharedFileName) REFERENCES Files(LocalFileName, SharedFileName),
    PRIMARY KEY (UserName, LocalFileName, SharedFileName)
);

INSERT INTO Users (UserName, Pass) VALUES
('1', '123'),
('2', '123'),
('3', '123');

INSERT INTO Files (LocalFileName, SharedFileName) VALUES
('file1.txt', 'shared_file1.txt'),
('file2.txt', 'shared_file2.txt'),
('file3.txt', 'shared_file3.txt');


INSERT INTO UserFiles (UserName, LocalFileName, SharedFileName) VALUES
('1', 'file1.txt', 'shared_file1.txt'),
('2', 'file2.txt', 'shared_file2.txt');
