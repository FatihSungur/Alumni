ALTER TABLE users
    ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'alumni' CHECK (role IN ('alumni', 'student')),
    ADD COLUMN password_hash VARCHAR(255);
