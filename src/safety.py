
import os

def _load_credential_from_file(filepath):
    real_path = os.path.abspath(filepath)
    with open(real_path, "rb") as f:
        return f.read()


SERVER_CERTIFICATE = _load_credential_from_file("assets/credentials/localhost.crt")
SERVER_CERTIFICATE_KEY = _load_credential_from_file("assets/credentials/localhost.key")
ROOT_CERTIFICATE = _load_credential_from_file("assets/credentials/root.crt")
