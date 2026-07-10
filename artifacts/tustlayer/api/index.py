import sys
import os
import traceback

error_traceback = None
app = None

try:
    # Safely get current file path with NameError fallback
    try:
        current_file = __file__
    except NameError:
        current_file = os.path.join(os.getcwd(), "api", "index.py")
        
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(current_file)))
    if project_root not in sys.path:
        sys.path.append(project_root)
        
    from backend.main import app as real_app
    
    class VercelPathMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                headers = dict(scope.get("headers", []))
                matched_path = headers.get(b"x-vercel-forwarded-path", b"").decode("utf-8")
                if not matched_path:
                    matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
                if matched_path:
                    scope["path"] = matched_path.split("?")[0]
            await self.app(scope, receive, send)

    app = VercelPathMiddleware(real_app)
except Exception as e:
    error_traceback = traceback.format_exc()
    print(f"Error on startup: {error_traceback}")

if app is None:
    # Pure Python ASGI fallback app to diagnose errors without any external dependencies (like FastAPI)
    async def fallback_app(scope, receive, send):
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [
                    (b'content-type', b'text/html; charset=utf-8'),
                ]
            })
            
            html_content = f"""
            <html>
            <head>
                <title>TrustLayer AI - Startup Diagnosis</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 2rem; }}
                    h1 {{ color: #f43f5e; }}
                    pre {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; overflow-x: auto; color: #fda4af; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.5; }}
                </style>
            </head>
            <body>
                <h1>TrustLayer AI - Startup Diagnosis Report</h1>
                <p>An exception occurred during module import / startup initialization on Vercel:</p>
                <pre>{error_traceback}</pre>
            </body>
            </html>
            """
            await send({
                'type': 'http.response.body',
                'body': html_content.encode('utf-8'),
            })
            
    app = fallback_app
