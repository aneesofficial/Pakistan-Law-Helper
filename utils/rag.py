import os
import re
from typing import List, Dict, Any, Tuple
from utils.search import hybrid_search
from utils.gemini_service import generate_answer, GeminiServiceError

def load_prompt_template() -> str:
    prompt_path = os.path.join("prompts", "rag_prompt.txt")
    if not os.path.exists(prompt_path):
        return "LEGAL CONTEXT:\n{context}\n\nUSER QUESTION:\n{question}"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def construct_context(sections: List[Dict[str, Any]]) -> str:
    """Formats the retrieved sections into a single string for the prompt."""
    if not sections:
        return "No relevant legal sections found."
        
    context_parts = []
    for i, sec in enumerate(sections):
        part = (
            f"--- Document {i+1} ---\n"
            f"Law Name: {sec.get('law_name', 'Unknown')}\n"
            f"Year: {sec.get('year', 'Unknown')}\n"
            f"Section Number: {sec.get('section_number', 'Unknown')}\n"
            f"Province: {sec.get('province', 'Unknown')}\n"
            f"Text: {sec.get('section_text', '')}\n"
        )
        context_parts.append(part)
        
    return "\n".join(context_parts)

def validate_sources(answer: str, retrieved_sections: List[Dict[str, Any]]) -> Tuple[str, bool]:
    """
    Lightweight verification layer.
    Checks if the generated answer cites any section numbers that were NOT retrieved.
    Returns (validated_answer, is_valid)
    """
    retrieved_section_nums = [str(sec.get('section_number', '')).lower() for sec in retrieved_sections]
    
    # Find all "Section X" or "Rule X" mentions in the text
    # e.g., "Section 45" or "Section 45(1)"
    cited_sections = re.findall(r'(?i)(?:section|rule)\s+([0-9]+[a-z]*(?:\([0-9a-z]+\))?)', answer)
    
    unsupported_citations = []
    for citation in cited_sections:
        # Check if this exact citation or its base (e.g. "45" from "45(1)") is in retrieved
        citation_lower = citation.lower()
        base_citation = re.sub(r'\(.*?\)', '', citation_lower)
        
        is_supported = False
        for ret_sec in retrieved_section_nums:
            if citation_lower == ret_sec or base_citation == ret_sec or ret_sec.startswith(base_citation):
                is_supported = True
                break
                
        if not is_supported:
            unsupported_citations.append(citation)
            
    if unsupported_citations:
        # We found hallucinations
        warning = (
            "\n\n**Warning (System Validation):** The AI cited section(s) " 
            f"{', '.join(unsupported_citations)} which were NOT found in the retrieved source documents. "
            "Please disregard those specific citations as they may be hallucinated."
        )
        return answer + warning, False
        
    return answer, True

def answer_question(question: str, province: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Main RAG pipeline:
    1. Retrieve context
    2. Construct prompt
    3. Call Gemini
    4. Validate response
    """
    try:
        # 1. Search
        top_sections = hybrid_search(question, province=province, top_k=5)
        
        if not top_sections:
            return "I couldn't find sufficient legal information in the available local sources.", []
            
        # 2. Construct Prompt
        context_str = construct_context(top_sections)
        prompt_template = load_prompt_template()
        
        prompt = prompt_template.format(
            context=context_str,
            question=question
        )
        
        # 3. Call Gemini
        raw_answer = generate_answer(prompt)
        
        # 4. Validate sources
        final_answer, _ = validate_sources(raw_answer, top_sections)
        
        return final_answer, top_sections
        
    except GeminiServiceError as e:
        if top_sections:
            fallback_answer = (
                f"**Service Error:** {e}\n\n"
                "---\n\n"
                "### ⚠️ Local Fallback Answer\n"
                "The AI service is temporarily unavailable. However, based on the locally retrieved legal texts, here is the relevant information:\n\n"
            )
            for sec in top_sections:
                fallback_answer += f"**Article/Section {sec.get('section_number', 'N/A')} - {sec.get('law_name', 'Unknown')}**\n"
                fallback_answer += f"{sec.get('section_text', '').strip()}\n\n"
                
            return fallback_answer, top_sections
        return f"**Service Error:** {e}", []
    except Exception as e:
        return f"**An unexpected error occurred:** {e}", []
