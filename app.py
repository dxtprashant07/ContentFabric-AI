import streamlit as st
from src.scrapers.web_scraper import scrape_website
from src.ai_agents.writer_agent import WriterAgent
import asyncio
import nest_asyncio
import sys
nest_asyncio.apply()

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.set_page_config(page_title="ContentFabric AI", layout="wide")
st.title("🧵 ContentFabric AI - Multi-Agent Content System")

# Initialize session state
if 'scraped_content' not in st.session_state:
    st.session_state.scraped_content = None
if 'url' not in st.session_state:
    st.session_state.url = ""
if 'ai_output' not in st.session_state:
    st.session_state.ai_output = None

# Sidebar for navigation
st.sidebar.title("ContentFabric AI")
page = st.sidebar.radio("Go to", ["Scrape & Write", "About"])

if page == "About":
    st.markdown("""
    ## About ContentFabric AI
    ContentFabric AI is a comprehensive multi-agent content processing system:
    - **Web Scraper**: Extracts content from any URL with intelligent parsing
    - **Writer Agent**: Uses advanced AI to process, summarize, and rewrite content
    - **Reviewer Agent**: Provides quality assessment and feedback
    - **Version Control**: Tracks all content versions and changes
    - **Intelligent Search**: RL-powered content discovery and retrieval
    
    Built with cutting-edge AI models, ChromaDB vector storage, and modern web technologies.
    """)

if page == "Scrape & Write":
    st.header("1. Enter a URL to Scrape")
    
    # URL input with session state
    url = st.text_input("Website URL", value=st.session_state.url, placeholder="https://example.com")
    if url != st.session_state.url:
        st.session_state.url = url
        st.session_state.scraped_content = None  # Clear content if URL changes
        st.session_state.ai_output = None  # Clear AI output if URL changes
    
    col1, col2 = st.columns([1, 4])
    with col1:
        scrape_button = st.button("Scrape Website")
    with col2:
        if st.button("Clear All"):
            st.session_state.scraped_content = None
            st.session_state.ai_output = None
            st.session_state.url = ""
            st.rerun()

    # Scraping logic
    if scrape_button and url:
        with st.spinner("Scraping website..."):
            try:
                scraped_content = scrape_website(url)
                if not scraped_content:
                    st.warning("No content was scraped from the URL.")
                else:
                    st.session_state.scraped_content = scraped_content
                    st.success("Website scraped successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error scraping website: {e}")

    # Display scraped content if available
    if st.session_state.scraped_content:
        st.subheader("Scraped Content")
        st.text_area("Content", st.session_state.scraped_content, height=200, key="scraped_content_display")

        st.header("2. Process with Writer Agent")
        prompt = st.text_area("Optional: Add instructions for the AI writer (e.g., summarize, rewrite, etc.)", 
                             value="Summarize the content above.", key="writer_prompt")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            process_button = st.button("Run Writer Agent")
        with col2:
            if st.button("Clear AI Output"):
                st.session_state.ai_output = None
                st.rerun()

        if process_button:
            with st.spinner("Processing with Writer Agent..."):
                try:
                    agent = WriterAgent()
                    ai_output = asyncio.get_event_loop().run_until_complete(
                        agent.process({"content": st.session_state.scraped_content}, instructions=prompt)
                    )
                    st.session_state.ai_output = ai_output
                    st.success("Writer Agent completed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error running Writer Agent: {e}")

        # Display AI output if available
        if st.session_state.ai_output:
            st.subheader("AI Output")
            if isinstance(st.session_state.ai_output, dict):
                # If it's a structured response
                if 'result' in st.session_state.ai_output:
                    ai_text = st.session_state.ai_output['result']
                    feedback = st.session_state.ai_output.get('feedback', '')
                    confidence = st.session_state.ai_output.get('confidence', 0.0)
                    
                    st.text_area("AI Output", ai_text, height=200, key="ai_output_display")
                    st.info(f"Feedback: {feedback}")
                    st.metric("Confidence", f"{confidence:.2f}")
                else:
                    st.text_area("AI Output", str(st.session_state.ai_output), height=200, key="ai_output_display")
            else:
                # If it's a simple string
                st.text_area("AI Output", str(st.session_state.ai_output), height=200, key="ai_output_display")

st.sidebar.markdown("---")
st.sidebar.info("Developed with ❤️ using Streamlit and Python.") 