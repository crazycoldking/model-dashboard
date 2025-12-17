"""
Hugging Face model scraper
Scrapes top 10k models from Hugging Face Hub by downloads
"""

import requests
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HuggingFaceScraper(BaseScraper):
    """Scraper for Hugging Face models - fetches top 10k models by downloads"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.hf_config = config.get('data_sources', {}).get('huggingface', {})
        self.base_url = self.hf_config.get('base_url', 'https://huggingface.co')
        self.api_url = self.hf_config.get('api_url', 'https://huggingface.co/api')
        self.models_per_page = self.hf_config.get('models_per_page', 100)
        self.max_models = self.hf_config.get('max_models', 10000)
        
    def scrape(self) -> List[Dict]:
        """
        Scrape top 10k models from Hugging Face by downloads
        
        Returns:
            List of model dictionaries
        """
        if not self.hf_config.get('enabled', True):
            logger.info("Hugging Face scraper is disabled")
            return []
            
        models = []
        
        try:
            # Fetch popular models (sorted by downloads) - top 10k
            url = f"{self.api_url}/models"
            params = {
                'sort': 'downloads',
                'direction': -1,
                'limit': self.models_per_page,
            }
            
            page = 0
            while len(models) < self.max_models:
                page += 1
                logger.info(f"Fetching Hugging Face models page {page} (total: {len(models)}/{self.max_models})")
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                page_models = response.json()
                
                if not page_models:
                    logger.info("No more models available")
                    break
                    
                for model_data in page_models:
                    model = self._parse_model(model_data)
                    if model:
                        models.append(model)
                        if len(models) >= self.max_models:
                            logger.info(f"Reached max_models limit of {self.max_models}")
                            break
                
                # Check if we've reached max_models after processing all models in this page
                if len(models) >= self.max_models:
                    break
                
                # Update offset for next page
                if len(page_models) < self.models_per_page:
                    logger.info("Reached last page")
                    break
                    
                params['skip'] = page * self.models_per_page
                
        except Exception as e:
            logger.error(f"Error scraping Hugging Face: {e}")
            
        logger.info(f"Scraped {len(models)} models from Hugging Face")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse Hugging Face model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_id = model_data.get('id', model_data.get('modelId', ''))
            
            # Parse last modified date
            last_modified = model_data.get('lastModified', '')
            last_updated = None
            if last_modified:
                try:
                    last_updated = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
            
            # Parse tags to extract task types
            tags = model_data.get('tags', [])
            pipeline_tag = model_data.get('pipeline_tag', '')
            task_types = []
            
            if pipeline_tag:
                task_types.append(pipeline_tag)
            
            # Extract task-related tags
            task_keywords = ['classification', 'generation', 'detection', 'segmentation', 
                           'translation', 'summarization', 'question-answering']
            for tag in tags:
                tag_lower = tag.lower()
                for keyword in task_keywords:
                    if keyword in tag_lower and tag_lower not in task_types:
                        task_types.append(tag_lower)
            
            if not task_types:
                task_types = ['other']
            
            # Get model description
            description = model_data.get('description', '') or ''
            
            # Check deprecation status
            is_deprecated = self.is_deprecated(last_updated, description)
            status = 'deprecated' if is_deprecated else 'active'
            
            # Get download count
            downloads = model_data.get('downloads', 0) or 0
            
            model = {
                'name': model_id,
                'version': 'N/A',
                'release_date': last_modified,
                'last_updated': last_modified,
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': f"{self.base_url}/{model_id}",
                'source_url': f"{self.base_url}/{model_id}",
                'platform': 'Hugging Face',
                'status': status,
                'description': description[:200] if description else '',
                'downloads': downloads,
                'stars': model_data.get('likes', 0) or 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing Hugging Face model: {e}")
            return None
