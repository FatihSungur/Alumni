ALTER TABLE users
    ADD COLUMN staff_role VARCHAR(20) CHECK (staff_role IN ('admin', 'moderator'));
