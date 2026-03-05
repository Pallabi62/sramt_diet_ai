from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, DietPlan
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from utils import calculate_calories, generate_meal_plan
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key_change_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_diet_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize the database with the app
db.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = db.session.get(User, session['user_id'])
    
    # Handle User Profile Updates (Height, Weight, Goal)
    if request.method == 'POST':
        try:
            user.height = float(request.form['height'])
            user.weight = float(request.form['weight'])
            user.age = int(request.form['age'])
            user.gender = request.form['gender']
            user.activity_level = request.form['activity_level']
            user.goal = request.form['goal']
            
            db.session.commit()
            
            # Recalculate and Save Diet Plan
            bmr, tdee, target_calories = calculate_calories(
                user.height, user.weight, user.age, user.gender, user.activity_level, user.goal
            )
            
            meal_plan = generate_meal_plan(target_calories)
            
            # Save new diet plan
            new_plan = DietPlan(
                user_id=user.id,
                bmr=bmr,
                tdee=tdee,
                target_calories=target_calories,
                meal_plan_data=json.dumps(meal_plan)
            )
            db.session.add(new_plan)
            db.session.commit()
            
            flash('Profile updated and new diet plan generated!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    # Get latest diet plan
    latest_plan = DietPlan.query.filter_by(user_id=user.id).order_by(DietPlan.created_at.desc()).first()
    plan_data = json.loads(latest_plan.meal_plan_data) if latest_plan else None
    
    return render_template('dashboard.html', user=user, plan=latest_plan, meal_plan=plan_data)

@app.route('/scanner', methods=['GET', 'POST'])
def scanner():
    if 'user_id' not in session:
        flash('Please login to use the scanner.', 'warning')
        return redirect(url_for('login'))
        
    result = None
    image_url = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'No file selected'}), 400
            flash('No file selected', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'No file selected'}), 400
            flash('No file selected', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
            # Save to static/uploads folder instead
            static_upload_folder = os.path.join('static', 'uploads')
            if not os.path.exists(static_upload_folder):
                os.makedirs(static_upload_folder)
                
            filepath = os.path.join(static_upload_folder, filename)
            file.save(filepath)
            
            # Correct URL for static folder
            image_url = url_for('static', filename=f'uploads/{filename}')
            
            # --- IMPROVED AI LOGIC with food detection ---
            # You can integrate a real AI service here like Google Vision API, Clarifai, etc.
            # For now, let's make it slightly smarter based on filename
            filename_lower = filename.lower()
            
            # Simple keyword-based detection
            if 'chicken' in filename_lower or 'grill' in filename_lower:
                result = {"name": "Grilled Chicken", "calories": 350, "fat": 12, "protein": 35, "carbs": 5}
            elif 'salad' in filename_lower:
                result = {"name": "Fresh Salad", "calories": 150, "fat": 8, "protein": 5, "carbs": 15}
            elif 'burger' in filename_lower:
                result = {"name": "Hamburger", "calories": 550, "fat": 28, "protein": 25, "carbs": 45}
            elif 'pizza' in filename_lower:
                result = {"name": "Pizza Slice", "calories": 300, "fat": 12, "protein": 12, "carbs": 38}
            elif 'apple' in filename_lower or 'fruit' in filename_lower:
                result = {"name": "Fresh Apple", "calories": 95, "fat": 0.3, "protein": 0.5, "carbs": 25}
            else:
                # Default random selection
                import random
                mock_foods = [
                    {"name": "Grilled Chicken Salad", "calories": 450, "fat": 15, "protein": 40, "carbs": 10},
                    {"name": "Cheeseburger", "calories": 600, "fat": 30, "protein": 25, "carbs": 45},
                    {"name": "Apple", "calories": 95, "fat": 0.3, "protein": 0.5, "carbs": 25},
                    {"name": "Pizza Slice", "calories": 285, "fat": 10, "protein": 12, "carbs": 36},
                    {"name": "Salmon with Vegetables", "calories": 550, "fat": 25, "protein": 35, "carbs": 15},
                    {"name": "Greek Yogurt with Berries", "calories": 200, "fat": 5, "protein": 15, "carbs": 25}
                ]
                result = random.choice(mock_foods)
            
            flash('Image processed successfully!', 'success')

            # If the request accepts JSON, return JSON instead of rendering the template
            if request.headers.get('Accept') == 'application/json':
                import time
                time.sleep(1)  # Simulate analysis delay
                return jsonify({'result': result, 'image_url': image_url})
        else:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
            flash('Invalid file type. Please upload an image.', 'danger')
            
    return render_template('scanner.html', result=result, image_url=image_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    app.run(debug=True, port=5000)