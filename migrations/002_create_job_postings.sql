-- Migration 002: create the job_postings table, as designed in DDD.md
-- One-to-many relationship: one user (users.id) can post many job_postings (posted_by)

CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(150) NOT NULL,
    posted_by INTEGER NOT NULL REFERENCES users(id),
    posted_date DATE NOT NULL
);
