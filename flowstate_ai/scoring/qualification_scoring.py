from typing import Dict, Any

class QualificationScorer:
    """
    QualificationScorer calculates a lead score based on engagement metrics and profile data.
    """

    def __init__(self, engagement_weights: Dict[str, float] = None, profile_weights: Dict[str, float] = None):
        # Default weights if none provided
        self.engagement_weights = engagement_weights or {
            'page_views': 1.0,
            'email_clicks': 3.0,
            'demo_requests': 5.0,
            'time_on_site': 0.1  # per minute
        }
        self.profile_weights = profile_weights or {
            'company_size': {
                'small': 1.0,
                'medium': 3.0,
                'large': 5.0
            },
            'industry': {
                'technology': 5.0,
                'finance': 4.0,
                'education': 2.0,
                # default category weight
                'other': 1.0
            },
            'job_title': {
                'ceo': 5.0,
                'cto': 4.0,
                'manager': 3.0,
                'intern': 0.5,
                # default
                'other': 1.0
            }
        }

    def score_engagement(self, engagement_data: Dict[str, Any]) -> float:
        score = 0.0
        # page_views
        pv = engagement_data.get('page_views', 0)
        score += pv * self.engagement_weights['page_views']

        # email_clicks
        ec = engagement_data.get('email_clicks', 0)
        score += ec * self.engagement_weights['email_clicks']

        # demo_requests
        dr = engagement_data.get('demo_requests', 0)
        score += dr * self.engagement_weights['demo_requests']

        # time_on_site (assumed in minutes)
        tos = engagement_data.get('time_on_site', 0)
        score += tos * self.engagement_weights['time_on_site']

        return score

    def score_profile(self, profile_data: Dict[str, Any]) -> float:
        score = 0.0

        # company_size
        cs = profile_data.get('company_size', '').lower()
        cs_score = self.profile_weights['company_size'].get(cs, 0)
        score += cs_score

        # industry
        ind = profile_data.get('industry', '').lower()
        ind_score = self.profile_weights['industry'].get(ind, self.profile_weights['industry']['other'])
        score += ind_score

        # job_title
        jt = profile_data.get('job_title', '').lower()
        jt_score = self.profile_weights['job_title'].get(jt, self.profile_weights['job_title']['other'])
        score += jt_score

        return score

    def calculate_total_score(self, engagement_data: Dict[str, Any], profile_data: Dict[str, Any]) -> float:
        engagement_score = self.score_engagement(engagement_data)
        profile_score = self.score_profile(profile_data)
        total_score = engagement_score + profile_score
        return total_score


# Example usage:
# scorer = QualificationScorer()
# engagement = {'page_views': 10, 'email_clicks': 2, 'demo_requests': 1, 'time_on_site': 15}
# profile = {'company_size': 'Medium', 'industry': 'Technology', 'job_title': 'CTO'}
# print(scorer.calculate_total_score(engagement, profile))
