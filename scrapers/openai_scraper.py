"""
OpenAI API scraper
Fetches models from OpenAI API (requires API key)
Source: https://api.openai.com/v1/models
"""

import requests
import os
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class OpenAIScraper(BaseScraper):
    """Scraper for OpenAI models (requires OPENAI_API_KEY environment variable)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.openai_config = config.get('data_sources', {}).get('openai', {})
        self.api_url = self.openai_config.get('api_url', 'https://api.openai.com/v1/models')
        self.api_key = os.environ.get('OPENAI_API_KEY', self.openai_config.get('api_key', ''))
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from OpenAI API
        
        Returns:
            List of model dictionaries
        """
        if not self.openai_config.get('enabled', False):
            logger.info("OpenAI scraper is disabled")
            return []
            
        if not self.api_key:
            logger.warning("OpenAI API key not found. Skipping OpenAI scraper.")
            logger.info("Set OPENAI_API_KEY environment variable to enable OpenAI scraper")
            return []
            
        models = []
        
        try:
            logger.info("Fetching OpenAI models")
            
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
                logger.error("OpenAI API authentication failed. Please check your API key.")
            else:
                logger.error(f"HTTP error scraping OpenAI: {e}")
        except Exception as e:
            logger.error(f"Error scraping OpenAI: {e}")
            
        logger.info(f"Scraped {len(models)} models from OpenAI")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse OpenAI model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_id = model_data.get('id', '')
            created = model_data.get('created', 0)
            owned_by = model_data.get('owned_by', 'openai')
            
            # Convert timestamp to ISO format
            release_date = ''
            if created:
                try:
                    release_date = datetime.fromtimestamp(created).isoformat()
                except (ValueError, TypeError):
                    pass
            
            # Determine task types based on model ID
            task_types = []
            model_id_lower = model_id.lower()
            if 'gpt' in model_id_lower or 'chat' in model_id_lower:
                task_types.append('text-generation')
            elif 'embed' in model_id_lower:
                task_types.append('embeddings')
            elif 'whisper' in model_id_lower:
                task_types.append('speech-recognition')
            elif 'dall-e' in model_id_lower or 'dalle' in model_id_lower:
                task_types.append('image-generation')
            elif 'tts' in model_id_lower:
                task_types.append('text-to-speech')
            else:
                task_types.append('other')
            
            description = f"Owner: {owned_by}"
            
            model = {
                'name': model_id,
                'version': 'N/A',
                'release_date': release_date,
                'last_updated': release_date,
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': f"https://platform.openai.com/docs/models/{model_id}",
                'source_url': 'https://platform.openai.com/docs/models',
                'platform': 'OpenAI',
                'status': 'active',
                'description': description,
                'downloads': 0,
                'stars': 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI model: {e}")
            return None
