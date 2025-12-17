# Contributing to AI Model Monitoring Dashboard

Thank you for your interest in contributing to the AI Model Monitoring Dashboard! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies: `pip install -r requirements.txt`
4. Create a new branch for your feature: `git checkout -b feature/your-feature-name`

## Development Workflow

### Running the Scraper Locally

```bash
python scrape_models.py
```

The scraper will:
- Fetch models from configured data sources
- Clean and deduplicate the data
- Merge with existing data in `data/models.json`
- Save the updated data

### Testing the Dashboard Locally

```bash
cd docs
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## Adding a New Data Source

To add a new AI model platform:

### 1. Create a New Scraper Class

Create a new file in `scrapers/` directory (e.g., `scrapers/new_platform_scraper.py`):

```python
from datetime import datetime
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class NewPlatformScraper(BaseScraper):
    """Scraper for NewPlatform models"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.platform_config = config.get('data_sources', {}).get('new_platform', {})
        # Add platform-specific configuration
        
    def scrape(self) -> List[Dict]:
        """
        Scrape models from NewPlatform
        
        Returns:
            List of model dictionaries
        """
        if not self.platform_config.get('enabled', True):
            logger.info("NewPlatform scraper is disabled")
            return []
            
        models = []
        
        try:
            # Implement your scraping logic here
            # Fetch models from the platform's API or web pages
            pass
            
        except Exception as e:
            logger.error(f"Error scraping NewPlatform: {e}")
            
        logger.info(f"Scraped {len(models)} models from NewPlatform")
        return self.clean_data(models)
    
    def _parse_model(self, raw_data: Dict) -> Dict:
        """
        Parse platform-specific model data into standard format
        
        Args:
            raw_data: Raw model data from platform
            
        Returns:
            Normalized model dictionary
        """
        try:
            # Parse the raw data
            model = {
                'name': raw_data.get('model_name', ''),
                'version': raw_data.get('version', 'N/A'),
                'release_date': raw_data.get('created_at', ''),
                'last_updated': raw_data.get('updated_at', ''),
                'task_types': raw_data.get('tasks', ['other']),
                'parameters': raw_data.get('params', 'N/A'),
                'documentation_url': raw_data.get('url', ''),
                'source_url': raw_data.get('url', ''),
                'platform': 'NewPlatform',
                'status': 'active',  # Or use self.is_deprecated() to determine
                'description': raw_data.get('description', '')[:200],
                'downloads': raw_data.get('downloads', 0),
                'stars': raw_data.get('stars', 0),
            }
            
            return self.normalize_model(model)
            
        except Exception as e:
            logger.error(f"Error parsing model: {e}")
            return None
```

### 2. Update `scrapers/__init__.py`

Add your new scraper to the package:

```python
from .new_platform_scraper import NewPlatformScraper

__all__ = [
    # ... existing scrapers
    'NewPlatformScraper',
]
```

### 3. Add Configuration

Update `config.yaml`:

```yaml
data_sources:
  # ... existing sources
  
  new_platform:
    enabled: true
    base_url: "https://newplatform.example.com"
    api_url: "https://api.newplatform.example.com"
    # Add platform-specific settings
```

### 4. Register the Scraper

Update `scrape_models.py`:

```python
from scrapers import HuggingFaceScraper, GitHubScraper, ModelScopeScraper, NewPlatformScraper

def main():
    # ...
    scrapers = [
        HuggingFaceScraper(config),
        GitHubScraper(config),
        ModelScopeScraper(config),
        NewPlatformScraper(config),  # Add your scraper
    ]
    # ...
```

## Model Data Format

All scrapers should return models in this standard format:

```python
{
    'name': str,              # Model identifier
    'version': str,           # Version number or 'N/A'
    'release_date': str,      # ISO format datetime or empty
    'last_updated': str,      # ISO format datetime or empty
    'task_types': List[str],  # List of task types
    'parameters': str,        # Parameter count (e.g., '7B', '110M') or 'N/A'
    'documentation_url': str, # URL to model documentation
    'source_url': str,        # URL to model source
    'platform': str,          # Platform name
    'status': str,            # 'active' or 'deprecated'
    'description': str,       # Brief description (max 200 chars)
    'downloads': int,         # Download count (0 if not available)
    'stars': int,             # Stars/likes count (0 if not available)
}
```

## Task Types

Use standardized task type names from `config.yaml`:

- `text-classification`
- `text-generation`
- `text-to-text`
- `translation`
- `summarization`
- `question-answering`
- `image-classification`
- `image-generation`
- `image-to-text`
- `object-detection`
- `speech-recognition`
- `text-to-speech`
- `multimodal`
- `reinforcement-learning`
- `other`

## Customizing Deprecation Logic

The base scraper provides a default `is_deprecated()` method. You can override it in your scraper:

```python
def is_deprecated(self, last_updated: Optional[datetime], description: str = "") -> bool:
    """Custom deprecation logic for this platform"""
    # Your custom logic here
    return super().is_deprecated(last_updated, description)
```

## Frontend Development

The dashboard frontend is in the `docs/` directory:

- `index.html` - Main HTML structure
- `style.css` - Styling
- `app.js` - JavaScript logic

To add new features:

1. Update the HTML structure if needed
2. Add corresponding CSS styles
3. Implement the logic in JavaScript
4. Test locally before committing

## Testing

Before submitting a PR:

1. **Test the scraper**: Run `python scrape_models.py` and verify it works
2. **Check the data**: Ensure `data/models.json` has the expected format
3. **Test the dashboard**: Serve locally and test all filters and features
4. **Verify no errors**: Check browser console for JavaScript errors

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to classes and methods
- Include type hints where appropriate
- Add logging for important operations

## Pull Request Process

1. Update the README if you've added new features
2. Update CONTRIBUTING.md if you've changed the development process
3. Ensure all tests pass and the dashboard works correctly
4. Create a pull request with a clear description of changes
5. Link to any related issues

## Issue Reporting

When reporting issues:

1. Use a clear, descriptive title
2. Describe the expected vs actual behavior
3. Include steps to reproduce
4. Add relevant logs or error messages
5. Specify your environment (OS, Python version, etc.)

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing! 🚀
