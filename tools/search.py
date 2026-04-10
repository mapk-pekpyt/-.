from duckduckgo_search import DDGS

def search_duckduckgo(query, max_results=5):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
        return [r["body"] for r in results]