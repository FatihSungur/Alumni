-- Announcements had no owner at all until now — needed so a user can see
-- and manage "their own" announcements. Nullable: existing rows predate
-- this and have no known creator.
ALTER TABLE announcements
    ADD COLUMN created_by INTEGER REFERENCES users(id);

-- A student requesting to become an alumnus: pending until an admin (or a
-- moderator with approve_role_changes) approves it. NULL = no pending request.
ALTER TABLE users
    ADD COLUMN requested_role VARCHAR(20) CHECK (requested_role IN ('alumni', 'student'));

-- Add the new 'approve_role_changes' permission to the existing CHECK.
ALTER TABLE moderator_permissions
    DROP CONSTRAINT moderator_permissions_permission_check;

ALTER TABLE moderator_permissions
    ADD CONSTRAINT moderator_permissions_permission_check CHECK (permission IN (
        'approve_users',
        'manage_users',
        'add_users',
        'approve_job_postings',
        'approve_announcements',
        'approve_role_changes'
    ));
