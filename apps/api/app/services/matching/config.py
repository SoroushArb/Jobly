"""Configuration for job matching and scoring"""
import os
from typing import Dict


class MatchConfig:
    """Configuration for matching and scoring"""
    
    # Default component weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "semantic": 0.35,
        "skill_overlap": 0.25,
        "seniority_fit": 0.15,
        "location_fit": 0.15,
        "recency": 0.10,
    }
    
    # Seniority level mappings
    SENIORITY_LEVELS = {
        "junior": 1,
        "mid": 2,
        "senior": 3,
        "staff": 4,
        "lead": 4,
        "principal": 5,
        "architect": 5,
    }
    
    # Keywords for seniority detection in titles
    JUNIOR_KEYWORDS = ["junior", "jr", "entry", "graduate", "intern", "associate"]
    MID_KEYWORDS = ["mid", "intermediate", "ii", "2"]
    SENIOR_KEYWORDS = ["senior", "sr", "iii", "3", "iv", "4"]
    LEAD_KEYWORDS = ["lead", "staff", "principal", "architect", "director", "head"]
    
    # Recency decay (days)
    RECENCY_DECAY_DAYS = 90  # Jobs posted more than 90 days ago get lower score
    
    @classmethod
    def get_weights(cls) -> Dict[str, float]:
        """Get scoring weights from environment or use defaults"""
        weights = {}
        
        # Try to read from environment variables
        for component in cls.DEFAULT_WEIGHTS.keys():
            env_key = f"MATCH_WEIGHT_{component.upper()}"
            env_value = os.getenv(env_key)
            
            if env_value:
                try:
                    weights[component] = float(env_value)
                except ValueError:
                    weights[component] = cls.DEFAULT_WEIGHTS[component]
            else:
                weights[component] = cls.DEFAULT_WEIGHTS[component]
        
        # Normalize to ensure they sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
