"""
Simple web interface for human-in-the-loop interactions
"""

import json
from typing import Dict, Any, List
from datetime import datetime


class WebInterface:
    """Simple web interface for human review."""
    
    def __init__(self):
        self.pending_reviews = []
        self.completed_reviews = []
    
    def generate_review_page(self, content_id: str, content: Dict[str, Any]) -> str:
        """Generate HTML page for content review."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Review - {content_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .content-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .content-text {{
            line-height: 1.6;
            font-size: 16px;
            white-space: pre-wrap;
        }}
        .review-form {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .form-group {{
            margin-bottom: 15px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }}
        textarea {{
            width: 100%;
            min-height: 100px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: inherit;
            resize: vertical;
        }}
        .radio-group {{
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }}
        .radio-group label {{
            display: flex;
            align-items: center;
            font-weight: normal;
            cursor: pointer;
        }}
        .radio-group input {{
            margin-right: 8px;
        }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }}
        .btn:hover {{
            opacity: 0.9;
        }}
        .btn-secondary {{
            background: #6c757d;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Content Review System</h1>
        <p>Review and approve AI-generated content</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{content.get('word_count', 'N/A')}</div>
            <div class="stat-label">Words</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{content.get('confidence', 0):.2f}</div>
            <div class="stat-label">AI Confidence</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{content.get('agent_name', 'Unknown')}</div>
            <div class="stat-label">AI Agent</div>
        </div>
    </div>
    
    <div class="content-section">
        <h2>📄 Content to Review</h2>
        <div class="metadata">
            <strong>Version ID:</strong> {content_id}<br>
            <strong>Agent:</strong> {content.get('agent_name', 'Unknown')}<br>
            <strong>Model:</strong> {content.get('model_name', 'Unknown')}<br>
            <strong>Processed:</strong> {content.get('processed_at', 'Unknown')}<br>
            <strong>Status:</strong> {content.get('status', 'Unknown')}
        </div>
        <div class="content-text">{content.get('result', content.get('content', 'No content available'))}</div>
    </div>
    
    <div class="review-form">
        <h2>✍️ Human Review</h2>
        <form id="reviewForm" onsubmit="submitReview(event)">
            <div class="form-group">
                <label for="feedback">Review Feedback:</label>
                <textarea id="feedback" name="feedback" placeholder="Provide your feedback on the content quality, suggestions for improvement, etc." required></textarea>
            </div>
            
            <div class="form-group">
                <label>Approval Decision:</label>
                <div class="radio-group">
                    <label>
                        <input type="radio" name="approved" value="true" required>
                        ✅ Approve
                    </label>
                    <label>
                        <input type="radio" name="approved" value="false" required>
                        ❌ Reject
                    </label>
                </div>
            </div>
            
            <button type="submit" class="btn">Submit Review</button>
            <button type="button" class="btn btn-secondary" onclick="window.history.back()">Back</button>
        </form>
    </div>
    
    <script>
        function submitReview(event) {{
            event.preventDefault();
            
            const formData = new FormData(event.target);
            const reviewData = {{
                content_id: '{content_id}',
                human_feedback: formData.get('feedback'),
                approved: formData.get('approved') === 'true'
            }};
            
            // Submit to API
            fetch('/review', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(reviewData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'success') {{
                    alert('Review submitted successfully!');
                    window.location.href = '/versions';
                }} else {{
                    alert('Error submitting review: ' + data.detail);
                }}
            }})
            .catch(error => {{
                alert('Error submitting review: ' + error);
            }});
        }}
    </script>
</body>
</html>
"""
        return html
    
    def generate_versions_page(self, versions: List[Dict[str, Any]]) -> str:
        """Generate HTML page for viewing all versions."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Versions</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .version-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .version-card:hover {
            transform: translateY(-2px);
        }
        .version-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .version-id {
            font-family: monospace;
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
        }
        .version-type {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }
        .type-scraped { background: #e3f2fd; color: #1976d2; }
        .type-processed { background: #f3e5f5; color: #7b1fa2; }
        .type-reviewed { background: #e8f5e8; color: #388e3c; }
        .version-content {
            max-height: 200px;
            overflow: hidden;
            position: relative;
        }
        .version-content::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 40px;
            background: linear-gradient(transparent, white);
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-right: 10px;
            font-size: 14px;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .metadata {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Content Versions</h1>
        <p>All versions of scraped and processed content</p>
    </div>
"""
        
        for version in versions:
            version_type = version.get('metadata', {}).get('type', 'unknown')
            version_id = version.get('version_id', 'unknown')
            content = version.get('content', '')[:300] + '...' if len(version.get('content', '')) > 300 else version.get('content', '')
            
            html += f"""
    <div class="version-card">
        <div class="version-header">
            <span class="version-id">{version_id}</span>
            <span class="version-type type-{version_type}">{version_type.upper()}</span>
        </div>
        <div class="version-content">{content}</div>
        <div class="metadata">
            <strong>Agent:</strong> {version.get('metadata', {}).get('agent_name', 'N/A')} | 
            <strong>Timestamp:</strong> {version.get('metadata', {}).get('timestamp', 'N/A')} | 
            <strong>Words:</strong> {len(version.get('content', '').split())}
        </div>
        <div style="margin-top: 15px;">
            <a href="/review/{version_id}" class="btn">Review</a>
            <a href="/versions/{version_id}" class="btn btn-secondary">View Full</a>
        </div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html


# Global web interface instance
web_interface = WebInterface() 