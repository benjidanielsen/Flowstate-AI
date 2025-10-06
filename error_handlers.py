"""
Error handlers for the Flowstate-AI unified dashboard.
Provides generic error messages to prevent information leakage.
"""

from flask import jsonify, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register custom error handlers with the Flask app."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.error(f"400 Bad Request: {error}")
        return jsonify({"error": "Bad request. Please check your input and try again."}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        logger.error(f"401 Unauthorized: {error}")
        return jsonify({"error": "Unauthorized. Please log in to access this resource."}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        logger.error(f"403 Forbidden: {error}")
        return jsonify({"error": "Forbidden. You do not have permission to access this resource."}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.error(f"404 Not Found: {error}")
        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>404 - Page Not Found</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; text-align: center; }
                    .error-container { background: rgba(255,255,255,0.1); padding: 60px 40px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
                    .error-container h1 { font-size: 6em; margin: 0; }
                    .error-container h2 { font-size: 2em; margin: 20px 0; }
                    .error-container p { font-size: 1.2em; margin: 20px 0; }
                    .error-container a { color: #28a745; text-decoration: none; font-weight: bold; }
                    .error-container a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>404</h1>
                    <h2>Page Not Found</h2>
                    <p>The page you are looking for does not exist.</p>
                    <p><a href="/">Return to Dashboard</a></p>
                </div>
            </body>
            </html>
        """), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"500 Internal Server Error: {error}", exc_info=True)
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
