"""
GitHub repository scraper for AI models
Scrapes popular AI repositories from GitHub
"""

import os
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class GitHubScraper(BaseScraper):
    """Scraper for GitHub AI repositories"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.github_config = config.get('data_sources', {}).get('github', {})
        self.min_stars = self.github_config.get('min_stars', 1000)
        self.topics = self.github_config.get('topics', [])
        self.max_repos = self.github_config.get('max_repos', 100)
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
        
    def scrape(self) -> List[Dict]:
        """
        Scrape AI repositories from GitHub
        
        Returns:
            List of model dictionaries
        """
        if not self.github_config.get('enabled', True):
            logger.info("GitHub scraper is disabled")
            return []
            
        models = []
        
        try:
            # Use PyGithub if token available, otherwise use REST API
            if self.github_token:
                models = self._scrape_with_pygithub()
            else:
                models = self._scrape_with_rest_api()
                
        except Exception as e:
            logger.error(f"Error scraping GitHub: {e}")
            
        logger.info(f"Scraped {len(models)} repositories from GitHub")
        return self.clean_data(models)
    
    def _scrape_with_pygithub(self) -> List[Dict]:
        """Scrape using PyGithub library"""
        from github import Github
        
        models = []
        g = Github(self.github_token)
        
        for topic in self.topics[:3]:  # Limit topics to avoid rate limiting
            try:
                logger.info(f"Searching GitHub for topic: {topic}")
                
                query = f"topic:{topic} stars:>={self.min_stars}"
                repositories = g.search_repositories(query=query, sort='stars', order='desc')
                
                for repo in repositories[:self.max_repos // len(self.topics)]:
                    model = self._parse_repository(repo)
                    if model:
                        models.append(model)
                        
            except Exception as e:
                logger.error(f"Error searching GitHub topic {topic}: {e}")
                
        return models
    
    def _scrape_with_rest_api(self) -> List[Dict]:
        """Scrape using GitHub REST API"""
        import requests
        
        models = []
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        for topic in self.topics[:3]:  # Limit topics
            try:
                logger.info(f"Searching GitHub for topic: {topic}")
                
                url = "https://api.github.com/search/repositories"
                params = {
                    'q': f"topic:{topic} stars:>={self.min_stars}",
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': min(30, self.max_repos // len(self.topics))
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                for repo_data in items:
                    model = self._parse_repository_dict(repo_data)
                    if model:
                        models.append(model)
                        
            except Exception as e:
                logger.error(f"Error searching GitHub topic {topic}: {e}")
                
        return models
    
    def _parse_repository(self, repo) -> Dict:
        """Parse GitHub repository object from PyGithub"""
        try:
            # Get last update time
            last_updated = repo.updated_at if hasattr(repo, 'updated_at') else None
            
            # Get description
            description = repo.description or ''
            
            # Check deprecation
            is_deprecated = repo.archived or self.is_deprecated(last_updated, description)
            status = 'deprecated' if is_deprecated else 'active'
            
            # Determine task types from topics and description
            topics = list(repo.get_topics()) if hasattr(repo, 'get_topics') else []
            task_types = self._extract_task_types(topics, description)
            
            model = {
                'name': repo.full_name,
                'version': 'N/A',
                'release_date': repo.created_at.isoformat() if repo.created_at else '',
                'last_updated': last_updated.isoformat() if last_updated else '',
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': repo.html_url,
                'source_url': repo.html_url,
                'platform': 'GitHub',
                'status': status,
                'description': description[:200] if description else '',
                'downloads': 0,
                'stars': repo.stargazers_count or 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing GitHub repository: {e}")
            return None
    
    def _parse_repository_dict(self, repo_data: Dict) -> Dict:
        """Parse GitHub repository from REST API response"""
        try:
            # Get last update time
            updated_at = repo_data.get('updated_at', '')
            last_updated = None
            if updated_at:
                try:
                    last_updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
            
            # Get description
            description = repo_data.get('description', '') or ''
            
            # Check deprecation
            is_archived = repo_data.get('archived', False)
            is_deprecated = is_archived or self.is_deprecated(last_updated, description)
            status = 'deprecated' if is_deprecated else 'active'
            
            # Determine task types from topics and description
            topics = repo_data.get('topics', [])
            task_types = self._extract_task_types(topics, description)
            
            created_at = repo_data.get('created_at', '')
            
            model = {
                'name': repo_data.get('full_name', ''),
                'version': 'N/A',
                'release_date': created_at,
                'last_updated': updated_at,
                'task_types': task_types,
                'parameters': 'N/A',
                'documentation_url': repo_data.get('html_url', ''),
                'source_url': repo_data.get('html_url', ''),
                'platform': 'GitHub',
                'status': status,
                'description': description[:200] if description else '',
                'downloads': 0,
                'stars': repo_data.get('stargazers_count', 0) or 0,
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing GitHub repository dict: {e}")
            return None
    
    def _extract_task_types(self, topics: List[str], description: str) -> List[str]:
        """Extract task types from topics and description"""
        task_types = set()
        
        # Map keywords to task types
        task_mapping = {
            'classification': 'classification',
            'generation': 'generation',
            'nlp': 'text-generation',
            'computer-vision': 'image-classification',
            'object-detection': 'object-detection',
            'translation': 'translation',
            'summarization': 'summarization',
            'question-answering': 'question-answering',
            'speech': 'speech-recognition',
            'text-to-speech': 'text-to-speech',
            'llm': 'text-generation',
            'transformer': 'text-generation',
        }
        
        # Check topics
        for topic in topics:
            topic_lower = topic.lower()
            for keyword, task_type in task_mapping.items():
                if keyword in topic_lower:
                    task_types.add(task_type)
        
        # Check description
        if description:
            desc_lower = description.lower()
            for keyword, task_type in task_mapping.items():
                if keyword in desc_lower:
                    task_types.add(task_type)
        
        return list(task_types) if task_types else ['other']
