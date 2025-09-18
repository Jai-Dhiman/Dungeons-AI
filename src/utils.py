import os
import json
import urllib.request
from langchain_community.document_loaders import WebBaseLoader
from state import Section

def load_and_format_urls(url_list):
    """Load web pages from URLs and format them into a readable string.
    
    Args:
        url_list (str or list): Single URL or list of URLs to load and format
        
    Returns:
        str: Formatted string containing metadata and content from all loaded documents,
             separated by '---' delimiters. Each document includes:
             - Title
             - Source URL
             - Description
             - Page content
    """

    if not isinstance(url_list, list):
        raise ValueError("url_list must be a list of strings")
    
    urls = [url.strip() for url in url_list if url.strip()]

    loader = WebBaseLoader(urls)
    docs = loader.load()

    formatted_docs = []
    
    for doc in docs:
        metadata_str = (
            f"Title: {doc.metadata.get('title', 'N/A')}\n"
            f"Source: {doc.metadata.get('source', 'N/A')}\n"
            f"Description: {doc.metadata.get('description', 'N/A')}\n"
        )
        
        content = doc.page_content.strip()
        
        formatted_doc = f"---\n{metadata_str}\nContent:\n{content}\n---"
        formatted_docs.append(formatted_doc)
    
    return "\n\n".join(formatted_docs)

def read_dictation_file(file_path: str) -> str:
    """Read content from a text file audio-to-text dictation."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        current_dir = os.getcwd()
    notes_dir = os.path.join(current_dir, "notes")
    absolute_path = os.path.join(notes_dir, file_path)
    print(f"Reading file from {absolute_path}")
    try:
        with open(absolute_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: File not found at {absolute_path}")
        return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

def format_sections(sections: list[Section]) -> str:
    """Format a list of sections into a string"""
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
            {'='*60}
            Section {idx}: {section.name}
            {'='*60}
            Description:
            {section.description}
            Main body: 
            {section.main_body}
            Content:
            {section.content if section.content else '[Not yet written]'}
            """
    return formatted_str

def fetch_rag_context(query: str, top_k: int = 5) -> str:
    """Call the local TS RAG service to retrieve context snippets for a query.
    Returns a formatted string suitable for prompt injection.
    """
    base_url = os.environ.get("RAG_BASE_URL", "http://localhost:3001")
    url = f"{base_url}/retrieve"
    payload = {"query": query, "topK": top_k}
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            contexts = data.get("contexts", [])
            if not contexts:
                return ""
            parts = []
            for i, c in enumerate(contexts, 1):
                title = c.get("title") or "Untitled"
                content = c.get("content") or ""
                source = c.get("source") or ""
                parts.append(f"Snippet {i} ({title})\nSource: {source}\n{content}")
            return "RAG Context:\n---\n" + "\n\n---\n".join(parts) + "\n---"
    except Exception as e:
        print(f"Warning: RAG retrieval failed: {e}")
        return ""
