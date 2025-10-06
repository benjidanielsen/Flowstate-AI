"""
CRM Dashboard Routes for Flowstate-AI Unified Dashboard
Flask routes for rendering CRM views and handling CRM-related requests.
"""

from flask import Blueprint, render_template, jsonify, request
import redis
import requests
from crm_contact_service import CRMContactService
from crm_deal_service import CRMDealService

# Create Blueprint for CRM routes
crm_bp = Blueprint('crm', __name__, url_prefix='/crm')

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)

# Initialize CRM services
contact_service = CRMContactService(redis_client)
deal_service = CRMDealService(redis_client)

# CRM API base URL (assuming it runs on port 5001)
CRM_API_BASE = "http://localhost:5001/api/v1"

@crm_bp.route('/')
def crm_dashboard():
    """Main CRM dashboard view."""
    try:
        # Get summary statistics
        total_contacts = contact_service.get_contact_count()
        total_deals = deal_service.get_deal_count()
        
        # Get counts by lifecycle stage
        stage_counts = {}
        for stage in ["subscriber", "lead", "mql", "sql", "customer", "partner"]:
            stage_counts[stage] = contact_service.get_contact_count(lifecycle_stage=stage)
        
        # Get counts by pipeline
        sales_deals = deal_service.get_deal_count(pipeline="Sales")
        recruiting_deals = deal_service.get_deal_count(pipeline="Recruiting")
        
        # Get recent contacts and deals
        recent_contacts = contact_service.list_contacts(limit=10)
        recent_deals = deal_service.list_deals(limit=10)
        
        return render_template('crm_dashboard.html',
                             total_contacts=total_contacts,
                             total_deals=total_deals,
                             stage_counts=stage_counts,
                             sales_deals=sales_deals,
                             recruiting_deals=recruiting_deals,
                             recent_contacts=recent_contacts,
                             recent_deals=recent_deals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_bp.route('/contacts')
def contacts_view():
    """View for managing contacts."""
    try:
        lifecycle_stage = request.args.get('lifecycle_stage')
        page = int(request.args.get('page', 1))
        limit = 50
        offset = (page - 1) * limit
        
        contacts = contact_service.list_contacts(
            lifecycle_stage=lifecycle_stage,
            limit=limit,
            offset=offset
        )
        
        total_count = contact_service.get_contact_count(lifecycle_stage=lifecycle_stage)
        total_pages = (total_count + limit - 1) // limit
        
        return render_template('crm_contacts.html',
                             contacts=contacts,
                             current_page=page,
                             total_pages=total_pages,
                             lifecycle_stage=lifecycle_stage,
                             total_count=total_count)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_bp.route('/deals')
def deals_view():
    """View for managing deals."""
    try:
        pipeline = request.args.get('pipeline')
        stage = request.args.get('stage')
        page = int(request.args.get('page', 1))
        limit = 50
        offset = (page - 1) * limit
        
        deals = deal_service.list_deals(
            pipeline=pipeline,
            stage=stage,
            limit=limit,
            offset=offset
        )
        
        total_count = deal_service.get_deal_count(pipeline=pipeline, stage=stage)
        total_pages = (total_count + limit - 1) // limit
        
        # Get pipeline stages for filtering
        sales_stages = deal_service.get_pipeline_stages("Sales")
        recruiting_stages = deal_service.get_pipeline_stages("Recruiting")
        
        return render_template('crm_deals.html',
                             deals=deals,
                             current_page=page,
                             total_pages=total_pages,
                             pipeline=pipeline,
                             stage=stage,
                             total_count=total_count,
                             sales_stages=sales_stages,
                             recruiting_stages=recruiting_stages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_bp.route('/pipelines')
def pipelines_view():
    """View for visualizing CRM pipelines."""
    try:
        # Get all deals grouped by pipeline and stage
        sales_pipeline = {}
        recruiting_pipeline = {}
        
        # Get stages for each pipeline
        sales_stages = deal_service.get_pipeline_stages("Sales")
        recruiting_stages = deal_service.get_pipeline_stages("Recruiting")
        
        # Get deals for each stage in Sales pipeline
        for stage in sales_stages:
            deals = deal_service.list_deals(pipeline="Sales", stage=stage, limit=100)
            sales_pipeline[stage] = {
                "count": len(deals),
                "deals": deals
            }
        
        # Get deals for each stage in Recruiting pipeline
        for stage in recruiting_stages:
            deals = deal_service.list_deals(pipeline="Recruiting", stage=stage, limit=100)
            recruiting_pipeline[stage] = {
                "count": len(deals),
                "deals": deals
            }
        
        return render_template('crm_pipelines.html',
                             sales_pipeline=sales_pipeline,
                             recruiting_pipeline=recruiting_pipeline,
                             sales_stages=sales_stages,
                             recruiting_stages=recruiting_stages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_bp.route('/analytics')
def analytics_view():
    """View for CRM analytics and reports."""
    try:
        # Get lifecycle stage distribution
        lifecycle_distribution = {}
        for stage in ["subscriber", "lead", "mql", "sql", "customer", "partner"]:
            lifecycle_distribution[stage] = contact_service.get_contact_count(lifecycle_stage=stage)
        
        # Get pipeline stage distribution
        sales_distribution = {}
        recruiting_distribution = {}
        
        for stage in deal_service.get_pipeline_stages("Sales"):
            sales_distribution[stage] = deal_service.get_deal_count(pipeline="Sales", stage=stage)
        
        for stage in deal_service.get_pipeline_stages("Recruiting"):
            recruiting_distribution[stage] = deal_service.get_deal_count(pipeline="Recruiting", stage=stage)
        
        return render_template('crm_analytics.html',
                             lifecycle_distribution=lifecycle_distribution,
                             sales_distribution=sales_distribution,
                             recruiting_distribution=recruiting_distribution)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API-style endpoints for AJAX requests
@crm_bp.route('/api/stats')
def get_crm_stats():
    """Get CRM statistics for dashboard widgets."""
    try:
        stats = {
            "total_contacts": contact_service.get_contact_count(),
            "total_deals": deal_service.get_deal_count(),
            "sales_deals": deal_service.get_deal_count(pipeline="Sales"),
            "recruiting_deals": deal_service.get_deal_count(pipeline="Recruiting"),
            "lifecycle_stages": {},
            "pipeline_stages": {
                "Sales": {},
                "Recruiting": {}
            }
        }
        
        # Get lifecycle stage counts
        for stage in ["subscriber", "lead", "mql", "sql", "customer", "partner"]:
            stats["lifecycle_stages"][stage] = contact_service.get_contact_count(lifecycle_stage=stage)
        
        # Get pipeline stage counts
        for stage in deal_service.get_pipeline_stages("Sales"):
            stats["pipeline_stages"]["Sales"][stage] = deal_service.get_deal_count(pipeline="Sales", stage=stage)
        
        for stage in deal_service.get_pipeline_stages("Recruiting"):
            stats["pipeline_stages"]["Recruiting"][stage] = deal_service.get_deal_count(pipeline="Recruiting", stage=stage)
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
