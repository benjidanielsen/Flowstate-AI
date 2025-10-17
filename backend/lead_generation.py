from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import re

lead_gen = Blueprint('lead_gen', __name__)
db = SQLAlchemy()

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Lead {self.email}>'

# Simple email validation regex
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@lead_gen.route('/api/leads', methods=['POST'])
def capture_lead():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip() if 'phone' in data else None

    # Validation
    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not email or not EMAIL_REGEX.match(email):
        errors['email'] = 'Valid email is required.'

    if errors:
        return jsonify({'errors': errors}), 400

    # Save lead
    new_lead = Lead(name=name, email=email, phone=phone)
    try:
        db.session.add(new_lead)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': 'Lead captured successfully', 'lead': {'id': new_lead.id, 'name': new_lead.name, 'email': new_lead.email, 'phone': new_lead.phone}}), 201
