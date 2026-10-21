-- Migration 003: create the job_applications table, as designed in DDD.md
-- Many-to-many relationship: one user can apply to many job_postings,
-- and one job_posting can receive applications from many users.

CREATE TABLE IF NOT EXISTS job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id),
    applied_date DATE NOT NULL,
    UNIQUE (user_id, job_posting_id)
);
