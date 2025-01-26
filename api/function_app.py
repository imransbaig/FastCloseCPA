import azure.functions as func
from app import app

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Azure Functions handler that wraps our Flask app.
    This function serves as the main entry point for all API requests.
    """
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

# Ensure Flask app is configured for Azure Functions
app.config['SERVER_NAME'] = None
app.config['PREFERRED_URL_SCHEME'] = 'https'