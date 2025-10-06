from typing import Dict, Any

class QualificationScorer:
    """
    Lead Qualification Scoring System based on engagement metrics and profile data.
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the scorer with optional custom weights.

        weights keys can include:
          - engagement_score
          - profile_score
          - email_open_rate
          - click_through_rate
          - job_title_score
          - company_size_score
          - industry_score

        Defaults provided if no weights supplied.
        """
        self.weights = weights or {
            "engagement_score": 0.4,
            "profile_score": 0.4,
            "email_open_rate": 0.1,
            "click_through_rate": 0.1
        }

    def score_engagement(self, engagement_metrics: Dict[str, Any]) -> float:
        """
        Calculate engagement score based on engagement metrics.

        engagement_metrics expected keys:
          - visits: int
          - time_spent_minutes: float
          - emails_opened: int
          - links_clicked: int

        Returns a normalized score between 0 and 1.
        """
        visits = engagement_metrics.get("visits", 0)
        time_spent = engagement_metrics.get("time_spent_minutes", 0.0)
        emails_opened = engagement_metrics.get("emails_opened", 0)
        links_clicked = engagement_metrics.get("links_clicked", 0)

        # Simple heuristic: weighted sum normalized by thresholds
        visit_score = min(visits / 10, 1.0)  # more than 10 visits saturates
        time_score = min(time_spent / 30, 1.0)  # 30 minutes or more saturates
        open_rate = min(emails_opened / 5, 1.0)  # 5 emails opened saturates
        click_rate = min(links_clicked / 3, 1.0)  # 3 clicks saturates

        engagement_score = (0.4 * visit_score + 0.3 * time_score + 0.2 * open_rate + 0.1 * click_rate)
        return engagement_score

    def score_profile(self, profile_data: Dict[str, Any]) -> float:
        """
        Calculate profile score based on profile data.

        profile_data expected keys:
          - job_title: str
          - company_size: int
          - industry: str

        Returns a normalized score between 0 and 1.
        """
        job_title = profile_data.get("job_title", "").lower()
        company_size = profile_data.get("company_size", 0)
        industry = profile_data.get("industry", "").lower()

        # Job title scoring
        title_scores = {
            "ceo": 1.0,
            "founder": 1.0,
            "co-founder": 1.0,
            "director": 0.8,
            "manager": 0.6,
            "engineer": 0.5,
            "intern": 0.1
        }

        job_score = 0.3  # default low score
        for key, val in title_scores.items():
            if key in job_title:
                job_score = val
                break

        # Company size scoring
        # Larger companies have higher score up to a cap
        if company_size >= 1000:
            company_score = 1.0
        elif company_size >= 100:
            company_score = 0.7
        elif company_size >= 10:
            company_score = 0.4
        else:
            company_score = 0.1

        # Industry scoring - prioritize tech and related
        industry_scores = {
            "software": 1.0,
            "technology": 1.0,
            "saas": 0.9,
            "finance": 0.7,
            "healthcare": 0.6,
            "education": 0.5
        }

        industry_score = 0.3  # base score for unknown
        for key, val in industry_scores.items():
            if key in industry:
                industry_score = val
                break

        profile_score = (0.5 * job_score + 0.3 * company_score + 0.2 * industry_score)
        return profile_score

    def calculate_score(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate the overall lead qualification score.

        lead_data keys:
          - engagement_metrics: Dict
          - profile_data: Dict

        Returns score between 0 and 1.
        """
        engagement_metrics = lead_data.get("engagement_metrics", {})
        profile_data = lead_data.get("profile_data", {})

        engagement_score = self.score_engagement(engagement_metrics)
        profile_score = self.score_profile(profile_data)

        # Weighting engagement and profile
        weighted_score = (
            self.weights.get("engagement_score", 0.4) * engagement_score +
            self.weights.get("profile_score", 0.4) * profile_score
        )

        # Optionally include email open and click rates if provided
        email_open_rate = 0.0
        click_through_rate = 0.0

        emails_sent = engagement_metrics.get("emails_sent", 0)
        emails_opened = engagement_metrics.get("emails_opened", 0)
        links_clicked = engagement_metrics.get("links_clicked", 0)

        if emails_sent > 0:
            email_open_rate = emails_opened / emails_sent
        if emails_opened > 0:
            click_through_rate = links_clicked / emails_opened

        weighted_score += self.weights.get("email_open_rate", 0.1) * min(email_open_rate, 1.0)
        weighted_score += self.weights.get("click_through_rate", 0.1) * min(click_through_rate, 1.0)

        # Clamp final score between 0 and 1
        return max(0.0, min(weighted_score, 1.0))


if __name__ == "__main__":
    scorer = QualificationScorer()
    example_lead = {
        "engagement_metrics": {
            "visits": 8,
            "time_spent_minutes": 25,
            "emails_sent": 5,
            "emails_opened": 4,
            "links_clicked": 2
        },
        "profile_data": {
            "job_title": "Director of Engineering",
            "company_size": 150,
            "industry": "Software"
        }
    }
    score = scorer.calculate_score(example_lead)
    print(f"Lead Qualification Score: {score:.2f}")
