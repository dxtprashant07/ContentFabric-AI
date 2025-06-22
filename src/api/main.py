from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime

# Import our modules
from ..scrapers.web_scraper import scrape_wikisource_chapter
from ..ai_agents.base_agent import agent_registry
from ..storage.chroma_manager import get_chroma_manager
from ..search.rl_search import rl_search_agent


app = FastAPI(
    title="ContentFabric AI",
    description="A comprehensive multi-agent content processing system for intelligent web scraping, AI writing, reviewing, and versioning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class ScrapeRequest(BaseModel):
    url: str
    take_screenshots: bool = True


class ProcessRequest(BaseModel):
    content_id: str
    agent_name: str
    parameters: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    filters: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    search_id: str
    result_id: str
    feedback_score: float


class ReviewRequest(BaseModel):
    content_id: str
    human_feedback: str
    approved: bool


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "ContentFabric AI - Multi-Agent Content Processing System",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/scrape")
async def scrape_content(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Scrape content from a URL."""
    try:
        # Scrape the content
        result = scrape_wikisource_chapter(request.url)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Store in ChromaDB
        chroma_manager = get_chroma_manager()
        version_id = chroma_manager.store_content_version(
            content=result,
            version_info={
                "type": "scraped",
                "url": request.url,
                "screenshots_taken": request.take_screenshots
            }
        )
        
        result['version_id'] = version_id
        
        return {
            "status": "success",
            "data": result,
            "message": "Content scraped and stored successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_content(request: ProcessRequest):
    """Process content with a specific AI agent."""
    try:
        # Get the content from ChromaDB
        chroma_manager = get_chroma_manager()
        content_data = chroma_manager.get_content_version(request.content_id)
        
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Process with the specified agent
        result = await agent_registry.process_with_agent(
            request.agent_name,
            content_data,
            **(request.parameters or {})
        )
        
        # Store the processed result
        new_version_id = chroma_manager.store_content_version(
            content=result,
            version_info={
                "type": "processed",
                "agent": request.agent_name,
                "parent_version": request.content_id,
                "parameters": request.parameters
            }
        )
        
        result['version_id'] = new_version_id
        
        return {
            "status": "success",
            "data": result,
            "message": f"Content processed by {request.agent_name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List all available AI agents."""
    try:
        agents = agent_registry.list_agents()
        return {
            "status": "success",
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/versions")
async def get_versions(url: Optional[str] = None, limit: int = 50):
    """Get all versions of content."""
    try:
        chroma_manager = get_chroma_manager()
        versions = chroma_manager.get_all_versions(url=url, limit=limit)
        
        return {
            "status": "success",
            "versions": versions,
            "count": len(versions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/versions/{version_id}")
async def get_version(version_id: str):
    """Get a specific version of content."""
    try:
        chroma_manager = get_chroma_manager()
        version = chroma_manager.get_content_version(version_id)
        
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        return {
            "status": "success",
            "data": version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_content(request: SearchRequest):
    """Search content using RL algorithm."""
    try:
        # Get all content from ChromaDB
        chroma_manager = get_chroma_manager()
        all_content = chroma_manager.get_all_versions(limit=1000)
        
        # Search using RL agent
        results = rl_search_agent.search(
            query=request.query,
            content_database=all_content,
            n_results=request.n_results
        )
        
        return {
            "status": "success",
            "results": results,
            "count": len(results),
            "search_id": f"search_{datetime.now().timestamp()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback for RL learning."""
    try:
        rl_search_agent.provide_feedback(
            search_id=request.search_id,
            result_id=request.result_id,
            feedback_score=request.feedback_score
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review")
async def human_review(request: ReviewRequest):
    """Handle human review of content."""
    try:
        chroma_manager = get_chroma_manager()
        content_data = chroma_manager.get_content_version(request.content_id)
        
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update metadata with human review
        metadata = content_data['metadata']
        metadata['human_reviewed'] = True
        metadata['human_feedback'] = request.human_feedback
        metadata['approved'] = request.approved
        metadata['reviewed_at'] = datetime.now().isoformat()
        
        # Store updated version
        new_version_id = chroma_manager.store_content_version(
            content=content_data,
            version_info=metadata
        )
        
        return {
            "status": "success",
            "version_id": new_version_id,
            "message": "Human review recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_statistics():
    """Get system statistics."""
    try:
        chroma_manager = get_chroma_manager()
        db_stats = chroma_manager.get_statistics()
        search_stats = rl_search_agent.get_search_statistics()
        
        return {
            "status": "success",
            "database": db_stats,
            "search": search_stats,
            "agents": {
                "count": len(agent_registry.list_agents()),
                "names": agent_registry.list_agents()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/versions/{version_id}")
async def delete_version(version_id: str):
    """Delete a specific version."""
    try:
        chroma_manager = get_chroma_manager()
        success = chroma_manager.delete_version(version_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Version not found or could not be deleted")
        
        return {
            "status": "success",
            "message": "Version deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 