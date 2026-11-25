from functools import wraps

from flask import jsonify, redirect, session, url_for

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
        return "Forbidden: you don't have permission to do this", 403

    return None


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
