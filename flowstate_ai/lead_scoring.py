import numpy as np

class LeadScorer:
    """
    AI-powered lead qualification and scoring system based on engagement metrics.
    """

    def __init__(self, weights=None):
        """
        Initialize the LeadScorer with optional weights for each metric.
        
        weights: dict with keys as metric names and values as weight floats.
        Defaults provided for common engagement metrics.
        """
        # Default weights if none provided
        self.weights = weights or {
            'email_open_rate': 0.3,
            'click_through_rate': 0.4,
            'website_visits': 0.2,
            'time_on_site': 0.1,
            # Add more metrics as needed
        }

    def score(self, engagement_data):
        """
        Calculate lead score based on engagement metrics.
        
        engagement_data: dict containing engagement metrics with keys matching self.weights
        
        Returns a float lead score between 0 and 100.
        """
        # Normalize metrics to [0,1] if needed
        # For this example, assume inputs are already normalized or raw numbers that we will scale

        # Example normalization thresholds (could be tuned or learned):
        normalization_params = {
            'email_open_rate': (0, 1),          # Already ratio
            'click_through_rate': (0, 1),       # Already ratio
            'website_visits': (0, 20),          # Typical visits cap
            'time_on_site': (0, 600),           # seconds, cap at 10 minutes
        }

        score_components = []
        total_weight = 0

        for metric, weight in self.weights.items():
            value = engagement_data.get(metric, 0)
            min_val, max_val = normalization_params.get(metric, (0, 1))
            # Clip value
            clipped = max(min_val, min(value, max_val))
            # Normalize to 0-1
            norm = (clipped - min_val) / (max_val - min_val) if max_val > min_val else 0
            score_components.append(norm * weight)
            total_weight += weight

        # Weighted sum
        raw_score = sum(score_components) / total_weight if total_weight > 0 else 0

        # Scale to 0-100
        lead_score = raw_score * 100

        return round(lead_score, 2)


if __name__ == '__main__':
    # Example usage
    scorer = LeadScorer()
    example_lead = {
        'email_open_rate': 0.75,        # 75% open rate
        'click_through_rate': 0.2,      # 20% CTR
        'website_visits': 10,           # 10 visits
        'time_on_site': 300,            # 5 minutes
    }
    score = scorer.score(example_lead)
    print(f'Lead Score: {score}')
