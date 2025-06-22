# ContentFabric-AI

ContentFabric-AI is an agentic system for automated content scraping, AI-assisted writing and review, human-in-the-loop workflows, versioning with ChromaDB, and reinforcement learning-based search.

## Features
- **Web Scraping:** Automated data collection using Playwright.
- **AI Writing & Review:** Content generation and review using Gemini LLM.
- **Human-in-the-Loop:** Manual review and approval steps.
- **Versioning:** Content and data versioning with ChromaDB.
- **RL Search:** Reinforcement learning-based search for improved results.

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/dxtprashant07/ContentFabric-AI.git
   cd ContentFabric-AI
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   python -m playwright install
   ```

3. **Configure environment variables:**
   - Copy `config.env.example` to `.env` and fill in your API keys and settings.

4. **Run the application:**
   ```sh
   python main.py
   ```

## Usage

- Use the web interface to start scraping, generate content, and review outputs.
- Refer to `CONFIGURATION.md` for advanced settings.

## Project Structure

- `src/` - Main source code
- `data/` - Data storage
- `tests/` - Test cases

## License

MIT License 