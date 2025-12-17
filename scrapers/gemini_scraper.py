"""
Gemini API scraper
Fetches models from Google Gemini API (requires API key)
Source: https://generativelanguage.googleapis.com/v1beta/models
"""

import requests
import os
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class GeminiScraper(BaseScraper):
    """Scraper for Google Gemini models (requires GEMINI_API_KEY environment variable)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.gemini_config = config.get('data_sources', {}).get('gemini', {})
        self.api_url = self.gemini_config.get('api_url', 'https://generativelanguage.googleapis.com/v1beta/models')
        self.api_key = os.environ.get('GEMINI_API_KEY', self.gemini_config.get('api_key', ''))
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from Gemini API
        
        Returns:
            List of model dictionaries
        """
        if not self.gemini_config.get('enabled', False):
            logger.info("Gemini scraper is disabled")
            return []
            
        if not self.api_key:
            logger.warning("Gemini API key not found. Skipping Gemini scraper.")
            logger.info("Set GEMINI_API_KEY environment variable to enable Gemini scraper")
            return []
            
        models = []
        
        try:
            logger.info("Fetching Gemini models")
            
            params = {
                'key': self.api_key
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            model_list = data.get('models', [])
            
            for model_data in model_list:
                model = self._parse_model(model_data)
                if model:
                    models.append(model)
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                logger.error("Gemini API authentication failed. Please check your API key.")
            else:
                logger.error(f"HTTP error scraping Gemini: {e}")
        except Exception as e:
            logger.error(f"Error scraping Gemini: {e}")
            
        logger.info(f"Scraped {len(models)} models from Gemini")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse Gemini model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_name = model_data.get('name', '')
            # Extract model ID from name (e.g., "models/gemini-pro" -> "gemini-pro")
            model_id = model_name.split('/')[-1] if '/' in model_name else model_name
            
            display_name = model_data.get('displayName', model_id)
            description = model_data.get('description', '')
            
            supported_methods = model_data.get('supportedGenerationMethods', [])
            
            # Determine task types based on supported methods
            task_types = []
            if 'generateContent' in supported_methods:
                task_types.append('text-generation')
            if 'embedContent' in supported_methods:
                task_types.append('embeddings')
            
            if not task_types:
                task_types = ['multimodal']
            
            # Truncate description to standard 200 characters
            full_description = f"{display_name}"
            if description:
                full_description += f": {description}"
            
            model = {
                'name': model_id,
                'version': 'N/A',
                'release_date': '',
                'last_updated': '',
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': f"https://ai.google.dev/models/{model_id}",
                'source_url': 'https://ai.google.dev/models',
                'platform': 'Gemini',
                'status': 'active',
                'description': full_description[:200] if full_description else '',
                'downloads': 0,
                'stars': 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing Gemini model: {e}")
            return None
