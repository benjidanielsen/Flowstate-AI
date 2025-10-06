from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

lead_capture_bp = Blueprint('lead_capture', __name__)
db = SQLAlchemy()

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Lead {self.email}>'

# Simple email regex for validation
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$")

@lead_capture_bp.route('/capture', methods=['POST'])
def capture_lead():
    data = request.json

    # Basic form validation
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    company = data.get('company')

    errors = {}

    if not name or not name.strip():
        errors['name'] = 'Name is required.'

    if not email or not EMAIL_REGEX.match(email):
        errors['email'] = 'Valid email is required.'

    if phone and not re.match(r'^\+?[0-9\-\s]{7,15}$', phone):
        errors['phone'] = 'Phone number format is invalid.'

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Check if email already exists
    existing_lead = Lead.query.filter_by(email=email).first()
    if existing_lead:
        return jsonify({'success': False, 'errors': {'email': 'Email already captured.'}}), 400

    # Save lead to database
    new_lead = Lead(name=name.strip(), email=email.strip(), phone=phone.strip() if phone else None, company=company.strip() if company else None)
    db.session.add(new_lead)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Lead captured successfully.'}), 201
