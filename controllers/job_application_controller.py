from flask import Blueprint, redirect, render_template, request, url_for

from models.job_application import JobApplication

job_application_bp = Blueprint("job_application", __name__, url_prefix="/applications")


@job_application_bp.route("", methods=["GET", "POST"])
def job_applications_collection():
    """
    List all job applications as an HTML page, or create a new one from a form.
    ---
    tags:
      - JobApplicationController
    parameters:
      - name: user_id
        in: formData
        type: integer
      - name: job_posting_id
        in: formData
        type: integer
      - name: applied_date
        in: formData
        type: string
    responses:
      200:
        description: HTML page listing job applications
      302:
        description: Redirect back to the list after creating an application
      409:
        description: This user already applied to this job
    """
    if request.method == "POST":
        application = JobApplication.create(
            request.form.get("user_id"),
            request.form.get("job_posting_id"),
            request.form.get("applied_date"),
        )
        if application is None:
            return "This user has already applied to this job. Go back and try again.", 409
        return redirect(url_for("job_application.job_applications_collection"))

    return render_template(
        "job_applications/list.html", applications=JobApplication.get_all()
    )


@job_application_bp.route("/<int:application_id>/delete", methods=["POST"])
def delete_job_application(application_id):
    """
    Delete a job application.
    ---
    tags:
      - JobApplicationController
    parameters:
      - name: application_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the list after deleting
      404:
        description: Application not found
    """
    application = JobApplication.get_by_id(application_id)
    if application is None:
        return "Application not found", 404

    JobApplication.delete(application_id)
    return redirect(url_for("job_application.job_applications_collection"))
