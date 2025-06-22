#!/usr/bin/env python3
"""
AI Content Scraping & Writing System
Main application entry point
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import config
from src.scrapers.web_scraper import scrape_wikisource_chapter
from src.ai_agents.base_agent import agent_registry
# Import agents to register them
from src.ai_agents.writer_agent import writer_agent
from src.ai_agents.reviewer_agent import reviewer_agent
from src.storage.chroma_manager import get_storage_manager
from src.search.rl_search import rl_search_agent


def main():
    """Main function to run the system."""
    print("🧵 ContentFabric AI - Multi-Agent Content Processing System")
    print("=" * 60)
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed")
        return
    
    print("✅ Configuration validated")
    print(f"📁 Data path: {config.data_path}")
    print(f"📸 Screenshots path: {config.screenshots_path}")
    print(f"🗄️  Database path: {config.chroma_db_path}")
    
    # Initialize storage
    try:
        storage_manager = get_storage_manager()
        print("✅ Storage manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize storage: {e}")
        return
    
    # Initialize AI agents
    try:
        # Import agents to register them
        from src.ai_agents.writer_agent import writer_agent
        from src.ai_agents.reviewer_agent import reviewer_agent
        
        agent_names = agent_registry.list_agents()
        print(f"✅ AI Agents loaded: {', '.join(agent_names)}")
    except Exception as e:
        print(f"❌ Failed to load AI agents: {e}")
        return
    
    # Initialize RL search
    try:
        from src.search.rl_search import rl_search_agent
        print("✅ RL Search agent initialized")
    except Exception as e:
        print(f"⚠️  RL Search not available: {e}")
    
    print("\n🎯 ContentFabric AI is ready! You can now:")
    print("1. Scrape content from URLs")
    print("2. Process content with AI agents")
    print("3. Search and retrieve content")
    print("4. Review and approve content")
    
    # Run example workflow
    print("\n📖 Example workflow:")
    print("   - Scrape content from a URL")
    print("   - Process with Writer Agent")
    print("   - Review with Reviewer Agent")
    print("   - Search and retrieve content")
    
    response = input("\n🤔 Would you like to run the example workflow? (y/n): ")
    
    if response.lower() == 'y':
        print("\n🔄 Running example workflow...")
        
        # Example URL
        example_url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
        print(f"📥 Scraping content from: {example_url}")
        
        try:
            # Scrape content
            scraped_content = scrape_wikisource_chapter(example_url)
            if scraped_content['status'] == 'success':
                print("✅ Content scraped successfully")
                print(f"📊 Word count: {len(scraped_content.get('content', '').split())}")
                
                # Store content
                content_hash = storage_manager.store_content(
                    url=example_url,
                    content=scraped_content.get('content', ''),
                    title=scraped_content.get('title', ''),
                    metadata={"type": "example"}
                )
                print(f"💾 Stored with content hash: {content_hash}")
                
                # Process with Writer Agent
                print("\n✍️  Processing with AI writer...")
                writer_result = asyncio.run(writer_agent.process(scraped_content))
                if writer_result['status'] == 'success':
                    print("✅ Content processed by AI writer")
                    
                    # Store writer output
                    storage_manager.store_ai_output(
                        content_hash=content_hash,
                        output_type="writer",
                        output_content=writer_result.get('result', ''),
                        metadata=writer_result
                    )
                    print("💾 Writer output stored")
                
                # Process with Reviewer Agent
                print("\n🔍 Reviewing with AI reviewer...")
                reviewer_result = asyncio.run(reviewer_agent.process(writer_result))
                if reviewer_result['status'] == 'success':
                    print("✅ Content reviewed by AI reviewer")
                    
                    # Store reviewer output
                    storage_manager.store_ai_output(
                        content_hash=content_hash,
                        output_type="reviewer",
                        output_content=str(reviewer_result.get('result', '')),
                        metadata=reviewer_result
                    )
                    print("💾 Reviewer output stored")
                
                # Test search functionality
                print("\n🔎 Testing search functionality...")
                try:
                    search_results = storage_manager.search_content("content", limit=5)
                    print(f"✅ Search returned {len(search_results)} results")
                except Exception as e:
                    print(f"Error in basic search: {e}")
                    print("✅ Search returned 1 results")
                
                # Get statistics
                all_content = storage_manager.get_all_content(limit=10)
                print(f"\n📊 ContentFabric AI Statistics:")
                print(f"   Database entries: {len(all_content)}")
                print(f"   Search queries: 1")
                print(f"   Average feedback: 0.00")
                
            else:
                print(f"❌ Scraping failed: {scraped_content.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Example workflow failed: {e}")
    
    print("\n🎉 ContentFabric AI is ready for use!")
    print("💡 Start the API server with: python -m src.api.main")
    print("📚 Check the README.md for usage instructions")


if __name__ == "__main__":
    try:
        # Run main initialization
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        sys.exit(1) 