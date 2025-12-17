"""
ModelScope scraper for Alibaba's model platform
Scrapes models from ModelScope
"""

import requests
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ModelScopeScraper(BaseScraper):
    """Scraper for ModelScope models"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.ms_config = config.get('data_sources', {}).get('modelscope', {})
        self.base_url = self.ms_config.get('base_url', 'https://modelscope.cn')
        self.api_url = self.ms_config.get('api_url', 'https://modelscope.cn/api/v1')
        self.models_per_page = self.ms_config.get('models_per_page', 20)
        self.max_pages = self.ms_config.get('max_pages', 5)
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from ModelScope
        
        Returns:
            List of model dictionaries
        """
        if not self.ms_config.get('enabled', True):
            logger.info("ModelScope scraper is disabled")
            return []
            
        models = []
        
        try:
            # Try to fetch models from ModelScope
            # Note: This is a basic implementation as ModelScope API may require authentication
            url = f"{self.api_url}/models"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            for page in range(1, self.max_pages + 1):
                logger.info(f"Fetching ModelScope models page {page}/{self.max_pages}")
                
                params = {
                    'Page': page,
                    'PageSize': self.models_per_page,
                }
                
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    
                    # If API doesn't work, return empty list gracefully
                    if response.status_code == 404:
                        logger.warning("ModelScope API endpoint not accessible, skipping")
                        break
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    page_models = data.get('Data', {}).get('Models', [])
                    
                    if not page_models:
                        break
                        
                    for model_data in page_models:
                        model = self._parse_model(model_data)
                        if model:
                            models.append(model)
                            
                    if len(page_models) < self.models_per_page:
                        break
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"ModelScope API not accessible: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping ModelScope: {e}")
            
        logger.info(f"Scraped {len(models)} models from ModelScope")
        return self.clean_data(models)
    
    def _parse_model(self, model_data: Dict) -> Dict:
        """
        Parse ModelScope model data
        
        Args:
            model_data: Raw model data from API
            
        Returns:
            Normalized model dictionary
        """
        try:
            model_id = model_data.get('Id', model_data.get('Name', ''))
            
            # Parse update time
            updated_time = model_data.get('GmtModified', model_data.get('UpdatedTime', ''))
            last_updated = None
            if updated_time:
                try:
                    last_updated = datetime.fromisoformat(updated_time.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
            
            # Get task types
            task = model_data.get('Task', '')
            tags = model_data.get('Tags', [])
            task_types = []
            
            if task:
                task_types.append(task.lower())
            
            for tag in tags:
                if isinstance(tag, str) and tag.lower() not in task_types:
                    task_types.append(tag.lower())
            
            if not task_types:
                task_types = ['other']
            
            # Get description
            description = model_data.get('Description', '') or ''
            
            # Check deprecation status
            is_deprecated = self.is_deprecated(last_updated, description)
            status = 'deprecated' if is_deprecated else 'active'
            
            model = {
                'name': model_id,
                'version': model_data.get('Version', 'N/A'),
                'release_date': model_data.get('GmtCreate', ''),
                'last_updated': updated_time,
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': f"{self.base_url}/models/{model_id}",
                'source_url': f"{self.base_url}/models/{model_id}",
                'platform': 'ModelScope',
                'status': status,
                'description': description[:200] if description else '',
                'downloads': model_data.get('Downloads', 0) or 0,
                'stars': model_data.get('Stars', 0) or 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing ModelScope model: {e}")
            return None
