from typing import Dict, Any

class QualificationScorer:
    """
    Lead Qualification Scoring System based on engagement metrics and profile data.
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize with optional custom weights for scoring components.
        Example weights keys:
          - 'engagement_time'
          - 'page_views'
          - 'email_clicks'
          - 'job_title_score'
          - 'company_size_score'
          - 'industry_score'

        :param weights: dict of weights for scoring components
        """
        # Default weights if none provided
        self.weights = weights or {
            'engagement_time': 0.4,
            'page_views': 0.2,
            'email_clicks': 0.2,
            'job_title_score': 0.1,
            'company_size_score': 0.05,
            'industry_score': 0.05
        }

        # Define scoring maps for profile data
        self.job_title_scores = {
            'ceo': 10,
            'founder': 9,
            'cto': 8,
            'manager': 6,
            'engineer': 4,
            'intern': 1
        }

        self.company_size_scores = {
            'enterprise': 10,
            'mid_market': 7,
            'small_business': 4,
            'startup': 3
        }

        self.industry_scores = {
            'technology': 10,
            'finance': 8,
            'healthcare': 7,
            'education': 5,
            'retail': 4,
            'other': 2
        }

    def score_engagement(self, engagement_metrics: Dict[str, Any]) -> float:
        """
        Compute engagement score based on engagement metrics.
        Expected keys: 'engagement_time' (minutes), 'page_views', 'email_clicks'

        :param engagement_metrics: dict of engagement metrics
        :return: engagement score (0-10 scale)
        """
        time = engagement_metrics.get('engagement_time', 0)
        page_views = engagement_metrics.get('page_views', 0)
        email_clicks = engagement_metrics.get('email_clicks', 0)

        # Normalize each metric to 0-10 scale
        time_score = min(time / 30 * 10, 10)  # assuming 30+ minutes max
        page_views_score = min(page_views / 20 * 10, 10)  # assuming 20+ page views max
        email_clicks_score = min(email_clicks / 5 * 10, 10)  # assuming 5+ clicks max

        weighted_score = (
            time_score * self.weights['engagement_time'] +
            page_views_score * self.weights['page_views'] +
            email_clicks_score * self.weights['email_clicks']
        )

        return weighted_score

    def score_profile(self, profile_data: Dict[str, Any]) -> float:
        """
        Compute profile score based on job title, company size, and industry.

        :param profile_data: dict with keys 'job_title', 'company_size', 'industry'
        :return: profile score (0-10 scale)
        """
        job_title = profile_data.get('job_title', '').lower()
        company_size = profile_data.get('company_size', '').lower()
        industry = profile_data.get('industry', '').lower()

        job_score = 0
        company_score = 0
        industry_score = 0

        # Find best matching job title score
        for title_keyword, score in self.job_title_scores.items():
            if title_keyword in job_title:
                job_score = max(job_score, score)

        company_score = self.company_size_scores.get(company_size, 0)
        industry_score = self.industry_scores.get(industry, self.industry_scores['other'])

        weighted_score = (
            job_score * self.weights['job_title_score'] +
            company_score * self.weights['company_size_score'] +
            industry_score * self.weights['industry_score']
        )

        return weighted_score

    def score_lead(self, engagement_metrics: Dict[str, Any], profile_data: Dict[str, Any]) -> float:
        """
        Compute total lead qualification score combining engagement and profile data.

        :param engagement_metrics: dict of engagement metrics
        :param profile_data: dict of profile data
        :return: total lead score (0-10 scale)
        """
        engagement_score = self.score_engagement(engagement_metrics)
        profile_score = self.score_profile(profile_data)

        total_score = engagement_score + profile_score
        # Clamp max to 10
        return min(total_score, 10)


# Example usage
if __name__ == '__main__':
    scorer = QualificationScorer()

    engagement = {
        'engagement_time': 15,  # minutes
        'page_views': 8,
        'email_clicks': 2
    }

    profile = {
        'job_title': 'Chief Technology Officer',
        'company_size': 'Enterprise',
        'industry': 'Technology'
    }

    score = scorer.score_lead(engagement, profile)
    print(f'Lead Qualification Score: {score:.2f}')
