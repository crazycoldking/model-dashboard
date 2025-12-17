#!/usr/bin/env python3
"""
Main script to scrape AI models from various platforms
"""

import json
import yaml
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict

from scrapers import (
    HuggingFaceScraper, 
    GitHubScraper, 
    ModelScopeScraper,
    LiteLLMScraper,
    OpenAIScraper,
    AnthropicScraper,
    MistralScraper,
    GeminiScraper,
    CohereScraper
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.yaml') -> Dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_models(models: List[Dict], output_path: str):
    """Save models to JSON file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add metadata
    data = {
        'last_updated': datetime.now().isoformat(),
        'total_models': len(models),
        'models': models
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(models)} models to {output_path}")


def merge_with_existing(new_models: List[Dict], existing_path: str) -> List[Dict]:
    """Merge new models with existing data"""
    existing_models = []
    
    if os.path.exists(existing_path):
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_models = data.get('models', [])
            logger.info(f"Loaded {len(existing_models)} existing models")
        except Exception as e:
            logger.error(f"Error loading existing models: {e}")
    
    # Create a map of existing models by (name, platform)
    existing_map = {}
    for model in existing_models:
        key = (model.get('name'), model.get('platform'))
        existing_map[key] = model
    
    # Update with new models
    for model in new_models:
        key = (model.get('name'), model.get('platform'))
        existing_map[key] = model
    
    # Convert back to list
    merged = list(existing_map.values())
    
    # Sort by last_updated (most recent first)
    merged.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
    
    logger.info(f"Merged to {len(merged)} total models")
    return merged


def main():
    """Main scraping function"""
    logger.info("Starting AI model scraping...")
    
    # Load configuration
    config = load_config()
    
    # Initialize scrapers
    scrapers = [
        HuggingFaceScraper(config),
        GitHubScraper(config),
        ModelScopeScraper(config),
        LiteLLMScraper(config),
        OpenAIScraper(config),
        AnthropicScraper(config),
        MistralScraper(config),
        GeminiScraper(config),
        CohereScraper(config),
    ]
    
    # Scrape from all sources
    all_models = []
    for scraper in scrapers:
        try:
            logger.info(f"Running {scraper.__class__.__name__}...")
            models = scraper.scrape()
            all_models.extend(models)
        except Exception as e:
            logger.error(f"Error running {scraper.__class__.__name__}: {e}")
    
    logger.info(f"Total models scraped: {len(all_models)}")
    
    # Prepare output path
    output_dir = config.get('output', {}).get('data_dir', 'data')
    output_file = config.get('output', {}).get('models_file', 'models.json')
    output_path = os.path.join(output_dir, output_file)
    
    # Merge with existing data
    merged_models = merge_with_existing(all_models, output_path)
    
    # Save to file
    save_models(merged_models, output_path)
    
    # Print summary statistics
    platforms = {}
    statuses = {}
    for model in merged_models:
        platform = model.get('platform', 'Unknown')
        status = model.get('status', 'Unknown')
        platforms[platform] = platforms.get(platform, 0) + 1
        statuses[status] = statuses.get(status, 0) + 1
    
    logger.info("Summary:")
    logger.info(f"  Total models: {len(merged_models)}")
    logger.info(f"  By platform: {platforms}")
    logger.info(f"  By status: {statuses}")
    
    logger.info("Scraping completed successfully!")


if __name__ == '__main__':
    main()
