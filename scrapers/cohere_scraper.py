"""
Cohere API scraper
Fetches models from Cohere API (requires API key)
Source: https://api.cohere.com/v1/models
"""

import requests
import os
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CohereScraper(BaseScraper):
    """Scraper for Cohere models (requires COHERE_API_KEY environment variable)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.cohere_config = config.get('data_sources', {}).get('cohere', {})
        self.api_url = self.cohere_config.get('api_url', 'https://api.cohere.com/v1/models')
        self.api_key = os.environ.get('COHERE_API_KEY', self.cohere_config.get('api_key', ''))
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from Cohere API
        
        Returns:
            List of model dictionaries
        """
        if not self.cohere_config.get('enabled', False):
            logger.info("Cohere scraper is disabled")
            return []
            
        if not self.api_key:
            logger.warning("Cohere API key not found. Skipping Cohere scraper.")
            logger.info("Set COHERE_API_KEY environment variable to enable Cohere scraper")
            return []
            
        models = []
        
        try:
            logger.info("Fetching Cohere models")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(self.api_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            model_list = data.get('models', [])
            
            for model_data in model_list:
                model = self._parse_model(model_data)
                if model:
                    models.append(model)
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Cohere API authentication failed. Please check your API key.")
            else:
                logger.error(f"HTTP error scraping Cohere: {e}")
        except Exception as e:
            logger.error(f"Error scraping Cohere: {e}")
            
        logger.info(f"Scraped {len(models)} models from Cohere")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse Cohere model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_name = model_data.get('name', '')
            endpoints = model_data.get('endpoints', [])
            
            # Determine task types based on endpoints
            task_types = []
            for endpoint in endpoints:
                endpoint_lower = endpoint.lower()
                if 'generate' in endpoint_lower or 'chat' in endpoint_lower:
                    task_types.append('text-generation')
                elif 'embed' in endpoint_lower:
                    task_types.append('embeddings')
                elif 'classify' in endpoint_lower:
                    task_types.append('text-classification')
                elif 'summarize' in endpoint_lower:
                    task_types.append('summarization')
            
            # Remove duplicates
            task_types = list(set(task_types))
            
            if not task_types:
                task_types = ['other']
            
            description = f"Endpoints: {', '.join(endpoints)}" if endpoints else ''
            
            model = {
                'name': model_name,
                'version': 'N/A',
                'release_date': '',
                'last_updated': '',
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': 'https://docs.cohere.com/docs/models',
                'source_url': 'https://docs.cohere.com/docs/models',
                'platform': 'Cohere',
                'status': 'active',
                'description': description[:200],
                'downloads': 0,
                'stars': 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing Cohere model: {e}")
            return None
