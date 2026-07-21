import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv  # noqa: E402
from flask import Flask, Response, jsonify  # noqa: E402
from flask_cors import CORS  # noqa: E402

from src.infrastructure.db.migrator import init_db_and_seed  # noqa: E402
from src.infrastructure.db.session import init_app_db  # noqa: E402
from src.presentation.routes.auth_routes import auth_bp  # noqa: E402
from src.presentation.routes.disbursement_routes import disbursement_bp  # noqa: E402
from src.presentation.routes.onboarding_routes import onboarding_bp  # noqa: E402
from src.presentation.routes.sales_routes import sales_bp  # noqa: E402


def create_app() -> Flask:
    """Application factory for the Flask web application."""
    load_dotenv()

    _app = Flask(__name__)

    # Initialize DB session and DI Container lifecycle hooks
    init_app_db(_app)

    # Configure CORS to allow communication with the frontend
    CORS(_app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    _app.register_blueprint(auth_bp)
    _app.register_blueprint(onboarding_bp)
    _app.register_blueprint(sales_bp)
    _app.register_blueprint(disbursement_bp)

    @_app.errorhandler(404)
    def resource_not_found(_e: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Resource not found"}), 404

    @_app.errorhandler(500)
    def internal_server_error(e: Exception) -> tuple[Response, int]:
        return jsonify({"error": f"Internal server error: {e}"}), 500

    @_app.route("/health")
    def health_check() -> tuple[Response, int]:
        return jsonify({"status": "healthy", "service": "backend"}), 200

    # Execute DB migrations & default admin seeding on app startup
    try:
        init_db_and_seed()
    except Exception as err:
        _app.logger.warning(f"DB migration auto-check encountered: {err}")

    return _app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
