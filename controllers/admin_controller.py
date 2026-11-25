from flask import Blueprint, redirect, render_template, request, url_for

from middleware.auth import require_role
from models.announcement import Announcement
from models.job_application import JobApplication
from models.job_posting import JobPosting
from models.user import ROLES, STAFF_ROLES, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def guard_admin_panel():
    """Everything under /admin requires the 'admin' staff role specifically —
    a moderator can delete content (see middleware/auth.py staff_required),
    but only an admin can grant/revoke admin or moderator to other users."""
    return require_role("admin")


@admin_bp.route("")
def dashboard():
    """
    Admin panel home: record counts and links to manage each entity.
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML admin dashboard
      302:
        description: Redirect to /login if not logged in
      403:
        description: Logged in but not an admin
    """
    return render_template(
        "admin/dashboard.html",
        user_count=len(User.get_all()),
        announcement_count=len(Announcement.get_all()),
        job_posting_count=len(JobPosting.get_all()),
        application_count=len(JobApplication.get_all()),
    )


@admin_bp.route("/users")
def users():
    """
    List every user with their role and staff role.
    ---
    tags:
      - AdminController
    responses:
      200:
        description: HTML page listing users with their roles
      302:
        description: Redirect to /login if not logged in
      403:
        description: Logged in but not an admin
    """
    return render_template("admin/users.html", users=User.get_all())


@admin_bp.route("/users/<int:user_id>/role", methods=["GET", "POST"])
def edit_role(user_id):
    """
    Show a form to change a user's role/staff role, or save the change.
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
        return redirect(url_for("admin.users"))

    return render_template(
        "admin/edit_role.html",
        user=user,
        roles=ROLES,
        staff_roles=STAFF_ROLES,
        error=request.args.get("error"),
    )
