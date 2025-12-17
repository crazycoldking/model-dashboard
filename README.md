# AI Model Monitoring Dashboard

🤖 A real-time monitoring dashboard for AI models across major platforms including Hugging Face, GitHub, and ModelScope.

## Features

- **Multi-Platform Scraping**: Automatically collects model information from:
  - **LiteLLM** - Community-maintained list of 1000+ models with deprecation dates
  - **Hugging Face Hub** - Top 10k models by downloads
  - **GitHub** - AI repositories with high stars
  - **Alibaba ModelScope**
  - **Provider APIs** (optional, requires API keys):
    - OpenAI
    - Anthropic (Claude)
    - Mistral AI
    - Google Gemini
    - Cohere
  
- **Comprehensive Model Data**: Tracks essential information including:
  - Model name and version
  - Release date and last update
  - Task types (classification, generation, prediction, etc.)
  - Parameter count
  - Documentation links
  - Status (active/deprecated based on update frequency)
  - Stars/likes and download counts

- **Smart Deprecation Detection**: Automatically identifies deprecated models based on:
  - Keywords in description (deprecated, obsolete, archived, etc.)
  - No updates in the last 6 months
  
- **Automated Workflow**: Daily automated scraping via GitHub Actions
  
- **Interactive Dashboard**: Clean, responsive UI with:
  - Filtering by platform, status, and task type
  - Search functionality
  - Sorting options (by update time, stars, downloads, name)
  - Pagination for better performance
  - Real-time statistics

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/crazycoldking/model-dashboard.git
cd model-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scraper:
```bash
python scrape_models.py
```

### Configuration

Edit `config.yaml` to customize:
- Data sources (enable/disable platforms)
- Scraping parameters (models per page, max pages)
- Deprecation criteria
- Task type mappings
- Output settings

Example configuration:
```yaml
data_sources:
  # LiteLLM - Community-maintained list
  litellm:
    enabled: true
  
  # Hugging Face - Top 10k models
  huggingface:
    enabled: true
    models_per_page: 100
    max_models: 10000
  
  github:
    enabled: true
    min_stars: 1000
    
  modelscope:
    enabled: true
  
  # Provider APIs (optional, requires API keys)
  openai:
    enabled: false  # Set to true and provide API key
  
  anthropic:
    enabled: false  # Set to true and provide API key
  
  mistral:
    enabled: false  # Set to true and provide API key
  
  gemini:
    enabled: false  # Set to true and provide API key
  
  cohere:
    enabled: false  # Set to true and provide API key
```

### GitHub Actions Setup

The dashboard automatically updates daily via GitHub Actions:

1. **Scrape Models**: Runs daily at 00:00 UTC (`.github/workflows/scrape-models.yml`)
2. **Deploy Pages**: Deploys to GitHub Pages on data updates (`.github/workflows/deploy-pages.yml`)

To set up GitHub Pages:
1. Go to repository Settings > Pages
2. Select "GitHub Actions" as the source
3. The dashboard will be available at `https://crazycoldking.github.io/model-dashboard/`

## Data Sources

The dashboard fetches model data from multiple sources:

### 1. LiteLLM
- **Source**: https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json
- **Description**: Community-maintained list of 1000+ models with deprecation dates
- **Data**: Model pricing, context windows, deprecation information
- **Configuration**: Always enabled by default

### 2. HuggingFace API
- **Source**: https://huggingface.co/api/models
- **Description**: Top 10k models by downloads
- **Data**: Model metadata, task types, downloads, stars
- **Configuration**: Fetches up to 10,000 models (configurable)

### 3. Provider APIs (Optional)
Requires API keys to enable:

#### OpenAI
- **API**: https://api.openai.com/v1/models
- **Env Variable**: `OPENAI_API_KEY`

#### Anthropic (Claude)
- **API**: https://api.anthropic.com/v1/models
- **Env Variable**: `ANTHROPIC_API_KEY`

#### Mistral AI
- **API**: https://api.mistral.ai/v1/models
- **Env Variable**: `MISTRAL_API_KEY`

#### Google Gemini
- **API**: https://generativelanguage.googleapis.com/v1beta/models
- **Env Variable**: `GEMINI_API_KEY`

#### Cohere
- **API**: https://api.cohere.com/v1/models
- **Env Variable**: `COHERE_API_KEY`

## Project Structure

```
model-dashboard/
├── scrapers/               # Scraper modules
│   ├── __init__.py
│   ├── base_scraper.py    # Base scraper class
│   ├── huggingface_scraper.py
│   ├── github_scraper.py
│   ├── modelscope_scraper.py
│   ├── litellm_scraper.py
│   ├── openai_scraper.py
│   ├── anthropic_scraper.py
│   ├── mistral_scraper.py
│   ├── gemini_scraper.py
│   └── cohere_scraper.py
├── docs/                   # GitHub Pages site
│   ├── index.html         # Dashboard UI
│   ├── style.css          # Styling
│   └── app.js             # Frontend logic
├── data/                   # Generated data
│   └── models.json        # Scraped model data
├── .github/
│   └── workflows/         # GitHub Actions
│       ├── scrape-models.yml
│       └── deploy-pages.yml
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── scrape_models.py       # Main scraper script
└── README.md

```

## Extending the Dashboard

### Adding a New Data Source

1. Create a new scraper class in `scrapers/`:

```python
from .base_scraper import BaseScraper

class NewPlatformScraper(BaseScraper):
    def scrape(self):
        # Implement scraping logic
        models = []
        # ... fetch and parse models
        return self.clean_data(models)
```

2. Update `scrapers/__init__.py`:
```python
from .new_platform_scraper import NewPlatformScraper
__all__ = [..., 'NewPlatformScraper']
```

3. Add configuration in `config.yaml`:
```yaml
data_sources:
  new_platform:
    enabled: true
    # ... platform-specific settings
```

4. Register in `scrape_models.py`:
```python
from scrapers import NewPlatformScraper
scrapers = [
    # ...
    NewPlatformScraper(config),
]
```

### Customizing Deprecation Logic

Modify `base_scraper.py`:
```python
def is_deprecated(self, last_updated, description):
    # Add custom logic
    pass
```

## Data Format

Models are stored in `data/models.json`:
```json
{
  "last_updated": "2024-01-01T00:00:00",
  "total_models": 100,
  "models": [
    {
      "name": "model-name",
      "version": "1.0",
      "release_date": "2024-01-01T00:00:00",
      "last_updated": "2024-01-01T00:00:00",
      "task_types": ["text-generation"],
      "parameters": "7B",
      "documentation_url": "https://...",
      "source_url": "https://...",
      "platform": "Hugging Face",
      "status": "active",
      "description": "...",
      "downloads": 10000,
      "stars": 500
    }
  ]
}
```

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper
python scrape_models.py

# Serve the dashboard locally
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token (for higher API rate limits)
- `OPENAI_API_KEY`: OpenAI API key (optional, for OpenAI scraper)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional, for Anthropic scraper)
- `MISTRAL_API_KEY`: Mistral API key (optional, for Mistral scraper)
- `GEMINI_API_KEY`: Google Gemini API key (optional, for Gemini scraper)
- `COHERE_API_KEY`: Cohere API key (optional, for Cohere scraper)

To use provider API scrapers:
1. Obtain API keys from respective providers
2. Set the environment variables or configure them in `config.yaml`
3. Enable the scrapers in `config.yaml` by setting `enabled: true`

Example:
```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
python scrape_models.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- Data sourced from Hugging Face, GitHub, and ModelScope
- Built with Python, vanilla JavaScript, and GitHub Actions