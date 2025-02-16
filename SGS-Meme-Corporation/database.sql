CREATE DATABASE sgs_meme_corp;

USE sgs_meme_corp;

CREATE TABLE thoughts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    thought TEXT NOT NULL,
    image VARCHAR(255),
    ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ip_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(45),
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
