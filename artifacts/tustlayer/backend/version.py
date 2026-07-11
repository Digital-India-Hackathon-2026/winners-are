from datetime import datetime, timezone

# Dynamically set on import/startup
DEPLOYED_AT = datetime.now(timezone.utc).isoformat()
GIT_COMMIT = "1daf5d8"
GIT_BRANCH = "main"
