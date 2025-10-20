"""
CRM API Endpoints for Flowstate-AI
Flask REST API for managing contacts and deals in the CRM system.
"""

from flask import Flask, request, jsonify
import redis
from crm_contact_service import CRMContactService
from crm_deal_service import CRMDealService

app = Flask(__name__)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)

# Initialize CRM services
contact_service = CRMContactService(redis_client)
deal_service = CRMDealService(redis_client)

# ============================================================================
# Contact Endpoints
# ============================================================================

@app.route('/api/v1/contacts', methods=['POST'])
def create_contact():
    """Create a new contact."""
    try:
        contact_data = request.json
        contact = contact_service.create_contact(contact_data)
        return jsonify(contact), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/contacts', methods=['GET'])
def list_contacts():
    """List contacts with optional filtering."""
    try:
        lifecycle_stage = request.args.get('lifecycle_stage')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        contacts = contact_service.list_contacts(
            lifecycle_stage=lifecycle_stage,
            limit=limit,
            offset=offset
        )
        
        total_count = contact_service.get_contact_count(lifecycle_stage=lifecycle_stage)
        
        return jsonify({
            "contacts": contacts,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/contacts/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID."""
    try:
        contact = contact_service.get_contact(contact_id)
        if contact:
            return jsonify(contact), 200
        return jsonify({"error": "Contact not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/contacts/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact."""
    try:
        updates = request.json
        contact = contact_service.update_contact(contact_id, updates)
        if contact:
            return jsonify(contact), 200
        return jsonify({"error": "Contact not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact."""
    try:
        success = contact_service.delete_contact(contact_id)
        if success:
            return jsonify({"message": "Contact deleted successfully"}), 200
        return jsonify({"error": "Contact not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============================================================================
# Deal Endpoints
# ============================================================================

@app.route('/api/v1/deals', methods=['POST'])
def create_deal():
    """Create a new deal."""
    try:
        deal_data = request.json
        deal = deal_service.create_deal(deal_data)
        return jsonify(deal), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/deals', methods=['GET'])
def list_deals():
    """List deals with optional filtering."""
    try:
        pipeline = request.args.get('pipeline')
        stage = request.args.get('stage')
        contact_id = request.args.get('contact_id')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        deals = deal_service.list_deals(
            pipeline=pipeline,
            stage=stage,
            contact_id=contact_id,
            limit=limit,
            offset=offset
        )
        
        total_count = deal_service.get_deal_count(pipeline=pipeline, stage=stage)
        
        return jsonify({
            "deals": deals,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/deals/<deal_id>', methods=['GET'])
def get_deal(deal_id):
    """Get a single deal by ID."""
    try:
        deal = deal_service.get_deal(deal_id)
        if deal:
            return jsonify(deal), 200
        return jsonify({"error": "Deal not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/deals/<deal_id>', methods=['PUT'])
def update_deal(deal_id):
    """Update an existing deal."""
    try:
        updates = request.json
        deal = deal_service.update_deal(deal_id, updates)
        if deal:
            return jsonify(deal), 200
        return jsonify({"error": "Deal not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/deals/<deal_id>', methods=['DELETE'])
def delete_deal(deal_id):
    """Delete a deal."""
    try:
        success = deal_service.delete_deal(deal_id)
        if success:
            return jsonify({"message": "Deal deleted successfully"}), 200
        return jsonify({"error": "Deal not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/deals/<deal_id>/advance_stage', methods=['POST'])
def advance_deal_stage(deal_id):
    """Advance a deal to the next stage."""
    try:
        deal = deal_service.advance_stage(deal_id)
        if deal:
            return jsonify(deal), 200
        return jsonify({"error": "Deal not found or already at final stage"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/v1/pipelines/<pipeline_type>/stages', methods=['GET'])
def get_pipeline_stages(pipeline_type):
    """Get the stages for a specific pipeline."""
    try:
        stages = deal_service.get_pipeline_stages(pipeline_type)
        if stages:
            return jsonify({"pipeline": pipeline_type, "stages": stages}), 200
        return jsonify({"error": "Pipeline not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============================================================================
# Health Check
# ============================================================================

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        redis_client.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
