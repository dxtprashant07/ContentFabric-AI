import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import json
from datetime import datetime
import random

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    print("Scikit-learn not installed. Run: pip install scikit-learn")
    TfidfVectorizer = None
    cosine_similarity = None


class RLSearchAgent:
    """Reinforcement Learning based search agent for content retrieval."""
    
    def __init__(self, learning_rate: float = 0.1, exploration_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.search_history = []
        self.reward_history = []
        self.query_embeddings = {}
        
        # Initialize TF-IDF vectorizer if available
        if TfidfVectorizer:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
        else:
            self.vectorizer = None
    
    def search(self, query: str, content_database: List[Dict[str, Any]], 
               n_results: int = 5, use_rl: bool = True) -> List[Dict[str, Any]]:
        """Search content using RL-enhanced retrieval."""
        try:
            # Record search query
            search_id = self._record_search(query)
            
            if use_rl and self.search_history:
                # Use RL to improve search
                results = self._rl_search(query, content_database, n_results)
            else:
                # Use basic search
                results = self._basic_search(query, content_database, n_results)
            
            # Store search results for learning
            self._store_search_results(search_id, query, results)
            
            return results
            
        except Exception as e:
            print(f"Error in RL search: {str(e)}")
            return self._basic_search(query, content_database, n_results)
    
    def _record_search(self, query: str) -> str:
        """Record a search query for learning."""
        search_id = f"search_{len(self.search_history)}_{datetime.now().timestamp()}"
        
        self.search_history.append({
            "search_id": search_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": []
        })
        
        return search_id
    
    def _basic_search(self, query: str, content_database: List[Dict[str, Any]], 
                     n_results: int) -> List[Dict[str, Any]]:
        """Basic search using TF-IDF similarity."""
        if not self.vectorizer or not content_database:
            return content_database[:n_results]
        
        try:
            # Extract content texts
            content_texts = [item.get('content', '') for item in content_database]
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(content_texts)
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            if cosine_similarity is not None:
                similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
            else:
                # Fallback: return first n_results items
                similarities = np.ones(len(content_database))
            
            # Sort by similarity
            sorted_indices = np.argsort(similarities)[::-1]
            
            # Return top results
            results = []
            for idx in sorted_indices[:n_results]:
                if similarities[idx] > 0:
                    result = content_database[idx].copy()
                    result['similarity_score'] = float(similarities[idx])
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error in basic search: {str(e)}")
            return content_database[:n_results]
    
    def _rl_search(self, query: str, content_database: List[Dict[str, Any]], 
                  n_results: int) -> List[Dict[str, Any]]:
        """RL-enhanced search using learned patterns."""
        try:
            # Get basic search results
            basic_results = self._basic_search(query, content_database, n_results * 2)
            
            # Apply RL-based reordering
            if self.search_history and len(self.search_history) > 1:
                reordered_results = self._apply_rl_reordering(query, basic_results)
                return reordered_results[:n_results]
            
            return basic_results[:n_results]
            
        except Exception as e:
            print(f"Error in RL search: {str(e)}")
            return self._basic_search(query, content_database, n_results)
    
    def _apply_rl_reordering(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply RL-based reordering to search results."""
        try:
            # Calculate RL scores based on historical feedback
            for result in results:
                rl_score = self._calculate_rl_score(query, result)
                result['rl_score'] = rl_score
            
            # Sort by combined score (similarity + RL score)
            results.sort(key=lambda x: x.get('similarity_score', 0) + x.get('rl_score', 0), reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error in RL reordering: {str(e)}")
            return results
    
    def _calculate_rl_score(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate RL score based on historical feedback."""
        try:
            score = 0.0
            
            # Look for similar queries in history
            for search_record in self.search_history[-10:]:  # Last 10 searches
                if self._query_similarity(query, search_record['query']) > 0.5:
                    # Check if this result was in previous results
                    for prev_result in search_record.get('results', []):
                        if self._content_similarity(result, prev_result) > 0.7:
                            # Add reward based on previous feedback
                            score += prev_result.get('feedback_score', 0.5)
            
            return score
            
        except Exception as e:
            print(f"Error calculating RL score: {str(e)}")
            return 0.0
    
    def _query_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries."""
        try:
            if not self.vectorizer:
                return 0.0
            
            # Simple word overlap for now
            words1 = set(query1.lower().split())
            words2 = set(query2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception:
            return 0.0
    
    def _content_similarity(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> float:
        """Calculate similarity between two content items."""
        try:
            text1 = content1.get('content', '')
            text2 = content2.get('content', '')
            
            if not text1 or not text2:
                return 0.0
            
            # Simple text similarity
            words1 = set(text1.lower().split()[:100])  # First 100 words
            words2 = set(text2.lower().split()[:100])
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception:
            return 0.0
    
    def _store_search_results(self, search_id: str, query: str, results: List[Dict[str, Any]]):
        """Store search results for learning."""
        try:
            # Find the search record
            for record in self.search_history:
                if record['search_id'] == search_id:
                    record['results'] = results
                    break
                    
        except Exception as e:
            print(f"Error storing search results: {str(e)}")
    
    def provide_feedback(self, search_id: str, result_id: str, feedback_score: float):
        """Provide feedback for learning."""
        try:
            # Find the search record and update feedback
            for record in self.search_history:
                if record['search_id'] == search_id:
                    for result in record.get('results', []):
                        if result.get('version_id') == result_id:
                            result['feedback_score'] = feedback_score
                            break
                    break
            
            # Store reward for RL learning
            self.reward_history.append({
                'search_id': search_id,
                'result_id': result_id,
                'feedback_score': feedback_score,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error providing feedback: {str(e)}")
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search statistics."""
        try:
            total_searches = len(self.search_history)
            total_feedback = len(self.reward_history)
            
            avg_feedback = 0.0
            if total_feedback > 0:
                avg_feedback = sum(r['feedback_score'] for r in self.reward_history) / total_feedback
            
            return {
                'total_searches': total_searches,
                'total_feedback': total_feedback,
                'average_feedback_score': avg_feedback,
                'learning_rate': self.learning_rate,
                'exploration_rate': self.exploration_rate
            }
            
        except Exception as e:
            print(f"Error getting search statistics: {str(e)}")
            return {}
    
    def save_model(self, filepath: str) -> bool:
        """Save the RL model state."""
        try:
            model_state = {
                'search_history': self.search_history,
                'reward_history': self.reward_history,
                'learning_rate': self.learning_rate,
                'exploration_rate': self.exploration_rate
            }
            
            with open(filepath, 'w') as f:
                json.dump(model_state, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load the RL model state."""
        try:
            with open(filepath, 'r') as f:
                model_state = json.load(f)
            
            self.search_history = model_state.get('search_history', [])
            self.reward_history = model_state.get('reward_history', [])
            self.learning_rate = model_state.get('learning_rate', 0.1)
            self.exploration_rate = model_state.get('exploration_rate', 0.1)
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False


# Global RL search agent instance
rl_search_agent = RLSearchAgent() 