#!/bin/bash
set -e

# Create the UserManagement database if not already created
psql -U user -d postgres -c "CREATE DATABASE UserManagement;"

# Create the users table
psql -U user -d UserManagement -c "
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

# Create the CompetitionService database if not already created
psql -U user -d postgres -c "CREATE DATABASE CompetitionService;"

# Create the competitions table
psql -U user -d CompetitionService -c "
CREATE TABLE IF NOT EXISTS competitions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

# Create the submissions table
psql -U user -d UserManagement -c "
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    competition_id INT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);"

# Create the subscriptions table without foreign key to competitions
psql -U user -d UserManagement -c "
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    competition_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);"
