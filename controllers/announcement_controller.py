from flask import Blueprint, redirect, render_template, request, url_for

from middleware.auth import staff_required
from models.announcement import Announcement

announcement_bp = Blueprint("announcement", __name__, url_prefix="/announcements")


@announcement_bp.route("", methods=["GET", "POST"])
def announcements_collection():
    """
    List all announcements as an HTML page, or create a new one from a form.
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
        description: Redirect back to the list after creating an announcement
    """
    if request.method == "POST":
        Announcement.create(
            request.form.get("title"),
            request.form.get("content"),
            request.form.get("date"),
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
      404:
        description: Announcement not found
    """
    announcement = Announcement.get_by_id(announcement_id)
    if announcement is None:
        return render_template("404.html"), 404

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
@staff_required
def delete_announcement(announcement_id):
    """
    Delete an announcement. Requires an admin or moderator session.
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
        description: Logged in but not staff (admin/moderator)
      404:
        description: Announcement not found
    """
    announcement = Announcement.get_by_id(announcement_id)
    if announcement is None:
        return render_template("404.html"), 404

    Announcement.delete(announcement_id)
    return redirect(url_for("announcement.announcements_collection"))
