"""
Anthropic API scraper
Fetches models from Anthropic API (requires API key)
Source: https://api.anthropic.com/v1/models
"""

import requests
import os
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AnthropicScraper(BaseScraper):
    """Scraper for Anthropic models (requires ANTHROPIC_API_KEY environment variable)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.anthropic_config = config.get('data_sources', {}).get('anthropic', {})
        self.api_url = self.anthropic_config.get('api_url', 'https://api.anthropic.com/v1/models')
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', self.anthropic_config.get('api_key', ''))
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from Anthropic API
        
        Returns:
            List of model dictionaries
        """
        if not self.anthropic_config.get('enabled', False):
            logger.info("Anthropic scraper is disabled")
            return []
            
        if not self.api_key:
            logger.warning("Anthropic API key not found. Skipping Anthropic scraper.")
            logger.info("Set ANTHROPIC_API_KEY environment variable to enable Anthropic scraper")
            return []
            
        models = []
        
        try:
            logger.info("Fetching Anthropic models")
            
            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'
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
                logger.error("Anthropic API authentication failed. Please check your API key.")
            else:
                logger.error(f"HTTP error scraping Anthropic: {e}")
        except Exception as e:
            logger.error(f"Error scraping Anthropic: {e}")
            
        logger.info(f"Scraped {len(models)} models from Anthropic")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse Anthropic model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_id = model_data.get('id', model_data.get('name', ''))
            created_at = model_data.get('created_at', '')
            display_name = model_data.get('display_name', model_id)
            
            # Determine task types (Claude models are primarily text-generation)
            task_types = ['text-generation']
            
            description = f"Display name: {display_name}" if display_name != model_id else ''
            
            model = {
                'name': model_id,
                'version': 'N/A',
                'release_date': created_at,
                'last_updated': created_at,
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': 'https://docs.anthropic.com/en/docs/models-overview',
                'source_url': 'https://docs.anthropic.com/en/docs/models-overview',
                'platform': 'Anthropic',
                'status': 'active',
                'description': description,
                'downloads': 0,
                'stars': 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing Anthropic model: {e}")
            return None
