# import firebase_admin
# from firebase_admin import credentials, auth
# from backend.core.config import settings

# Initialize Firebase (Uncomment when credentials are provided)
# cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
# firebase_admin.initialize_app(cred)

def verify_token(token: str):
    # Placeholder for Firebase token verification
    # return auth.verify_id_token(token)
    return {"uid": "mock-user-id"}
