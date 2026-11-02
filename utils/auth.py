from utils.supabase_client import get_supabase_client


def sign_up(email, password, display_name):
    """Register a new BookFlix reader."""

    supabase = get_supabase_client()

    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "display_name": display_name
            }
        }
    })

    return response


def sign_in(email, password):
    """Sign in an existing BookFlix reader."""

    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    return response


def sign_out():
    """Sign out the current reader."""

    supabase = get_supabase_client()
    supabase.auth.sign_out()