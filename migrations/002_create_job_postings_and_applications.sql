-- Migration 002: create job_postings and job_applications, as designed in DDD.md
-- job_postings:   one-to-many with users (one user can post many jobs)
-- job_applications: many-to-many junction between users and job_postings (applying)

CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(150) NOT NULL,
    posted_by INTEGER NOT NULL REFERENCES users(id),
    posted_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id),
    applied_date DATE NOT NULL,
    UNIQUE (user_id, job_posting_id)
);
