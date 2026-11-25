from flask import Blueprint, redirect, render_template, request, session, url_for

from middleware.auth import STAFF_ROLES, require_permission, require_role
from models.announcement import Announcement
from models.job_application import JobApplication
from models.job_posting import JobPosting
from models.user import PERMISSIONS, ROLES, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def guard_admin_panel():
    """Anyone with a staff role (admin or moderator) can at least open the
    panel; which sections they can actually use past that point is decided
    per-route below, by require_permission (or require_role("admin") for the
    one thing even a moderator can't do: granting roles to someone else)."""
    return require_role(*STAFF_ROLES)


@admin_bp.route("")
def dashboard():
    """
    Admin panel home: record counts and links to manage each entity, filtered
    to what this session is actually allowed to do.
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML admin dashboard
      302:
        description: Redirect to /login if not logged in
      403:
        description: Logged in but not staff
    """
    is_admin = session.get("staff_role") == "admin"
    permissions = session.get("permissions", [])

    def can(permission):
        return is_admin or permission in permissions

    return render_template(
        "admin/dashboard.html",
        user_count=len(User.get_all()),
        announcement_count=len(Announcement.get_all()),
        job_posting_count=len(JobPosting.get_all()),
        application_count=len(JobApplication.get_all()),
        pending_user_count=len(User.get_pending()),
        pending_job_posting_count=len(JobPosting.get_pending()),
        pending_announcement_count=len(Announcement.get_pending()),
        is_admin=is_admin,
        can_manage_users=can("manage_users"),
        can_add_users=can("add_users"),
        can_approve_users=can("approve_users"),
        can_approve_job_postings=can("approve_job_postings"),
        can_approve_announcements=can("approve_announcements"),
    )


@admin_bp.route("/users")
def users():
    """
    List every user with their role and staff role. Requires manage_users
    (or admin).
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML page listing users with their roles
      403:
        description: Logged in but missing the manage_users permission
    """
    guard = require_permission("manage_users")
    if guard:
        return guard

    return render_template(
        "admin/users.html",
        users=User.get_all(),
        is_admin=session.get("staff_role") == "admin",
    )


@admin_bp.route("/users/new", methods=["GET", "POST"])
def new_user():
    """
    Create a user account directly (bypassing self-registration). Requires
    add_users (or admin). Created already 'approved'.
    ---
    tags:
      - AdminController
    parameters:
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: email
        in: formData
        type: string
      - name: graduation_year
        in: formData
        type: integer
    responses:
      200:
        description: HTML form
      302:
        description: Redirect back to the user list after creating, or back with an error
      403:
        description: Logged in but missing the add_users permission
    """
    guard = require_permission("add_users")
    if guard:
        return guard

    if request.method == "POST":
        User.create(
            request.form.get("first_name"),
            request.form.get("last_name"),
            request.form.get("graduation_year"),
            request.form.get("email"),
        )
        return redirect(url_for("admin.users"))

    return render_template("admin/new_user.html")


@admin_bp.route("/users/pending")
def pending_users():
    """
    List registrations awaiting approval. Requires approve_users (or admin).
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML page listing pending users
      403:
        description: Logged in but missing the approve_users permission
    """
    guard = require_permission("approve_users")
    if guard:
        return guard

    return render_template("admin/pending_users.html", users=User.get_pending())


@admin_bp.route("/users/<int:user_id>/approve", methods=["POST"])
def approve_user(user_id):
    """
    Approve a pending registration. Requires approve_users (or admin).
    ---
    tags:
      - AdminController
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the pending list after approving
      403:
        description: Logged in but missing the approve_users permission
      404:
        description: User not found
    """
    guard = require_permission("approve_users")
    if guard:
        return guard

    user = User.get_by_id(user_id)
    if user is None:
        return render_template("404.html"), 404

    User.approve(user_id)
    return redirect(url_for("admin.pending_users"))


@admin_bp.route("/job-postings/pending")
def pending_job_postings():
    """
    List job postings awaiting approval. Requires approve_job_postings (or admin).
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML page listing pending job postings
      403:
        description: Logged in but missing the approve_job_postings permission
    """
    guard = require_permission("approve_job_postings")
    if guard:
        return guard

    return render_template("admin/pending_job_postings.html", job_postings=JobPosting.get_pending())


@admin_bp.route("/job-postings/<int:job_posting_id>/approve", methods=["POST"])
def approve_job_posting(job_posting_id):
    """
    Approve a pending job posting. Requires approve_job_postings (or admin).
    ---
    tags:
      - AdminController
    parameters:
      - name: job_posting_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the pending list after approving
      403:
        description: Logged in but missing the approve_job_postings permission
      404:
        description: Job posting not found
    """
    guard = require_permission("approve_job_postings")
    if guard:
        return guard

    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return render_template("404.html"), 404

    JobPosting.approve(job_posting_id)
    return redirect(url_for("admin.pending_job_postings"))


@admin_bp.route("/announcements/pending")
def pending_announcements():
    """
    List announcements awaiting approval. Requires approve_announcements (or admin).
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML page listing pending announcements
      403:
        description: Logged in but missing the approve_announcements permission
    """
    guard = require_permission("approve_announcements")
    if guard:
        return guard

    return render_template(
        "admin/pending_announcements.html", announcements=Announcement.get_pending()
    )


@admin_bp.route("/announcements/<int:announcement_id>/approve", methods=["POST"])
def approve_announcement(announcement_id):
    """
    Approve a pending announcement. Requires approve_announcements (or admin).
    ---
    tags:
      - AdminController
    parameters:
      - name: announcement_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the pending list after approving
      403:
        description: Logged in but missing the approve_announcements permission
      404:
        description: Announcement not found
    """
    guard = require_permission("approve_announcements")
    if guard:
        return guard

    announcement = Announcement.get_by_id(announcement_id)
    if announcement is None:
        return render_template("404.html"), 404

    Announcement.approve(announcement_id)
    return redirect(url_for("admin.pending_announcements"))


@admin_bp.route("/users/<int:user_id>/role", methods=["GET", "POST"])
def edit_role(user_id):
    """
    Show a form to change a user's role/staff role/permissions, or save the
    change. Unlike every other /admin route, this is admin-only — granting
    elevated access is not something a moderator permission can unlock, by
    design (see DDD.md).
    ---
    tags:
      - AdminController
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: role
        in: formData
        type: string
        enum: [alumni, student]
      - name: staff_role
        in: formData
        type: string
        enum: ["", admin, moderator]
      - name: permissions
        in: formData
        type: array
        items:
          type: string
    responses:
      200:
        description: HTML role edit form
      302:
        description: Redirect back to /admin/users after saving, or back with an error
      403:
        description: Logged in but not an admin
      404:
        description: User not found
    """
    guard = require_role("admin")
    if guard:
        return guard

    user = User.get_by_id(user_id)
    if user is None:
        return render_template("404.html"), 404

    if request.method == "POST":
        role = request.form.get("role")
        staff_role = request.form.get("staff_role") or None

        errors = User.validate_roles(role, staff_role)
        if errors:
            return redirect(url_for("admin.edit_role", user_id=user_id, error=", ".join(errors)))

        User.set_roles(user_id, role, staff_role)
        # Permissions only ever mean anything for a moderator — assigning
        # admin or plain alumni/student clears any leftover permission grant.
        User.set_permissions(
            user_id,
            request.form.getlist("permissions") if staff_role == "moderator" else [],
        )
        return redirect(url_for("admin.users"))

    return render_template(
        "admin/edit_role.html",
        user=user,
        roles=ROLES,
        staff_roles=STAFF_ROLES,
        permissions=PERMISSIONS,
        granted_permissions=User.get_permissions(user_id),
        error=request.args.get("error"),
    )
