from flask import Blueprint, redirect, render_template, request, url_for

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
        description: Redirect back to the list after creating a job posting
    """
    if request.method == "POST":
        JobPosting.create(
            request.form.get("title"),
            request.form.get("company"),
            request.form.get("description"),
            request.form.get("location"),
            request.form.get("posted_by"),
            request.form.get("posted_date"),
        )
        return redirect(url_for("job_posting.job_postings_collection"))

    return render_template("job_postings/list.html", job_postings=JobPosting.get_all())


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
      404:
        description: Job posting not found
    """
    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return "Job posting not found", 404

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
    Delete a job posting.
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
      404:
        description: Job posting not found
    """
    job_posting = JobPosting.get_by_id(job_posting_id)
    if job_posting is None:
        return "Job posting not found", 404

    JobPosting.delete(job_posting_id)
    return redirect(url_for("job_posting.job_postings_collection"))
