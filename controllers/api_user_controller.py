from flask import Blueprint, jsonify, request

from models.user import User

api_user_bp = Blueprint("api_user", __name__, url_prefix="/api/users")


@api_user_bp.route("", methods=["GET", "POST"])
def users_collection():
    """
    List all alumni records, or create a new one.
    ---
    tags:
      - ApiUserController
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
        description: List of alumni records
      201:
        description: Created alumni record
    """
    if request.method == "POST":
        user = User.create(
            request.form.get("first_name"),
            request.form.get("last_name"),
            request.form.get("graduation_year"),
            request.form.get("email"),
        )
        return jsonify(user), 201

    return jsonify(User.get_all())


@api_user_bp.route("/<int:user_id>", methods=["PUT", "PATCH", "DELETE"])
def user_item(user_id):
    """
    Replace, partially update, or delete an alumni record by id.
    ---
    tags:
      - ApiUserController
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
        description: Updated or deleted alumni record
      404:
        description: User not found
    """
    user = User.get_by_id(user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    if request.method == "PUT":
        updated_user = User.update(
            user_id,
            request.form.get("first_name"),
            request.form.get("last_name"),
            request.form.get("graduation_year"),
            request.form.get("email"),
        )
        return jsonify(updated_user)

    if request.method == "PATCH":
        updated_user = User.patch(
            user_id,
            first_name=request.form.get("first_name"),
            last_name=request.form.get("last_name"),
            graduation_year=request.form.get("graduation_year"),
            email=request.form.get("email"),
        )
        return jsonify(updated_user)

    deleted_user = User.delete(user_id)
    return jsonify(deleted_user)
