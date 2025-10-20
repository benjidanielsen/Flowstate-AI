"""
CRM Analytics Service for Flowstate-AI
Provides detailed analytics, reporting, and data visualization for CRM data.
"""

import redis
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class CRMAnalyticsService:
    """Service for CRM analytics and reporting."""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize the CRM analytics service."""
        self.redis = redis_client
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline metrics and statistics."""
        contacts = self._get_all_contacts()
        deals = self._get_all_deals()
        
        # Contact metrics by lifecycle stage
        lifecycle_distribution = Counter(c.get('lifecycle_stage', 'lead') for c in contacts)
        
        # Deal metrics by stage
        deal_stage_distribution = Counter(d.get('stage', 'prospecting') for d in deals)
        
        # Deal metrics by status
        deal_status_distribution = Counter(d.get('status', 'open') for d in deals)
        
        # Calculate conversion rates
        total_contacts = len(contacts)
        mql_count = lifecycle_distribution.get('mql', 0)
        sql_count = lifecycle_distribution.get('sql', 0)
        customer_count = lifecycle_distribution.get('customer', 0)
        
        lead_to_mql_rate = (mql_count / total_contacts * 100) if total_contacts > 0 else 0
        mql_to_sql_rate = (sql_count / mql_count * 100) if mql_count > 0 else 0
        sql_to_customer_rate = (customer_count / sql_count * 100) if sql_count > 0 else 0
        
        # Calculate deal metrics
        total_deal_value = sum(float(d.get('amount', 0)) for d in deals)
        won_deals = [d for d in deals if d.get('status') == 'won']
        lost_deals = [d for d in deals if d.get('status') == 'lost']
        open_deals = [d for d in deals if d.get('status') == 'open']
        
        won_deal_value = sum(float(d.get('amount', 0)) for d in won_deals)
        lost_deal_value = sum(float(d.get('amount', 0)) for d in lost_deals)
        open_deal_value = sum(float(d.get('amount', 0)) for d in open_deals)
        
        win_rate = (len(won_deals) / len(deals) * 100) if len(deals) > 0 else 0
        
        # Calculate average deal size
        avg_deal_size = total_deal_value / len(deals) if len(deals) > 0 else 0
        avg_won_deal_size = won_deal_value / len(won_deals) if len(won_deals) > 0 else 0
        
        return {
            'contacts': {
                'total': total_contacts,
                'by_lifecycle_stage': dict(lifecycle_distribution),
                'conversion_rates': {
                    'lead_to_mql': round(lead_to_mql_rate, 2),
                    'mql_to_sql': round(mql_to_sql_rate, 2),
                    'sql_to_customer': round(sql_to_customer_rate, 2)
                }
            },
            'deals': {
                'total': len(deals),
                'by_stage': dict(deal_stage_distribution),
                'by_status': dict(deal_status_distribution),
                'total_value': round(total_deal_value, 2),
                'won_value': round(won_deal_value, 2),
                'lost_value': round(lost_deal_value, 2),
                'open_value': round(open_deal_value, 2),
                'win_rate': round(win_rate, 2),
                'avg_deal_size': round(avg_deal_size, 2),
                'avg_won_deal_size': round(avg_won_deal_size, 2)
            }
        }
    
    def get_time_series_data(self, days: int = 30) -> Dict[str, Any]:
        """Get time series data for contacts and deals over the specified period."""
        contacts = self._get_all_contacts()
        deals = self._get_all_deals()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Initialize daily counters
        daily_contacts = defaultdict(int)
        daily_deals = defaultdict(int)
        daily_deal_value = defaultdict(float)
        
        # Count contacts by creation date
        for contact in contacts:
            created_at = contact.get('created_at', '')
            if created_at:
                try:
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                    if start_date.date() <= date <= end_date.date():
                        daily_contacts[str(date)] += 1
                except:
                    pass
        
        # Count deals by creation date
        for deal in deals:
            created_at = deal.get('created_at', '')
            amount = float(deal.get('amount', 0))
            if created_at:
                try:
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                    if start_date.date() <= date <= end_date.date():
                        daily_deals[str(date)] += 1
                        daily_deal_value[str(date)] += amount
                except:
                    pass
        
        # Generate complete date series
        date_series = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            date_str = str(current_date)
            date_series.append({
                'date': date_str,
                'contacts': daily_contacts.get(date_str, 0),
                'deals': daily_deals.get(date_str, 0),
                'deal_value': round(daily_deal_value.get(date_str, 0), 2)
            })
            current_date += timedelta(days=1)
        
        return {
            'start_date': str(start_date.date()),
            'end_date': str(end_date.date()),
            'data': date_series
        }
    
    def get_top_contacts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top contacts by deal value."""
        contacts = self._get_all_contacts()
        deals = self._get_all_deals()
        
        # Calculate total deal value per contact
        contact_values = defaultdict(float)
        for deal in deals:
            contact_id = deal.get('contact_id')
            if contact_id:
                contact_values[contact_id] += float(deal.get('amount', 0))
        
        # Enrich contacts with deal values
        enriched_contacts = []
        for contact in contacts:
            contact_id = contact.get('id')
            total_value = contact_values.get(contact_id, 0)
            enriched_contacts.append({
                **contact,
                'total_deal_value': round(total_value, 2)
            })
        
        # Sort by total deal value and return top N
        enriched_contacts.sort(key=lambda x: x['total_deal_value'], reverse=True)
        return enriched_contacts[:limit]
    
    def get_top_deals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top deals by value."""
        deals = self._get_all_deals()
        deals.sort(key=lambda x: float(x.get('amount', 0)), reverse=True)
        return deals[:limit]
    
    def get_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get activity summary for the specified period."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        contacts = self._get_all_contacts()
        deals = self._get_all_deals()
        
        # Count new contacts
        new_contacts = [c for c in contacts if self._is_within_period(c.get('created_at'), start_date, end_date)]
        
        # Count new deals
        new_deals = [d for d in deals if self._is_within_period(d.get('created_at'), start_date, end_date)]
        
        # Count updated contacts
        updated_contacts = [c for c in contacts if self._is_within_period(c.get('updated_at'), start_date, end_date)]
        
        # Count updated deals
        updated_deals = [d for d in deals if self._is_within_period(d.get('updated_at'), start_date, end_date)]
        
        # Count won/lost deals
        won_deals = [d for d in new_deals if d.get('status') == 'won']
        lost_deals = [d for d in new_deals if d.get('status') == 'lost']
        
        return {
            'period_days': days,
            'start_date': str(start_date.date()),
            'end_date': str(end_date.date()),
            'new_contacts': len(new_contacts),
            'new_deals': len(new_deals),
            'updated_contacts': len(updated_contacts),
            'updated_deals': len(updated_deals),
            'won_deals': len(won_deals),
            'lost_deals': len(lost_deals),
            'won_deal_value': round(sum(float(d.get('amount', 0)) for d in won_deals), 2),
            'lost_deal_value': round(sum(float(d.get('amount', 0)) for d in lost_deals), 2)
        }
    
    def generate_custom_report(self, report_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a custom report based on the specified type and parameters."""
        params = params or {}
        
        if report_type == 'pipeline_health':
            return self._generate_pipeline_health_report(params)
        elif report_type == 'sales_forecast':
            return self._generate_sales_forecast_report(params)
        elif report_type == 'contact_engagement':
            return self._generate_contact_engagement_report(params)
        else:
            return {'error': f'Unknown report type: {report_type}'}
    
    def _generate_pipeline_health_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a pipeline health report."""
        metrics = self.get_pipeline_metrics()
        activity = self.get_activity_summary(days=30)
        
        # Calculate health score (0-100)
        health_score = 0
        
        # Factor 1: Conversion rates (40 points)
        conversion_rates = metrics['contacts']['conversion_rates']
        avg_conversion = (conversion_rates['lead_to_mql'] + conversion_rates['mql_to_sql'] + conversion_rates['sql_to_customer']) / 3
        health_score += min(avg_conversion / 2, 40)  # Cap at 40 points
        
        # Factor 2: Win rate (30 points)
        win_rate = metrics['deals']['win_rate']
        health_score += min(win_rate / 3.33, 30)  # Cap at 30 points
        
        # Factor 3: Activity level (30 points)
        total_activity = activity['new_contacts'] + activity['new_deals'] + activity['updated_contacts'] + activity['updated_deals']
        health_score += min(total_activity / 10, 30)  # Cap at 30 points
        
        return {
            'health_score': round(health_score, 2),
            'metrics': metrics,
            'activity': activity,
            'recommendations': self._generate_recommendations(health_score, metrics)
        }
    
    def _generate_sales_forecast_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a sales forecast report."""
        deals = self._get_all_deals()
        open_deals = [d for d in deals if d.get('status') == 'open']
        
        # Calculate weighted pipeline value
        stage_weights = {
            'prospecting': 0.1,
            'qualification': 0.2,
            'proposal': 0.5,
            'negotiation': 0.7,
            'closing': 0.9
        }
        
        weighted_value = 0
        for deal in open_deals:
            amount = float(deal.get('amount', 0))
            stage = deal.get('stage', 'prospecting')
            weight = stage_weights.get(stage, 0.1)
            weighted_value += amount * weight
        
        # Get historical win rate
        metrics = self.get_pipeline_metrics()
        win_rate = metrics['deals']['win_rate'] / 100
        
        # Calculate forecast
        forecast_value = weighted_value * win_rate
        
        return {
            'total_pipeline_value': round(sum(float(d.get('amount', 0)) for d in open_deals), 2),
            'weighted_pipeline_value': round(weighted_value, 2),
            'forecast_value': round(forecast_value, 2),
            'win_rate': round(win_rate * 100, 2),
            'open_deals_count': len(open_deals),
            'deals_by_stage': Counter(d.get('stage', 'prospecting') for d in open_deals)
        }
    
    def _generate_contact_engagement_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a contact engagement report."""
        contacts = self._get_all_contacts()
        
        # Calculate engagement score for each contact
        engaged_contacts = []
        for contact in contacts:
            engagement_score = self._calculate_engagement_score(contact)
            if engagement_score > 0:
                engaged_contacts.append({
                    **contact,
                    'engagement_score': engagement_score
                })
        
        # Sort by engagement score
        engaged_contacts.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return {
            'total_contacts': len(contacts),
            'engaged_contacts': len(engaged_contacts),
            'engagement_rate': round(len(engaged_contacts) / len(contacts) * 100, 2) if len(contacts) > 0 else 0,
            'top_engaged_contacts': engaged_contacts[:10]
        }
    
    def _calculate_engagement_score(self, contact: Dict[str, Any]) -> float:
        """Calculate engagement score for a contact."""
        score = 0
        
        # Factor 1: Lifecycle stage progression
        lifecycle_scores = {
            'lead': 1,
            'mql': 2,
            'sql': 3,
            'opportunity': 4,
            'customer': 5
        }
        score += lifecycle_scores.get(contact.get('lifecycle_stage', 'lead'), 0) * 10
        
        # Factor 2: Recent updates
        updated_at = contact.get('updated_at', '')
        if updated_at:
            try:
                update_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_since_update = (datetime.now(update_date.tzinfo) - update_date).days
                if days_since_update < 7:
                    score += 20
                elif days_since_update < 30:
                    score += 10
            except:
                pass
        
        # Factor 3: Associated deals
        # (Would need to query deals by contact_id, simplified here)
        
        return score
    
    def _generate_recommendations(self, health_score: float, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on pipeline health."""
        recommendations = []
        
        if health_score < 50:
            recommendations.append("Pipeline health is below optimal. Focus on lead generation and qualification.")
        
        conversion_rates = metrics['contacts']['conversion_rates']
        if conversion_rates['lead_to_mql'] < 20:
            recommendations.append("Lead to MQL conversion rate is low. Review lead quality and qualification criteria.")
        
        if conversion_rates['mql_to_sql'] < 30:
            recommendations.append("MQL to SQL conversion rate is low. Improve lead nurturing and engagement strategies.")
        
        win_rate = metrics['deals']['win_rate']
        if win_rate < 25:
            recommendations.append("Win rate is below industry average. Analyze lost deals and refine sales process.")
        
        if len(recommendations) == 0:
            recommendations.append("Pipeline health is good. Continue current strategies and monitor key metrics.")
        
        return recommendations
    
    def _get_all_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts from Redis."""
        contacts = []
        for key in self.redis.scan_iter("contact:*"):
            try:
                contact_data = self.redis.get(key)
                if contact_data:
                    contacts.append(json.loads(contact_data))
            except:
                pass
        return contacts
    
    def _get_all_deals(self) -> List[Dict[str, Any]]:
        """Get all deals from Redis."""
        deals = []
        for key in self.redis.scan_iter("deal:*"):
            try:
                deal_data = self.redis.get(key)
                if deal_data:
                    deals.append(json.loads(deal_data))
            except:
                pass
        return deals
    
    def _is_within_period(self, timestamp: str, start_date: datetime, end_date: datetime) -> bool:
        """Check if a timestamp is within the specified period."""
        if not timestamp:
            return False
        try:
            date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return start_date <= date <= end_date
        except:
            return False
