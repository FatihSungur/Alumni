from flask import Blueprint, jsonify, request

from middleware.auth import require_owner_or_staff_api
from models.job_application import JobApplication

api_job_application_bp = Blueprint(
    "api_job_application", __name__, url_prefix="/api/applications"
)


@api_job_application_bp.route("", methods=["GET"])
def applications_collection():
    """
    Direct route: list every job application in the system.
    ---
    tags:
      - ApiJobApplicationController
    responses:
      200:
        description: List of all applications
    """
    return jsonify(JobApplication.get_all())


@api_job_application_bp.route("/<int:application_id>", methods=["GET", "DELETE"])
def application_item(application_id):
    """
    Direct route: get or delete a single job application by id.
    ---
    tags:
      - ApiJobApplicationController
    parameters:
      - name: application_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The application (or the deleted version)
      401:
        description: Login required (DELETE only)
      403:
        description: Logged in but neither the applicant nor staff (DELETE only)
      404:
        description: Application not found
    """
    application = JobApplication.get_by_id(application_id)
    if application is None:
        return jsonify(error="Application not found"), 404

    if request.method == "DELETE":
        guard = require_owner_or_staff_api(application["user_id"])
        if guard:
            return guard

        deleted = JobApplication.delete(application_id)
        return jsonify(deleted)

    return jsonify(application)
