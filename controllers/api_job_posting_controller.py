from flask import Blueprint, jsonify, request

from middleware.auth import STAFF_ROLES, require_role_api
from models.job_application import JobApplication
from models.job_posting import JobPosting

api_job_posting_bp = Blueprint("api_job_posting", __name__, url_prefix="/api/job-postings")


@api_job_posting_bp.route("", methods=["GET", "POST"])
def job_postings_collection():
    """
    Direct route: list all job postings, or create a new one.
    ---
    tags:
      - ApiJobPostingController
    parameters:
      - name: title
        in: formData
        type: string
      - name: company
        in: formData
        type: string
      - name: description
        in: formData
        type: string
      - name: location
        in: formData
        type: string
      - name: posted_by
        in: formData
        type: integer
      - name: posted_date
        in: formData
        type: string
    responses:
      200:
        description: List of job postings
      201:
        description: Created job posting
      400:
        description: Invalid job posting data (see error message)
      401:
        description: Login required (POST only)
      403:
        description: Logged in but not an alumnus (POST only)
    """
    if request.method == "POST":
        guard = require_role_api("alumni")
        if guard:
            return guard

        errors = JobPosting.validate(request.form.get("title"), request.form.get("company"))
        if errors:
            return jsonify(error=", ".join(errors)), 400

        job_posting = JobPosting.create(
            request.form.get("title"),
            request.form.get("company"),
            request.form.get("description"),
            request.form.get("location"),
            request.form.get("posted_by"),
            request.form.get("posted_date"),
        )
        return jsonify(job_posting), 201

    return jsonify(JobPosting.get_approved())


@api_job_posting_bp.route("/<int:job_posting_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def job_posting_item(job_posting_id):
    """
    Direct route: get, replace, partially update, or delete a job posting by id.
    ---
    tags:
      - ApiJobPostingController
    parameters:
      - name: job_posting_id
        in: path
        type: integer
        required: true
      - name: title
        in: formData
        type: string
      - name: company
        in: formData
        type: string
      - name: description
        in: formData
        type: string
      - name: location
        in: formData
        type: string
      - name: posted_date
        in: formData
        type: string
    responses:
      200:
        description: The job posting (or the updated/deleted version)
      401:
        description: Login required (DELETE only)
      403:
        description: Logged in but not staff (DELETE only)
      404:
        description: Job posting not found
    """
    if request.method == "DELETE":
        guard = require_role_api(*STAFF_ROLES)
        if guard:
            return guard

    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return jsonify(error="Job posting not found"), 404

    if request.method == "GET":
        return jsonify(job_posting)

    if request.method == "PUT":
        updated = JobPosting.update(
            job_posting_id,
            request.form.get("title"),
            request.form.get("company"),
            request.form.get("description"),
            request.form.get("location"),
            request.form.get("posted_date"),
        )
        return jsonify(updated)

    if request.method == "PATCH":
        updated = JobPosting.patch(
            job_posting_id,
            title=request.form.get("title"),
            company=request.form.get("company"),
            description=request.form.get("description"),
            location=request.form.get("location"),
            posted_date=request.form.get("posted_date"),
        )
        return jsonify(updated)

    deleted = JobPosting.delete(job_posting_id)
    return jsonify(deleted)


@api_job_posting_bp.route("/<int:job_posting_id>/applications", methods=["GET", "POST"])
def job_posting_applications(job_posting_id):
    """
    Nested route: list who applied to this job posting, or apply to it.
    ---
    tags:
      - ApiJobPostingController
    parameters:
      - name: job_posting_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: formData
        type: integer
      - name: applied_date
        in: formData
        type: string
    responses:
      200:
        description: List of applicants for this job posting
      201:
        description: Created application
      401:
        description: Login required (POST only)
      404:
        description: Job posting not found
      409:
        description: This user already applied to this job
    """
    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return jsonify(error="Job posting not found"), 404

    if request.method == "POST":
        guard = require_role_api()
        if guard:
            return guard

        application = JobApplication.create(
            request.form.get("user_id"),
            job_posting_id,
            request.form.get("applied_date"),
        )
        if application is None:
            return jsonify(error="This user has already applied to this job"), 409
        return jsonify(application), 201

    return jsonify(JobApplication.get_by_job_posting(job_posting_id))
