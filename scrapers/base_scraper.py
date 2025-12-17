"""
Base scraper class for AI model platforms
Provides common functionality for all scrapers
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for model scrapers"""
    
    def __init__(self, config: Dict):
        """
        Initialize scraper with configuration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.deprecated_months = config.get('model_status', {}).get('deprecated_months', 6)
        self.deprecated_keywords = config.get('model_status', {}).get('deprecated_keywords', [])
        
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrape models from the platform
        
        Returns:
            List of model dictionaries
        """
        pass
    
    def is_deprecated(self, last_updated: Optional[datetime], description: str = "") -> bool:
        """
        Check if a model is deprecated based on last update time and keywords
        
        Args:
            last_updated: Last update datetime
            description: Model description or readme
            
        Returns:
            True if model is deprecated
        """
        # Check for deprecated keywords
        if description:
            description_lower = description.lower()
            for keyword in self.deprecated_keywords:
                if keyword.lower() in description_lower:
                    return True
        
        # Check if no updates in specified months
        if last_updated:
            cutoff_date = datetime.now() - timedelta(days=30 * self.deprecated_months)
            if last_updated < cutoff_date:
                return True
                
        return False
    
    def normalize_model(self, raw_model: Dict) -> Dict:
        """
        Normalize model data to standard format
        
        Args:
            raw_model: Raw model data from platform
            
        Returns:
            Normalized model dictionary
        """
        return {
            'name': raw_model.get('name', ''),
            'version': raw_model.get('version', 'N/A'),
            'release_date': raw_model.get('release_date', ''),
            'last_updated': raw_model.get('last_updated', ''),
            'task_types': raw_model.get('task_types', []),
            'parameters': raw_model.get('parameters', 'N/A'),
            'documentation_url': raw_model.get('documentation_url', ''),
            'source_url': raw_model.get('source_url', ''),
            'platform': raw_model.get('platform', ''),
            'status': raw_model.get('status', 'active'),
            'description': raw_model.get('description', ''),
            'downloads': raw_model.get('downloads', 0),
            'stars': raw_model.get('stars', 0),
        }
    
    def clean_data(self, models: List[Dict]) -> List[Dict]:
        """
        Clean and deduplicate model data
        
        Args:
            models: List of model dictionaries
            
        Returns:
            Cleaned list of models
        """
        # Remove duplicates based on name and platform
        seen = set()
        cleaned = []
        
        for model in models:
            key = (model.get('name', ''), model.get('platform', ''))
            if key not in seen and model.get('name'):
                seen.add(key)
                cleaned.append(model)
                
        logger.info(f"Cleaned {len(models)} models to {len(cleaned)} unique models")
        return cleaned
