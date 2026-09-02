import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# We'll store the index in the data directory
INDEX_PATH = os.path.join("data", "vector_index.pkl")
CLEAN_LAWS_DIR = os.path.join("data", "clean_laws")

class VectorStore:
    def __init__(self):
        self.metadata: List[Dict[str, str]] = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.is_loaded = False

    def load_index(self) -> bool:
        """Loads the vector index from disk if it exists."""
        if os.path.exists(INDEX_PATH):
            try:
                with open(INDEX_PATH, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.vectorizer = data.get('vectorizer', None)
                    self.tfidf_matrix = data.get('tfidf_matrix', None)
                    
                    # Backward compatibility handling just in case old format is loaded
                    if self.vectorizer is None or self.tfidf_matrix is None:
                        print("Old index format detected. Requires rebuild.")
                        return False
                        
                self.is_loaded = True
                print(f"Loaded index with {len(self.metadata)} sections.")
                return True
            except Exception as e:
                print(f"Error loading index: {e}")
        return False

    def save_index(self):
        """Saves the current metadata, vectorizer, and tfidf_matrix to disk."""
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        with open(INDEX_PATH, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix
            }, f)
        print(f"Saved index with {len(self.metadata)} sections to {INDEX_PATH}.")

    def build_index(self):
        """
        Reads all JSON files in clean_laws, extracts text, generates TF-IDF vectors,
        and saves the vector index completely locally.
        """
        all_sections = []
        if not os.path.exists(CLEAN_LAWS_DIR):
            print(f"Directory {CLEAN_LAWS_DIR} does not exist.")
            return

        print("Reading cleaned laws from disk...")
        for filename in os.listdir(CLEAN_LAWS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(CLEAN_LAWS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    sections = json.load(f)
                    all_sections.extend(sections)
                    
        # Filter unique signatures (law_name + section_number)
        unique_sections = []
        seen = set()
        for sec in all_sections:
            sig = f"{sec.get('law_name', '')}_{sec.get('section_number', '')}"
            if sig not in seen:
                seen.add(sig)
                unique_sections.append(sec)
                
        if not unique_sections:
            print("No valid sections found to index.")
            return
            
        print(f"Found {len(unique_sections)} unique sections. Building TF-IDF index locally...")
        
        texts_to_embed = []
        for sec in unique_sections:
            # Include section_title so title-based queries match correctly.
            title_part = sec.get('section_title', '')
            text = (
                f"Law: {sec.get('law_name', '')}\n"
                f"Section: {sec.get('section_number', '')}\n"
                f"Title: {title_part}\n"
                f"Province: {sec.get('province', '')}\n"
                f"Text: {sec.get('section_text', '')}"
            )
            texts_to_embed.append(text)
            
        self.metadata = unique_sections
        # min_df=1 so rare but important legal terms are indexed in a small corpus.
        self.vectorizer = TfidfVectorizer(stop_words='english', max_df=0.85, min_df=1)
        self.tfidf_matrix = self.vectorizer.fit_transform(texts_to_embed)
        self.is_loaded = True
        
        self.save_index()
        print(f"Successfully built and saved complete local index of {len(self.metadata)} sections.")

    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Performs a cosine similarity search between the query text and the TF-IDF index.
        """
        if not self.is_loaded or self.tfidf_matrix is None or self.vectorizer is None:
            return []
            
        # Vectorize the query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            # Only include if similarity > 0
            if similarities[idx] > 0:
                results.append((self.metadata[idx], float(similarities[idx])))
            
        return results

# Singleton instance for easy usage
vector_store = VectorStore()
