import httpx

from app.core.config import settings


async def search_torah_source(query: str, max_results: int = 5):
    """Search Sefaria API for Torah sources."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.SEFARIA_API_URL}/texts/{query}")
        if response.status_code == 200:
            return response.json()
        return None


async def get_citation_link(ref: str):
    """Generate Sefaria permalink for citation."""
    return f"https://www.sefaria.org/{ref.replace(' ', '_')}"
