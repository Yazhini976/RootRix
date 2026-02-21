import os
from flask import Flask, send_from_directory, render_template, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db
from auth import auth_bp
from admin import admin_bp
from participant import participant_bp
import config as cfg

# Limiter instance (imported by blueprints)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],          # No global limit; we apply per-route
    storage_uri="memory://",
)


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = cfg.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = cfg.SECRET_KEY
    app.config["UPLOAD_FOLDER"] = cfg.UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = cfg.MAX_CONTENT_LENGTH

    # Session config (server-side)
    app.config["SESSION_TYPE"] = "filesystem"

    # Init DB
    db.init_app(app)

    # Init rate limiter
    limiter.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(participant_bp)

    # ── Rate limiting ──
    # Login: 5 attempts/minute, 20/hour per IP
    from auth import login as login_view
    limiter.limit("5 per minute;20 per hour")(login_view)

    # Submit-flag: 10 attempts/minute per IP (prevents flag brute-forcing)
    from participant import submit_flag as submit_flag_view
    limiter.limit("10 per minute")(submit_flag_view)

    # Return clean JSON on rate-limit exceeded (instead of HTML 429 page)
    @app.errorhandler(429)
    def ratelimit_handler(e):
        from flask import jsonify
        return jsonify({
            "error": f"Too many login attempts. Please wait and try again.",
            "retry_after": str(e.description),
        }), 429

    # Serve uploaded files
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Page routes
    @app.route("/")
    def index():
        if "user_id" in session:
            if session.get("role") == "admin":
                return redirect(url_for("admin_page"))
            return redirect(url_for("dashboard_page"))
        return redirect(url_for("login_page"))

    @app.route("/login")
    def login_page():
        if "user_id" in session:
            if session.get("role") == "admin":
                return redirect(url_for("admin_page"))
            return redirect(url_for("dashboard_page"))
        return render_template("login.html")

    @app.route("/admin")
    def admin_page():
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template("admin.html", username=session.get("username"))

    @app.route("/dashboard")
    def dashboard_page():
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        if session.get("role") == "admin":
            return redirect(url_for("admin_page"))
        return render_template("dashboard.html", username=session.get("username"))

    @app.route("/leaderboard")
    def leaderboard_page():
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return render_template("leaderboard.html", username=session.get("username"), role=session.get("role"))

    return app


app = create_app()

if __name__ == "__main__":
    os.makedirs(cfg.UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
