import os


class SupabaseConfigError(RuntimeError):
    """Raised when Supabase configuration is missing."""


def get_supabase_config_errors():
    errors = []

    if not os.getenv("SUPABASE_URL"):
        errors.append("SUPABASE_URL is not set.")

    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        errors.append("SUPABASE_SERVICE_ROLE_KEY is not set.")

    return errors


def is_supabase_configured():
    return not get_supabase_config_errors()


def create_supabase_client():
    errors = get_supabase_config_errors()
    if errors:
        raise SupabaseConfigError(" ".join(errors))

    from supabase import create_client

    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )
