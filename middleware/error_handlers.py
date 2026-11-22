import logging
import os
import traceback

from flask import render_template, request
from werkzeug.exceptions import HTTPException

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "error.log")

os.makedirs(LOG_DIR, exist_ok=True)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
_file_handler = logging.FileHandler(LOG_FILE)
_file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
error_logger.addHandler(_file_handler)


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(Exception)
    def handle_server_error(error):
        if isinstance(error, HTTPException):
            return error

        error_logger.error(
            "%s %s -> unhandled exception\n%s",
            request.method,
            request.path,
            traceback.format_exc(),
        )
        return "Something went wrong on our end. Please try again later.", 500
