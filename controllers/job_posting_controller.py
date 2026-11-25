from flask import Blueprint, redirect, render_template, request, url_for

from middleware.auth import require_owner_or_staff, require_role
from models.job_posting import JobPosting

job_posting_bp = Blueprint("job_posting", __name__, url_prefix="/job-postings")


@job_posting_bp.route("", methods=["GET", "POST"])
def job_postings_collection():
    """
    List all job postings as an HTML page, or create a new one from a form.
    ---
    tags:
      - JobPostingController
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
        description: HTML page listing job postings
      302:
        description: Redirect back to the list after creating a job posting, or back with an error if the data is invalid
      403:
        description: Logged in but not an alumnus (only alumni can create job postings)
    """
    if request.method == "POST":
        guard = require_role("alumni")
        if guard:
            return guard

        errors = JobPosting.validate(request.form.get("title"), request.form.get("company"))
        if errors:
            return redirect(url_for("job_posting.job_postings_collection", error=", ".join(errors)))

        JobPosting.create(
            request.form.get("title"),
            request.form.get("company"),
            request.form.get("description"),
            request.form.get("location"),
            request.form.get("posted_by"),
            request.form.get("posted_date"),
        )
        return redirect(url_for(
            "job_posting.job_postings_collection",
            error="Job posting submitted. It will appear once approved by staff.",
        ))

    return render_template(
        "job_postings/list.html",
        job_postings=JobPosting.get_approved(),
        error=request.args.get("error"),
    )


@job_posting_bp.route("/<int:job_posting_id>/edit", methods=["GET", "POST"])
def edit_job_posting(job_posting_id):
    """
    Show an edit form for a job posting, or save the changes.
    ---
    tags:
      - JobPostingController
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
        description: HTML edit form
      302:
        description: Redirect back to the list after saving
      403:
        description: Logged in but neither the poster nor staff
      404:
        description: Job posting not found
    """
    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return render_template("404.html"), 404

    guard = require_owner_or_staff(job_posting["posted_by"])
    if guard:
        return guard

    if request.method == "POST":
        JobPosting.update(
            job_posting_id,
            request.form.get("title"),
            request.form.get("company"),
            request.form.get("description"),
            request.form.get("location"),
            request.form.get("posted_date"),
        )
        return redirect(url_for("job_posting.job_postings_collection"))

    return render_template("job_postings/edit.html", job_posting=job_posting)


@job_posting_bp.route("/<int:job_posting_id>/delete", methods=["POST"])
def delete_job_posting(job_posting_id):
    """
    Delete a job posting. Requires being its poster, or staff.
    ---
    tags:
      - JobPostingController
    parameters:
      - name: job_posting_id
        in: path
        type: integer
        required: true
    responses:
      302:
        description: Redirect back to the list after deleting
      403:
        description: Logged in but neither the poster nor staff
      404:
        description: Job posting not found
    """
    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return render_template("404.html"), 404

    guard = require_owner_or_staff(job_posting["posted_by"])
    if guard:
        return guard

    JobPosting.delete(job_posting_id)
    return redirect(url_for("job_posting.job_postings_collection"))
