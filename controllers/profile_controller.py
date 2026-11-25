import psycopg2
from flask import Blueprint, redirect, render_template, request, session, url_for

from middleware.auth import require_role
from models.announcement import Announcement
from models.job_application import JobApplication
from models.job_posting import JobPosting
from models.user import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.before_request
def guard_profile():
    """Everything under /profile is about the logged-in user's own account —
    there's no "viewing someone else's profile" concept here, so just being
    logged in at all is the only requirement."""
    return require_role()


@profile_bp.route("")
def show():
    """
    The logged-in user's own profile: their info, and whether they have a
    pending role-change request.
    ---
    tags:
      - ProfileController
    responses:
      200:
        description: HTML profile page
      302:
        description: Redirect to /login if not logged in
    """
    user = User.get_by_id(session["user_id"])
    return render_template("profile/show.html", user=user, error=request.args.get("error"))


@profile_bp.route("/request-role-change", methods=["POST"])
def request_role_change():
    """
    Ask to switch role (student -> alumni, or the reverse) — becomes
    effective only once a staff member with approve_role_changes approves it.
    ---
    tags:
      - ProfileController
    responses:
      302:
        description: Redirect back to /profile
    """
    user = User.get_by_id(session["user_id"])
    requested_role = "alumni" if user["role"] == "student" else "student"
    User.request_role_change(session["user_id"], requested_role)
    return redirect(url_for("profile.show"))


@profile_bp.route("/delete", methods=["POST"])
def delete_account():
    """
    Delete the logged-in user's own account. Refuses (with a friendly
    message) if they still have job postings, applications, or
    announcements referencing them — same foreign-key safety net as every
    other delete in this app, just surfaced for the owner instead of staff.
    ---
    tags:
      - ProfileController
    responses:
      302:
        description: Redirect home (session cleared) after deleting, or back to /profile with an error
    """
    try:
        User.delete(session["user_id"])
    except psycopg2.errors.ForeignKeyViolation:
        return redirect(url_for(
            "profile.show",
            error="Delete your job postings, applications, and announcements first.",
        ))

    session.clear()
    return redirect(url_for("index"))


@profile_bp.route("/job-postings")
def job_postings():
    """
    The logged-in user's own job postings (any status), with edit/delete
    available regardless of staff_role — ownership is enough.
    ---
    tags:
      - ProfileController
    responses:
      200:
        description: HTML page listing this user's job postings
    """
    return render_template(
        "profile/job_postings.html", job_postings=JobPosting.get_by_user(session["user_id"])
    )


@profile_bp.route("/applications")
def applications():
    """
    The logged-in user's own job applications.
    ---
    tags:
      - ProfileController
    responses:
      200:
        description: HTML page listing this user's applications
    """
    return render_template(
        "profile/applications.html", applications=JobApplication.get_by_user(session["user_id"])
    )


@profile_bp.route("/announcements")
def announcements():
    """
    The logged-in user's own announcements.
    ---
    tags:
      - ProfileController
    responses:
      200:
        description: HTML page listing this user's announcements
    """
    return render_template(
        "profile/announcements.html", announcements=Announcement.get_by_user(session["user_id"])
    )
