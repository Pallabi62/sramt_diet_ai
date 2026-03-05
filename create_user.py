from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    existing_user = User.query.filter_by(username='playwright_test').first()
    if not existing_user:
        hashed_password = generate_password_hash('password123')
        new_user = User(username='playwright_test', email='playwright@test.com', password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print("User created.")
    else:
        print("User already exists.")
