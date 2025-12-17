"""
Mistral API scraper
Fetches models from Mistral API (requires API key)
Source: https://api.mistral.ai/v1/models
"""

import requests
import os
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MistralScraper(BaseScraper):
    """Scraper for Mistral models (requires MISTRAL_API_KEY environment variable)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.mistral_config = config.get('data_sources', {}).get('mistral', {})
        self.api_url = self.mistral_config.get('api_url', 'https://api.mistral.ai/v1/models')
        self.api_key = os.environ.get('MISTRAL_API_KEY', self.mistral_config.get('api_key', ''))
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from Mistral API
        
        Returns:
            List of model dictionaries
        """
        if not self.mistral_config.get('enabled', False):
            logger.info("Mistral scraper is disabled")
            return []
            
        if not self.api_key:
            logger.warning("Mistral API key not found. Skipping Mistral scraper.")
            logger.info("Set MISTRAL_API_KEY environment variable to enable Mistral scraper")
            return []
            
        models = []
        
        try:
            logger.info("Fetching Mistral models")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(self.api_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            model_list = data.get('data', [])
            
            for model_data in model_list:
                model = self._parse_model(model_data)
                if model:
                    models.append(model)
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Mistral API authentication failed. Please check your API key.")
            else:
                logger.error(f"HTTP error scraping Mistral: {e}")
        except Exception as e:
            logger.error(f"Error scraping Mistral: {e}")
            
        logger.info(f"Scraped {len(models)} models from Mistral")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse Mistral model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_id = model_data.get('id', '')
            created = model_data.get('created', 0)
            owned_by = model_data.get('owned_by', 'mistralai')
            
            # Convert timestamp to ISO format
            release_date = ''
            if created:
                try:
                    release_date = datetime.fromtimestamp(created).isoformat()
                except (ValueError, TypeError):
                    pass
            
            # Mistral models are primarily text-generation
            task_types = ['text-generation']
            
            description = f"Owner: {owned_by}" if owned_by else ''
            
            model = {
                'name': model_id,
                'version': 'N/A',
                'release_date': release_date,
                'last_updated': release_date,
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': 'https://docs.mistral.ai/getting-started/models/',
                'source_url': 'https://docs.mistral.ai/getting-started/models/',
                'platform': 'Mistral',
                'status': 'active',
                'description': description,
                'downloads': 0,
                'stars': 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing Mistral model: {e}")
            return None
