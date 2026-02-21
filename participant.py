from datetime import datetime
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError
from models import db, Challenge, Submission, User
from auth import login_required
from admin import _compute_leaderboard

participant_bp = Blueprint("participant", __name__)

POINTS_PENALTY = 5   # Points deducted per additional solver
MIN_POINTS = 10      # Minimum points a solver can earn


def calculate_earned_points(challenge, solve_order):
    """
    solve_order: 1-based index (1 = first solver, 2 = second solver, …)
    Returns: challenge.points - (solve_order - 1) * POINTS_PENALTY, floored at MIN_POINTS
    """
    earned = challenge.points - (solve_order - 1) * POINTS_PENALTY
    return max(earned, MIN_POINTS)


def get_solve_order(challenge_id):
    """Returns how many teams have already correctly solved this challenge (before this moment)."""
    return Submission.query.filter_by(
        challenge_id=challenge_id,
        is_correct=True
    ).count()


@participant_bp.route("/challenges", methods=["GET"])
@login_required
def list_challenges():
    # Participants only see published challenges
    challenges = Challenge.query.filter_by(is_published=True).order_by(Challenge.category, Challenge.created_at).all()
    user_id = session["user_id"]

    result = []
    for c in challenges:
        data = c.to_dict()
        sub = Submission.query.filter_by(user_id=user_id, challenge_id=c.id).first()
        data["user_solved"] = sub.is_correct if sub else False
        data["user_earned_points"] = sub.earned_points if (sub and sub.is_correct) else 0
        result.append(data)
    return jsonify(result)


@participant_bp.route("/submit-flag", methods=["POST"])
@login_required
def submit_flag():
    data = request.get_json(silent=True) or request.form
    challenge_id = data.get("challenge_id")
    submitted_flag = (data.get("submitted_flag") or "").strip()

    if not challenge_id or not submitted_flag:
        return jsonify({"error": "challenge_id and submitted_flag are required"}), 400

    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({"error": "Challenge not found"}), 404

    is_correct = submitted_flag == challenge.correct_flag
    user_id = session["user_id"]

    existing = Submission.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()

    earned = 0
    if existing:
        # Already solved correctly — don't allow re-submission
        if existing.is_correct:
            return jsonify({
                "correct": True,
                "message": f"✅ Already solved! You earned {existing.earned_points} pts.",
                "solved_count": challenge.solved_count(),
                "earned_points": existing.earned_points,
            })
        # Wrong → new attempt
        if is_correct:
            # Calculate solve order BEFORE this commit (existing teams who solved correctly)
            solve_order = get_solve_order(challenge_id) + 1  # +1 because this team is next
            earned = calculate_earned_points(challenge, solve_order)

        existing.submitted_flag = submitted_flag
        existing.is_correct = is_correct
        existing.earned_points = earned if is_correct else 0
        existing.submitted_at = datetime.utcnow()
        db.session.commit()
    else:
        if is_correct:
            solve_order = get_solve_order(challenge_id) + 1
            earned = calculate_earned_points(challenge, solve_order)

        new_sub = Submission(
            user_id=user_id,
            challenge_id=challenge_id,
            submitted_flag=submitted_flag,
            is_correct=is_correct,
            earned_points=earned if is_correct else 0,
        )
        db.session.add(new_sub)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Submission error"}), 500

    if is_correct:
        solve_order_display = challenge.solved_count()  # now includes this solve
        msg = f"✅ Correct Flag! You earned {earned} pts (#{solve_order_display} to solve)"
    else:
        msg = "❌ Wrong Flag! Try again."

    return jsonify({
        "correct": is_correct,
        "message": msg,
        "solved_count": challenge.solved_count(),
        "earned_points": earned,
    })


@participant_bp.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    from admin import get_setting, _compute_leaderboard
    # Admin always bypasses the visibility check
    if session.get("role") != "admin":
        visible = get_setting("leaderboard_visible", "false") == "true"
        if not visible:
            return jsonify({"hidden": True, "message": "🔒 Leaderboard is not available yet. Please wait for the admin to release it."}), 403
    rows = _compute_leaderboard()
    return jsonify(rows)
