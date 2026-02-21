import sys
sys.path.insert(0, '.')
from app import create_app
app = create_app()
with app.app_context():
    from models import db, Challenge
    c = Challenge(title='Test', category='welcome', correct_flag='flag{test}', points=10, is_published=False)
    db.session.add(c)
    try:
        db.session.commit()
        print('Success! Challenge created with id', c.id)
        db.session.delete(c)
        db.session.commit()
        print('Cleaned up.')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
