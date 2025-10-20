"""
CRM Analytics API for Flowstate-AI
Flask blueprint providing analytics and reporting endpoints.
"""

from flask import Blueprint, jsonify, request
import redis
from crm_analytics_service import CRMAnalyticsService

crm_analytics_bp = Blueprint('crm_analytics', __name__, url_prefix='/api/crm/analytics')

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize analytics service
analytics_service = CRMAnalyticsService(redis_client)

@crm_analytics_bp.route('/metrics', methods=['GET'])
def get_pipeline_metrics():
    """Get comprehensive pipeline metrics."""
    try:
        metrics = analytics_service.get_pipeline_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_analytics_bp.route('/time-series', methods=['GET'])
def get_time_series():
    """Get time series data for contacts and deals."""
    try:
        days = int(request.args.get('days', 30))
        data = analytics_service.get_time_series_data(days=days)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_analytics_bp.route('/top-contacts', methods=['GET'])
def get_top_contacts():
    """Get top contacts by deal value."""
    try:
        limit = int(request.args.get('limit', 10))
        contacts = analytics_service.get_top_contacts(limit=limit)
        return jsonify(contacts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_analytics_bp.route('/top-deals', methods=['GET'])
def get_top_deals():
    """Get top deals by value."""
    try:
        limit = int(request.args.get('limit', 10))
        deals = analytics_service.get_top_deals(limit=limit)
        return jsonify(deals), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_analytics_bp.route('/activity', methods=['GET'])
def get_activity_summary():
    """Get activity summary for the specified period."""
    try:
        days = int(request.args.get('days', 7))
        summary = analytics_service.get_activity_summary(days=days)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_analytics_bp.route('/reports/<report_type>', methods=['POST'])
def generate_custom_report(report_type):
    """Generate a custom report."""
    try:
        params = request.get_json() or {}
        report = analytics_service.generate_custom_report(report_type, params)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crm_analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get all data needed for the analytics dashboard."""
    try:
        metrics = analytics_service.get_pipeline_metrics()
        time_series = analytics_service.get_time_series_data(days=30)
        activity = analytics_service.get_activity_summary(days=7)
        top_contacts = analytics_service.get_top_contacts(limit=5)
        top_deals = analytics_service.get_top_deals(limit=5)
        
        return jsonify({
            'metrics': metrics,
            'time_series': time_series,
            'activity': activity,
            'top_contacts': top_contacts,
            'top_deals': top_deals
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
