"""
AI Model Scrapers Package
Provides scrapers for different AI model platforms
"""

from .base_scraper import BaseScraper
from .huggingface_scraper import HuggingFaceScraper
from .github_scraper import GitHubScraper
from .modelscope_scraper import ModelScopeScraper

__all__ = [
    'BaseScraper',
    'HuggingFaceScraper',
    'GitHubScraper',
    'ModelScopeScraper',
]
