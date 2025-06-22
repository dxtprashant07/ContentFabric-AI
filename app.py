import streamlit as st
from src.scrapers.web_scraper import scrape_website
from src.ai_agents.writer_agent import WriterAgent
from src.ai_agents.reviewer_agent import ReviewerAgent
from src.storage.chroma_manager import get_chroma_manager
from src.search.rl_search import rl_search_agent
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
page = st.sidebar.radio("Go to", ["Scrape & Write", "Review Content", "Version History", "Search", "Human Review", "About"])

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

            # --- Reviewer Agent Section ---
            st.header("3. Review with Reviewer Agent")
            if 'reviewer_output' not in st.session_state:
                st.session_state.reviewer_output = None
            review_button = st.button("Run Reviewer Agent")
            if st.button("Clear Reviewer Output"):
                st.session_state.reviewer_output = None
                st.rerun()
            if review_button:
                with st.spinner("Reviewing with Reviewer Agent..."):
                    try:
                        reviewer = ReviewerAgent()
                        # Use the AI output as input for the reviewer
                        review_result = asyncio.get_event_loop().run_until_complete(
                            reviewer.process(st.session_state.ai_output)
                        )
                        st.session_state.reviewer_output = review_result
                        st.success("Reviewer Agent completed!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error running Reviewer Agent: {e}")
            if st.session_state.reviewer_output:
                st.subheader("Reviewer Agent Feedback")
                review = st.session_state.reviewer_output
                if isinstance(review, dict):
                    result = review.get('result', {})
                    st.write(f"**Status:** {review.get('status', 'N/A')}")
                    st.write(f"**Feedback:** {review.get('feedback', '')}")
                    st.write(f"**Confidence:** :green[{review.get('confidence', 0.0):.2f}]")
                    if isinstance(result, dict):
                        st.write(f"**Overall Score:** :green[{result.get('overall_score', 'N/A')}]" if result.get('overall_score', 0) > 0.8 else f"**Overall Score:** :orange[{result.get('overall_score', 'N/A')}]" )
                        criteria_scores = result.get('criteria_scores', {})
                        if criteria_scores:
                            with st.expander("Criteria Scores", expanded=False):
                                for k, v in criteria_scores.items():
                                    color = 'green' if v > 0.8 else 'orange' if v > 0.6 else 'red'
                                    st.markdown(f"- **{k.capitalize()}:** <span style='color:{color}'>{v:.2f}</span>", unsafe_allow_html=True)
                        strengths = result.get('strengths', [])
                        if strengths:
                            with st.expander("Strengths", expanded=False):
                                st.markdown("\n".join([f"- {s}" for s in strengths]))
                        weaknesses = result.get('weaknesses', [])
                        if weaknesses:
                            with st.expander("Weaknesses", expanded=False):
                                st.markdown("\n".join([f"- {w}" for w in weaknesses]))
                        suggestions = result.get('suggestions', [])
                        if suggestions:
                            with st.expander("Suggestions", expanded=True):
                                st.markdown("\n".join([f"- {s}" for s in suggestions]))
                        # Export and copy options
                        import json
                        review_text = f"Feedback: {review.get('feedback', '')}\n\n" \
                            f"Confidence: {review.get('confidence', 0.0):.2f}\n" \
                            f"Overall Score: {result.get('overall_score', 'N/A')}\n" \
                            f"Criteria Scores: {json.dumps(criteria_scores, indent=2)}\n" \
                            f"Strengths: {json.dumps(strengths, indent=2)}\n" \
                            f"Weaknesses: {json.dumps(weaknesses, indent=2)}\n" \
                            f"Suggestions: {json.dumps(suggestions, indent=2)}\n"
                        st.download_button("Export Review as Text", review_text, file_name="reviewer_feedback.txt")
                        st.code(review_text, language="text")
                        st.caption("You can copy the above feedback or download it as a file.")
                    else:
                        st.write(result)
                else:
                    st.write(review)



if page == "Version History":
    st.header("Content Version History")
    chroma_manager = get_chroma_manager()
    versions = chroma_manager.get_all_versions(limit=50)
    if not versions:
        st.info("No content versions found.")
    else:
        version_options = [f"{v['content_hash']} | {v.get('title','No Title')} | {v.get('timestamp','')}" for v in versions]
        selected = st.selectbox("Select a version to view details", version_options)
        selected_hash = selected.split(" | ")[0]
        version_data = chroma_manager.get_content_version(selected_hash)
        if version_data:
            st.write(f"**Content Hash:** {version_data['content_hash']}")
            st.write(f"**Title:** {version_data.get('title','')}")
            st.write(f"**URL:** {version_data.get('url','')}")
            st.write(f"**Timestamp:** {version_data.get('timestamp','')}")
            st.write(f"**Version:** {version_data.get('version','')}")
            st.write("**Content Preview:**")
            st.text_area("Content", version_data.get('content',''), height=200)
            if st.button("Restore this version"):
                st.session_state.scraped_content = version_data.get('content','')
                st.session_state.url = version_data.get('url','')
                st.success("Version restored to Scrape & Write page!")

if page == "Search":
    st.header("Search Content (RL Search)")
    chroma_manager = get_chroma_manager()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    query = st.text_input("Enter your search query")
    n_results = st.number_input("Number of results", min_value=1, max_value=20, value=5)
    if st.button("Run RL Search"):
        with st.spinner("Searching content..."):
            all_content = chroma_manager.get_all_versions(limit=1000)
            results = rl_search_agent.search(query=query, content_database=all_content, n_results=n_results)
            st.session_state.search_results = results
    if st.button("Clear Search Results"):
        st.session_state.search_results = None
        st.rerun()
    if st.session_state.search_results:
        st.subheader("Search Results")
        for idx, result in enumerate(st.session_state.search_results):
            st.write(f"**Result {idx+1}:**")
            st.write(f"**Title:** {result.get('title','')}")
            st.write(f"**Content Hash:** {result.get('content_hash','')}")
            st.write(f"**Similarity Score:** {result.get('similarity_score', 0.0):.2f}")
            st.write(f"**Content Preview:**")
            st.text_area(f"Content Preview {idx+1}", result.get('content',''), height=100, key=f"search_content_{idx}")
            # Feedback for RL
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button(f"👍 Relevant {idx+1}"):
                    rl_search_agent.provide_feedback(search_id=f"search_{idx}", result_id=result.get('content_hash',''), feedback_score=1.0)
                    st.success("Feedback recorded: Relevant")
            with feedback_col2:
                if st.button(f"👎 Not Relevant {idx+1}"):
                    rl_search_agent.provide_feedback(search_id=f"search_{idx}", result_id=result.get('content_hash',''), feedback_score=0.0)
                    st.success("Feedback recorded: Not Relevant")

if page == "Human Review":
    st.header("Human-in-the-Loop Review")
    chroma_manager = get_chroma_manager()
    versions = chroma_manager.get_all_versions(limit=50)
    if not versions:
        st.info("No content versions found.")
    else:
        version_options = [f"{v['content_hash']} | {v.get('title','No Title')} | {v.get('timestamp','')}" for v in versions]
        selected = st.selectbox("Select a version to review", version_options, key="human_review_select")
        selected_hash = selected.split(" | ")[0]
        version_data = chroma_manager.get_content_version(selected_hash)
        if version_data:
            
            st.write(f"**Title:** {version_data.get('title','')}")
            st.write(f"**URL:** {version_data.get('url','')}")
            st.write(f"**Timestamp:** {version_data.get('timestamp','')}")
            st.write(f"**Version:** {version_data.get('version','')}")
            
            st.write("**Content Preview:**")
            st.text_area("Content", version_data.get('content',''), height=200, key="human_review_content")
            st.subheader("Human Review Feedback")
            feedback = st.text_area("Enter your feedback", key="human_feedback")
            approved = st.radio("Approve this content?", ("Yes", "No"), key="human_approve")
            if st.button("Submit Human Review"):
                # Update metadata and store as new version
                metadata = version_data.get('metadata', {}) or {}
                metadata['human_reviewed'] = True
                metadata['human_feedback'] = feedback
                metadata['approved'] = (approved == "Yes")
                from datetime import datetime
                metadata['reviewed_at'] = datetime.now().isoformat()
                new_version_id = chroma_manager.store_content_version(content=version_data, version_info=metadata)
                st.success(f"Human review recorded! New version ID: {new_version_id}")

st.sidebar.markdown("---")
st.sidebar.info("Developed with ❤️ using Streamlit and Python.") 