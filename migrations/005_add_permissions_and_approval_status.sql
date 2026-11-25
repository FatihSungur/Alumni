CREATE TABLE moderator_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    permission VARCHAR(30) NOT NULL CHECK (permission IN (
        'approve_users',
        'manage_users',
        'add_users',
        'approve_job_postings',
        'approve_announcements'
    )),
    UNIQUE (user_id, permission)
);

-- DEFAULT 'approved' so every existing row (and any insert that doesn't
-- mention status, e.g. factories/seed) is grandfathered in as already
-- approved. Only the public creation flows (register, job posting,
-- announcement) explicitly insert 'pending' going forward.
ALTER TABLE users
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (status IN ('pending', 'approved'));

ALTER TABLE job_postings
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (status IN ('pending', 'approved'));

ALTER TABLE announcements
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (status IN ('pending', 'approved'));
