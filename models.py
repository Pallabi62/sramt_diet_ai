from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    
    # Physical Attributes for Diet Calculation
    height = Column(Float) # in cm
    weight = Column(Float) # in kg
    age = Column(Integer)
    gender = Column(String(10)) # 'male' or 'female'
    activity_level = Column(String(20)) # sedentary, light, moderate, active, very_active
    goal = Column(String(20)) # lose, maintain, gain
    
    # Relationships
    diet_plans = relationship('DietPlan', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class DietPlan(db.Model):
    __tablename__ = 'diet_plans'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Calculated Results
    bmr = Column(Float)
    tdee = Column(Float)
    target_calories = Column(Integer)
    
    # Storing the plan as JSON/Text since it's a generated list of meals
    # In a real app, this might be a separate table 'Meals', but for this scope, a JSON dump is efficient.
    meal_plan_data = Column(Text, nullable=False) 
    
    def __repr__(self):
        return f'<DietPlan {self.id} for User {self.user_id}>'
