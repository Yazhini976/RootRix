import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db, Challenge, Submission, User
from auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "zip", "txt", "pcap", "docx", "mp3", "mp4", "wav", "bmp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route("/challenges", methods=["POST"])
@admin_required
def create_challenge():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip().lower()
    description = request.form.get("description", "").strip()
    resource_type = request.form.get("resource_type", "").strip().lower()
    correct_flag = request.form.get("correct_flag", "").strip()
    points = request.form.get("points", 100)

    if not title or not category or not correct_flag:
        return jsonify({"error": "Title, category, and correct_flag are required"}), 400

    try:
        points = int(points)
    except ValueError:
        points = 100

    resource_path = None

    if resource_type == "link":
        resource_path = request.form.get("resource_link", "").strip()
    elif resource_type == "file":
        file = request.files.get("resource_file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            upload_dir = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, unique_name))
            resource_path = f"/uploads/{unique_name}"
        else:
            return jsonify({"error": "Invalid or missing file"}), 400

    challenge = Challenge(
        title=title,
        category=category,
        description=description,
        resource_type=resource_type,
        resource_path=resource_path,
        correct_flag=correct_flag,
        points=points,
    )
    db.session.add(challenge)
    db.session.commit()

    return jsonify({"message": "Challenge created", "challenge": challenge.to_dict(include_flag=True)}), 201


@admin_bp.route("/challenges", methods=["GET"])
@admin_required
def list_challenges():
    challenges = Challenge.query.order_by(Challenge.category, Challenge.created_at).all()
    return jsonify([c.to_dict(include_flag=True) for c in challenges])


@admin_bp.route("/challenges/<int:challenge_id>", methods=["DELETE"])
@admin_required
def delete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    Submission.query.filter_by(challenge_id=challenge_id).delete()
    db.session.delete(challenge)
    db.session.commit()
    return jsonify({"message": "Challenge deleted"})


@admin_bp.route("/challenges/<int:challenge_id>/publish", methods=["POST"])
@admin_required
def toggle_publish(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    data = request.get_json(silent=True) or {}
    # Accept explicit true/false, or just toggle
    if "publish" in data:
        challenge.is_published = bool(data["publish"])
    else:
        challenge.is_published = not challenge.is_published
    db.session.commit()
    status = "published" if challenge.is_published else "unpublished"
    return jsonify({"message": f"Challenge {status}", "is_published": challenge.is_published})


@admin_bp.route("/submissions", methods=["GET"])
@admin_required
def list_submissions():
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    return jsonify([s.to_dict() for s in submissions])


@admin_bp.route("/leaderboard", methods=["GET"])
@admin_required
def leaderboard():
    # Always use _compute_leaderboard() so it reflects earned_points (dynamic scoring)
    # The PostgreSQL leaderboard VIEW uses SUM(c.points) which ignores dynamic scoring
    rows = _compute_leaderboard()
    return jsonify(rows)


def _compute_leaderboard():
    users = User.query.filter_by(role="participant").all()
    data = []
    for u in users:
        correct_subs = Submission.query.filter_by(user_id=u.id, is_correct=True).all()
        solved_count = len(correct_subs)
        # Use earned_points stored at submission time (reflects dynamic scoring)
        total_points = sum(s.earned_points for s in correct_subs)
        data.append({"username": u.username, "solved_count": solved_count, "total_points": total_points})
    return sorted(data, key=lambda x: (-x["total_points"], -x["solved_count"]))


# ── Global Settings Helpers ──────────────────────────────────────
def get_setting(key: str, default: str = "false") -> str:
    row = db.session.execute(
        db.text("SELECT value FROM settings WHERE key = :k"), {"k": key}
    ).fetchone()
    return row[0] if row else default


def set_setting(key: str, value: str):
    db.session.execute(
        db.text("""
            INSERT INTO settings (key, value) VALUES (:k, :v)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """),
        {"k": key, "v": value},
    )
    db.session.commit()


@admin_bp.route("/settings", methods=["GET"])
@admin_required
def get_settings():
    lb_visible = get_setting("leaderboard_visible", "false") == "true"
    return jsonify({"leaderboard_visible": lb_visible})


@admin_bp.route("/settings/leaderboard-visible", methods=["POST"])
@admin_required
def toggle_leaderboard_visibility():
    data = request.get_json(silent=True) or {}
    if "visible" in data:
        new_val = "true" if data["visible"] else "false"
    else:
        current = get_setting("leaderboard_visible", "false")
        new_val = "false" if current == "true" else "true"
    set_setting("leaderboard_visible", new_val)
    is_visible = new_val == "true"
    status = "visible" if is_visible else "hidden"
    return jsonify({"message": f"Leaderboard is now {status} to participants", "leaderboard_visible": is_visible})
