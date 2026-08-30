import json
import os
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from core.compat import get_resource_path

SCOPES = [
    "https://www.googleapis.com/auth/generative-language.tuning",
    "https://www.googleapis.com/auth/cloud-platform"
]


class GeminiOAuthManager:
    """Manages Google OAuth 2.0 Login, Token Storage, and Auto-Refresh."""

    def __init__(self):
        self.client_secrets_file = get_resource_path("client_secret.json")
        # Token file should be stored in user's working directory or home directory
        self.token_file = Path.cwd() / "gemini_token.json"
        self.credentials: Optional[Credentials] = None

    def get_valid_token(self) -> str:
        """Get an active Access Token, refreshing or prompting browser login if needed."""
        creds = None
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception:
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = self._login_interactive()
            else:
                creds = self._login_interactive()

            # Save token locally
            self.token_file.write_text(creds.to_json(), encoding="utf-8")

        self.credentials = creds
        return creds.token

    def _login_interactive(self) -> Credentials:
        """Launch local browser for Google OAuth Login."""
        secret_path = self.client_secrets_file
        if not secret_path.exists():
            # Check cwd fallback
            secret_path = Path.cwd() / "client_secret.json"
            
        if not secret_path.exists():
            raise FileNotFoundError(
                f"Google OAuth 클라이언트 설정 파일({secret_path.name})이 없습니다.\n"
                "Google Cloud Console에서 생성한 OAuth 2.0 데스크톱 클라이언트 JSON 파일을\n"
                f"'{secret_path.resolve()}' 경로에 넣어주세요."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(secret_path),
            scopes=SCOPES
        )
        creds = flow.run_local_server(port=0, prompt="consent")
        return creds

    def is_logged_in(self) -> bool:
        """Check if a saved token exists and is valid/refreshable."""
        if not self.token_file.exists():
            return False
        try:
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            return creds.valid or (creds.expired and bool(creds.refresh_token))
        except Exception:
            return False
