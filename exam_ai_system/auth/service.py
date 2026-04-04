class AuthService:
    def __init__(self, client_factory):
        self.client_factory = client_factory

    def create_user(self, email, password, display_name):
        normalized_email = (email or "").strip().lower()
        cleaned_display_name = (display_name or "").strip()

        if not normalized_email:
            raise ValueError("Email is required.")

        if not cleaned_display_name:
            raise ValueError("Display name is required.")

        if len(password or "") < 8:
            raise ValueError("Password must be at least 8 characters long.")

        client = self.client_factory()
        try:
            response = client.auth.admin.create_user(
                {
                    "email": normalized_email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"display_name": cleaned_display_name},
                }
            )
        except Exception as exc:
            message = str(exc).lower()
            if "already" in message and "registered" in message:
                raise ValueError("That email is already registered.") from exc
            raise ValueError("Unable to create the account right now.") from exc

        user = getattr(response, "user", None) or getattr(response, "data", None)
        if not user:
            raise ValueError("Unable to create the account right now.")

        return {
            "id": getattr(user, "id"),
            "email": getattr(user, "email", normalized_email),
            "display_name": getattr(user, "user_metadata", {}).get(
                "display_name",
                cleaned_display_name,
            ),
        }

    def authenticate_user(self, email, password):
        normalized_email = (email or "").strip().lower()

        if not normalized_email or not password:
            return None

        client = self.client_factory()
        try:
            response = client.auth.sign_in_with_password(
                {
                    "email": normalized_email,
                    "password": password,
                }
            )
        except Exception:
            return None

        user = getattr(response, "user", None)
        if user is None:
            data = getattr(response, "data", None)
            user = getattr(data, "user", None) if data is not None else None

        if not user:
            return None

        metadata = getattr(user, "user_metadata", {}) or {}

        return {
            "id": getattr(user, "id"),
            "email": getattr(user, "email", normalized_email),
            "display_name": metadata.get("display_name") or normalized_email,
        }
