from dotenv import load_dotenv
from flask import Flask, Response, jsonify
from flask_cors import CORS


def create_app() -> Flask:
    """Application factory for the Flask web application."""
    load_dotenv()

    app = Flask(__name__)

    # Configure CORS to allow communication with the frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.errorhandler(404)
    def resource_not_found(_e: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(_e: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/health")
    def health_check() -> tuple[Response, int]:
        return jsonify({"status": "healthy", "service": "backend"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
