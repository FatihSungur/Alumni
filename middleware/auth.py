from functools import wraps

from flask import jsonify, redirect, render_template, session, url_for

STAFF_ROLES = ("admin", "moderator")


def _is_authorized(allowed_roles):
    return session.get("role") in allowed_roles or session.get("staff_role") in allowed_roles


def require_role(*allowed_roles):
    """For HTML routes. Call this at the top of a protected branch inside a
    view function. Returns a Flask response to return early with if the
    current session isn't authorized, or None if it's fine to proceed. With
    no arguments, only checks that someone is logged in at all (any role
    passes). Not logged in -> redirects to /login. Logged in with the wrong
    role -> 403.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login", error="Please log in to continue"))

    if allowed_roles and not _is_authorized(allowed_roles):
        return render_template("403.html"), 403

    return None


def require_permission(permission):
    """Call inline, like require_role. An admin always passes (full access,
    nothing to ask). A moderator passes only if granted this specific
    permission (session['permissions'], set at login from
    moderator_permissions — see models/user.py). Anyone else, including a
    plain alumni/student, is forbidden.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login", error="Please log in to continue"))

    if session.get("staff_role") == "admin":
        return None

    if session.get("staff_role") == "moderator" and permission in session.get("permissions", []):
        return None

    return render_template("403.html"), 403


def require_owner_or_staff(owner_id):
    """Call inline, for routes that mutate one specific record (edit/delete a
    job posting, announcement, application...). The record's own
    owner — whoever's id matches owner_id — may act on it, and so may any
    staff member; anyone else is forbidden, even if logged in."""
    if "user_id" not in session:
        return redirect(url_for("auth.login", error="Please log in to continue"))

    if session.get("staff_role") in STAFF_ROLES:
        return None

    if session.get("user_id") == owner_id:
        return None

    return render_template("403.html"), 403


def require_role_api(*allowed_roles):
    """Same idea as require_role, but for JSON API routes: a redirect to an
    HTML login page makes no sense for an API client, so this returns a JSON
    error with 401 (not logged in) or 403 (logged in, wrong role) instead.
    """
    if "user_id" not in session:
        return jsonify(error="Login required"), 401

    if allowed_roles and not _is_authorized(allowed_roles):
        return jsonify(error="You don't have permission to do this"), 403

    return None


def require_owner_or_staff_api(owner_id):
    """Same idea as require_owner_or_staff, but JSON instead of a redirect/page."""
    if "user_id" not in session:
        return jsonify(error="Login required"), 401

    if session.get("staff_role") in STAFF_ROLES:
        return None

    if session.get("user_id") == owner_id:
        return None

    return jsonify(error="You don't have permission to do this"), 403


def login_required(view_func):
    """Decorator for a route that is entirely gated behind login (no public GET)."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        guard = require_role()
        if guard:
            return guard
        return view_func(*args, **kwargs)

    return wrapped


def role_required(*allowed_roles):
    """Decorator factory for a route entirely gated behind specific roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            guard = require_role(*allowed_roles)
            if guard:
                return guard
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


staff_required = role_required(*STAFF_ROLES)
admin_required = role_required("admin")
