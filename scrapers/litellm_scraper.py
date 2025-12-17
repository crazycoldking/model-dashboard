"""
LiteLLM model scraper
Fetches community-maintained list of 1000+ models with deprecation dates
Source: https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json
"""

import requests
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class LiteLLMScraper(BaseScraper):
    """Scraper for LiteLLM community-maintained model list"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.litellm_config = config.get('data_sources', {}).get('litellm', {})
        self.json_url = self.litellm_config.get(
            'json_url',
            'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'
        )
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from LiteLLM JSON file
        
        Returns:
            List of model dictionaries
        """
        if not self.litellm_config.get('enabled', True):
            logger.info("LiteLLM scraper is disabled")
            return []
            
        models = []
        
        try:
            logger.info(f"Fetching LiteLLM model data from {self.json_url}")
            
            response = requests.get(self.json_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse the model data
            for model_id, model_data in data.items():
                model = self._parse_model(model_id, model_data)
                if model:
                    models.append(model)
                    
        except Exception as e:
            logger.error(f"Error scraping LiteLLM: {e}")
            
        logger.info(f"Scraped {len(models)} models from LiteLLM")
        return self.clean_data(models)
    
    def _parse_model(self, model_id: str, model_data: Dict) -> Dict:
        """
        Parse LiteLLM model data
        
        Args:
            model_id: Model identifier
            model_data: Raw model data from JSON
            
        Returns:
            Normalized model dictionary
        """
        try:
            # Extract relevant fields
            max_tokens = model_data.get('max_tokens', model_data.get('max_output_tokens', 'N/A'))
            input_cost = model_data.get('input_cost_per_token', 0)
            output_cost = model_data.get('output_cost_per_token', 0)
            litellm_provider = model_data.get('litellm_provider', 'Unknown')
            mode = model_data.get('mode', 'N/A')
            
            # Check for deprecation
            deprecation_date = model_data.get('deprecation_date')
            is_deprecated = False
            status = 'active'
            
            if deprecation_date:
                try:
                    dep_date = datetime.fromisoformat(deprecation_date.replace('Z', '+00:00'))
                    # Ensure both datetimes are timezone-aware for comparison
                    from datetime import timezone
                    if dep_date.tzinfo is None:
                        dep_date = dep_date.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    if dep_date < now:
                        is_deprecated = True
                        status = 'deprecated'
                except (ValueError, TypeError):
                    pass
            
            # Determine task types based on mode
            task_types = []
            if mode:
                if 'chat' in mode.lower():
                    task_types.append('text-generation')
                elif 'embedding' in mode.lower():
                    task_types.append('embeddings')
                elif 'completion' in mode.lower():
                    task_types.append('text-generation')
                else:
                    task_types.append(mode)
            
            if not task_types:
                task_types = ['other']
            
            # Build description
            description_parts = []
            if litellm_provider and litellm_provider != 'Unknown':
                description_parts.append(f"Provider: {litellm_provider}")
            if max_tokens and max_tokens != 'N/A':
                description_parts.append(f"Max tokens: {max_tokens}")
            if input_cost > 0 or output_cost > 0:
                description_parts.append(f"Pricing available")
            if deprecation_date:
                description_parts.append(f"Deprecation: {deprecation_date}")
            
            description = "; ".join(description_parts)
            
            # Build documentation URL (only for known, simple provider names)
            doc_url = ''
            if litellm_provider and litellm_provider != 'Unknown':
                # Only use provider in URL if it's a simple name without special chars
                provider_slug = litellm_provider.lower().replace(' ', '-')
                if provider_slug.replace('-', '').replace('_', '').isalnum():
                    doc_url = f"https://docs.litellm.ai/docs/providers/{provider_slug}"
            
            model = {
                'name': model_id,
                'version': 'N/A',
                'release_date': '',
                'last_updated': deprecation_date if deprecation_date else '',
                'task_types': task_types,
                'parameters': str(max_tokens) if max_tokens != 'N/A' else 'N/A',
                'documentation_url': doc_url,
                'source_url': 'https://github.com/BerriAI/litellm',
                'platform': 'LiteLLM',
                'status': status,
                'description': description[:200] if description else '',
                'downloads': 0,
                'stars': 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing LiteLLM model {model_id}: {e}")
            return None
