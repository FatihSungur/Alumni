from flask import Blueprint, jsonify, request

from models.announcement import Announcement

api_announcement_bp = Blueprint(
    "api_announcement", __name__, url_prefix="/api/announcements"
)


@api_announcement_bp.route("", methods=["GET", "POST"])
def announcements_collection():
    """
    List all announcements, or create a new one.
    ---
    tags:
      - ApiAnnouncementController
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
        description: List of announcements
      201:
        description: Created announcement
    """
    if request.method == "POST":
        announcement = Announcement.create(
            request.form.get("title"),
            request.form.get("content"),
            request.form.get("date"),
        )
        return jsonify(announcement), 201

    return jsonify(Announcement.get_all())


@api_announcement_bp.route("/<int:announcement_id>", methods=["PUT", "PATCH", "DELETE"])
def announcement_item(announcement_id):
    """
    Replace, partially update, or delete an announcement by id.
    ---
    tags:
      - ApiAnnouncementController
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
        description: Updated or deleted announcement
      404:
        description: Announcement not found
    """
    announcement = Announcement.get_by_id(announcement_id)
    if announcement is None:
        return jsonify(error="Announcement not found"), 404

    if request.method == "PUT":
        updated_announcement = Announcement.update(
            announcement_id,
            request.form.get("title"),
            request.form.get("content"),
            request.form.get("date"),
        )
        return jsonify(updated_announcement)

    if request.method == "PATCH":
        updated_announcement = Announcement.patch(
            announcement_id,
            title=request.form.get("title"),
            content=request.form.get("content"),
            date=request.form.get("date"),
        )
        return jsonify(updated_announcement)

    deleted_announcement = Announcement.delete(announcement_id)
    return jsonify(deleted_announcement)
