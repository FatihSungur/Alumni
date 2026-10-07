from flask import Blueprint, redirect, render_template, request, url_for

from models.user import User

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("", methods=["GET", "POST"])
def users_collection():
    """
    List all alumni records as an HTML page, or create a new one from a form.
    ---
    tags:
      - UserController
    parameters:
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: graduation_year
        in: formData
        type: string
      - name: email
        in: formData
        type: string
    responses:
      200:
        description: HTML page listing alumni records
      302:
        description: Redirect back to the list after creating a record
    """
    if request.method == "POST":
        User.create(
            request.form.get("first_name"),
            request.form.get("last_name"),
            request.form.get("graduation_year"),
            request.form.get("email"),
        )
        return redirect(url_for("user.users_collection"))

    return render_template("users/list.html", users=User.get_all())


@user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """
    Show an edit form for an alumni record, or save the changes.
    ---
    tags:
      - UserController
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: graduation_year
        in: formData
        type: string
      - name: email
        in: formData
        type: string
    responses:
      200:
        description: HTML edit form
      302:
        description: Redirect back to the list after saving
      404:
        description: User not found
    """
    user = User.get_by_id(user_id)
    if user is None:
        return "User not found", 404

    if request.method == "POST":
        User.update(
            user_id,
            request.form.get("first_name"),
            request.form.get("last_name"),
            request.form.get("graduation_year"),
            request.form.get("email"),
        )
        return redirect(url_for("user.users_collection"))

    return render_template("users/edit.html", user=user)


@user_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """
    Delete an alumni record.
    ---
    tags:
      - UserController
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the list after deleting
      404:
        description: User not found
    """
    user = User.get_by_id(user_id)
    if user is None:
        return "User not found", 404

    User.delete(user_id)
    return redirect(url_for("user.users_collection"))
