# Configuration Guide

## Environment Variables

Copy `config.env.example` to `.env` and set the following variables:

- `GOOGLE_API_KEY`: Your Gemini API key.
- `CHROMA_DB_PATH`: Path for ChromaDB storage.
- `PLAYWRIGHT_BROWSER`: Browser to use for scraping (e.g., chromium).

## Advanced Settings

- Adjust scraping parameters in `src/scrapers/web_scraper.py`.
- Modify agent behavior in `src/ai_agents/`.

## Troubleshooting

- If you encounter import errors, ensure all dependencies are installed and your IDE recognizes the environment.
- For Playwright issues, run:
  ```sh
  python -m playwright install
  ``` 