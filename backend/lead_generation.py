from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError

lead_gen = Blueprint('lead_gen', __name__)
db = SQLAlchemy()

# Database model for Lead
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    company = db.Column(db.String(100), nullable=True)

# Schema for input validation
class LeadSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str(required=False)
    company = fields.Str(required=False)

lead_schema = LeadSchema()

@lead_gen.route('/api/leads', methods=['POST'])
def capture_lead():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate input
    try:
        data = lead_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # Check for existing lead by email
    existing_lead = Lead.query.filter_by(email=data['email']).first()
    if existing_lead:
        return jsonify({'message': 'Lead with this email already exists'}), 409

    # Create new lead
    new_lead = Lead(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        company=data.get('company')
    )
    db.session.add(new_lead)
    db.session.commit()

    return jsonify({'message': 'Lead captured successfully', 'lead': lead_schema.dump(new_lead)}), 201
