from flask import Blueprint, redirect, render_template, request, session, url_for

from middleware.auth import require_owner_or_staff, require_role
from models.announcement import Announcement

announcement_bp = Blueprint("announcement", __name__, url_prefix="/announcements")


@announcement_bp.route("", methods=["GET", "POST"])
def announcements_collection():
    """
    List all announcements as an HTML page, or create a new one from a form.
    Creating requires a login session, so every announcement has a known
    creator (see DDD.md — needed for "my announcements").
    ---
    tags:
      - AnnouncementController
    parameters:
      - name: title
        in: formData
        type: string
      - name: content
        in: formData
        type: string
      - name: date
        in: formData
        type: string
    responses:
      200:
        description: HTML page listing announcements
      302:
        description: Redirect back to the list after creating an announcement, or to /login if not logged in
    """
    if request.method == "POST":
        guard = require_role()
        if guard:
            return guard

        Announcement.create(
            request.form.get("title"),
            request.form.get("content"),
            request.form.get("date"),
            session["user_id"],
        )
        return redirect(url_for(
            "announcement.announcements_collection",
            error="Announcement submitted. It will appear once approved by staff.",
        ))

    return render_template(
        "announcements/list.html",
        announcements=Announcement.get_approved(),
        error=request.args.get("error"),
    )


@announcement_bp.route("/<int:announcement_id>/edit", methods=["GET", "POST"])
def edit_announcement(announcement_id):
    """
    Show an edit form for an announcement, or save the changes.
    ---
    tags:
      - AnnouncementController
    parameters:
      - name: announcement_id
        in: path
        type: integer
        required: true
      - name: title
        in: formData
        type: string
      - name: content
        in: formData
        type: string
      - name: date
        in: formData
        type: string
    responses:
      200:
        description: HTML edit form
      302:
        description: Redirect back to the list after saving
      403:
        description: Logged in but neither the creator nor staff
      404:
        description: Announcement not found
    """
    announcement = Announcement.get_by_id(announcement_id)
    if announcement is None:
        return render_template("404.html"), 404

    guard = require_owner_or_staff(announcement["created_by"])
    if guard:
        return guard

    if request.method == "POST":
        Announcement.update(
            announcement_id,
            request.form.get("title"),
            request.form.get("content"),
            request.form.get("date"),
        )
        return redirect(url_for("announcement.announcements_collection"))

    return render_template("announcements/edit.html", announcement=announcement)


@announcement_bp.route("/<int:announcement_id>/delete", methods=["POST"])
def delete_announcement(announcement_id):
    """
    Delete an announcement. Requires being its creator, or staff.
    ---
    tags:
      - AnnouncementController
    parameters:
      - name: announcement_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the list after deleting
      403:
        description: Logged in but neither the creator nor staff
      404:
        description: Announcement not found
    """
    announcement = Announcement.get_by_id(announcement_id)
    if announcement is None:
        return render_template("404.html"), 404

    guard = require_owner_or_staff(announcement["created_by"])
    if guard:
        return guard

    Announcement.delete(announcement_id)
    return redirect(url_for("announcement.announcements_collection"))
