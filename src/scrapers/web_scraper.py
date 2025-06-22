import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import json

# Fix for Windows asyncio issues
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import with error handling
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup not installed. Run: pip install beautifulsoup4")
    BeautifulSoup = None

try:
    import requests
except ImportError:
    print("Requests not installed. Run: pip install requests")
    requests = None

try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Run: pip install pillow")
    Image = Any

import io


class SimpleWebScraper:
    """Simple web scraper using requests and BeautifulSoup."""
    
    def __init__(self, screenshots_path: str = "./screenshots"):
        self.screenshots_path = Path(screenshots_path)
        self.screenshots_path.mkdir(exist_ok=True)
        
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL using requests."""
        try:
            if not requests:
                raise ImportError("Requests not available")
                
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            if BeautifulSoup is not None:
                soup = BeautifulSoup(response.content, 'html.parser')
            else:
                soup = None
            
            # Extract text content
            text_content = self._extract_text_content(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            return {
                'url': url,
                'title': metadata.get('title', ''),
                'content': text_content,
                'metadata': metadata,
                'screenshots': [],  # No screenshots with simple scraper
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def _extract_text_content(self, soup: Any) -> str:
        """Extract clean text content from the page."""
        if soup is None:
            return ""
            
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_metadata(self, soup: Any, url: str) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {
            'url': url,
            'title': '',
            'description': '',
            'keywords': [],
            'author': '',
            'language': 'en'
        }
        
        if soup is None:
            return metadata
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and hasattr(meta_desc, 'get'):
            metadata['description'] = meta_desc.get('content', '')
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and hasattr(meta_keywords, 'get'):
            keywords = meta_keywords.get('content', '')
            if isinstance(keywords, str):
                metadata['keywords'] = [k.strip() for k in keywords.split(',')]
        
        # Author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and hasattr(meta_author, 'get'):
            metadata['author'] = meta_author.get('content', '')
        
        return metadata


def scrape_wikisource_chapter(url: str) -> Dict[str, Any]:
    """Specialized scraper for Wikisource chapters."""
    scraper = SimpleWebScraper()
    result = scraper.scrape_content(url)
    
    if result['status'] == 'success':
        # Extract chapter-specific content
        if BeautifulSoup is not None:
            soup = BeautifulSoup(result['content'], 'html.parser')
        else:
            soup = None
        
        # Find chapter content (Wikisource specific)
        chapter_content = ""
        if soup:
            content_div = soup.find('div', class_='prp-pages-output')
            if content_div:
                chapter_content = content_div.get_text()
        
        result['chapter_content'] = chapter_content
        result['word_count'] = len(chapter_content.split())
        
    return result


def scrape_website(url: str) -> str:
    """Synchronous wrapper to scrape a website and return its text content."""
    try:
        scraper = SimpleWebScraper()
        result = scraper.scrape_content(url)
        if result.get('status') == 'success':
            return result.get('content', '')
        else:
            return f"Error scraping website: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error: {e}"


# For backward compatibility
class WebScraper(SimpleWebScraper):
    """Backward compatibility wrapper."""
    pass


if __name__ == "__main__":
    # Test the scraper
    def test():
        url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
        result = scrape_wikisource_chapter(url)
        print(json.dumps(result, indent=2))
    
    test() 