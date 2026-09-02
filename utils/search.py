import re
from typing import List, Dict, Any, Tuple
from utils.vector_store import vector_store

def _keyword_search_scored(query: str, province: str = None, top_k: int = 10) -> List[Tuple[Dict[str, Any], int]]:
    if not vector_store.is_loaded:
        vector_store.load_index()
        
    if not vector_store.is_loaded:
        return []

    # Clean query into words
    query_words = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 2]
    
    # Extract potential section/article numbers from query.
    # Handles: "article 5", "section 25A", "art. 10", "sec.19", "article 25a" etc.
    target_sections = re.findall(
        r'(?:section|article|sec|art)\.?\s*([0-9]+[a-zA-Z]*)',
        query.lower()
    )
    target_sections = [s.upper().rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + 
                       s.upper()[len(s.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')):]  
                       if s != s.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ') 
                       else s for s in target_sections]
    # Also accept bare number at end: "article 5" -> "5"
    target_sections_lower = [s.lower() for s in target_sections]
    
    results = []
    for sec in vector_store.metadata:
        # Province filtering
        if province and province != "Federal":
            if sec.get('province') not in [province, "Federal"]:
                continue
        elif province == "Federal":
            if sec.get('province') != "Federal":
                continue

        score = 0
        text_lower = sec.get('section_text', '').lower()
        title_lower = str(sec.get('section_title', '')).lower()
        law_name_lower = str(sec.get('law_name', '')).lower()
        sec_num = str(sec.get('section_number', '')).lower()
        
        # Massive boost for exact section/article number match
        if sec_num and sec_num in target_sections_lower:
            score += 100
            
        for word in query_words:
            # Law name matches
            if word in law_name_lower:
                score += 3
            # Section title matches – these are very targeted
            if word in title_lower:
                score += 5
            # Text matches
            if word in text_lower:
                score += 1
                
        if score > 0:
            results.append((sec, score))
            
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

def keyword_search(query: str, province: str = None, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Performs a simple keyword search across the metadata and section text.
    Returns results scored by basic keyword match frequency.
    """
    scored = _keyword_search_scored(query, province, top_k)
    return [r[0] for r in scored]

def hybrid_search(query: str, province: str = None, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Combines semantic search and keyword search, deduplicates, filters by province,
    and returns the top_k relevant sections. Prioritizes exact section matches.
    """
    # 1. Ensure index is loaded
    if not vector_store.is_loaded:
        success = vector_store.load_index()
        if not success:
            return [] # No data available
            
    # 2. Get Semantic Results
    semantic_results = []
    try:
        # Fetch a bit more to allow for filtering
        raw_semantic = vector_store.semantic_search(query, top_k=top_k * 2)
        
        # Filter by province
        for sec, score in raw_semantic:
            sec_prov = sec.get('province')
            if province == "Federal" and sec_prov != "Federal":
                continue
            if province and province != "Federal" and sec_prov not in [province, "Federal"]:
                continue
                
            semantic_results.append(sec)
    except Exception as e:
        print(f"Semantic search failed: {e}")

    # 3. Get Keyword Results
    keyword_scored = _keyword_search_scored(query, province=province, top_k=top_k * 2)
    
    # 4. Merge and Deduplicate
    final_results = []
    seen_signatures = set()
    
    def get_signature(sec: Dict[str, Any]) -> str:
        return f"{sec.get('law_name', '')}_{sec.get('section_number', '')}"
        
    # Phase A: Inject exact section matches first (Score >= 100)
    exact_match_laws = set()
    exact_match_numbers = set()
    for sec, score in keyword_scored:
        if score >= 100:
            sig = get_signature(sec)
            if sig not in seen_signatures:
                final_results.append(sec)
                seen_signatures.add(sig)
                exact_match_laws.add(sec.get('law_name'))
                exact_match_numbers.add(str(sec.get('section_number', '')).lower())
                
    # Phase B: Inject semantic results
    for sec in semantic_results:
        # Law-aware filtering: If we found exact matches in a specific law,
        # do not mix in unrelated laws.
        if exact_match_laws and sec.get('law_name') not in exact_match_laws:
            continue
            
        # Strict relevance threshold if exact article was requested
        if exact_match_numbers:
            text_lower = sec.get('section_text', '').lower()
            title_lower = str(sec.get('section_title', '')).lower()
            
            # To be a highly relevant supporting section, it must explicitly mention
            # the requested article number in its text or title.
            is_supporting = False
            for num in exact_match_numbers:
                # Look for "article 8", "section 8", etc.
                pattern = r'\b(?:article|section|art|sec)\.?\s*' + re.escape(num) + r'\b'
                if re.search(pattern, text_lower) or re.search(pattern, title_lower):
                    is_supporting = True
                    break
            
            if not is_supporting:
                continue # Skip unrelated sections! Do not blindly pad Top-5.
                
        sig = get_signature(sec)
        if sig not in seen_signatures:
            final_results.append(sec)
            seen_signatures.add(sig)
            if len(final_results) >= top_k:
                break
                
    # Phase C: Fill remaining with normal keyword results ONLY IF no exact match was requested
    if len(final_results) < top_k and not exact_match_numbers:
        for sec, score in keyword_scored:
            sig = get_signature(sec)
            if sig not in seen_signatures:
                final_results.append(sec)
                seen_signatures.add(sig)
                if len(final_results) >= top_k:
                    break

    print("\n--- DEBUG LOG ---")
    print(f"Query: {query}")
    print(f"Province: {province}")
    print(f"Candidates before filtering (Semantic): {len(raw_semantic)}")
    print(f"Candidates after filtering (Semantic): {len(semantic_results)}")
    print(f"Keyword scored candidates: {len(keyword_scored)}")
    print(f"Final selected context count: {len(final_results)}")
    print(f"Top {top_k} section numbers: {[r.get('section_number') for r in final_results]}")
    print("-----------------\n")

    return final_results
