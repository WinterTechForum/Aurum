from typing import Any

import httpx
from mcp.server import FastMCP

mcp = FastMCP("mining_districts")

API_BASE = "https://localhost:8000"

async def make_api_request(url:str, params: dict[str, Any]) -> dict[str, Any] | None:
    headers = {}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0, params=params)
            await response.raise_for_status()
            return await response.json()
        except Exception:
            return None

def format_district(district: dict) -> str:
    return f"""
    Name: {district.get('name', 'Unknown')}
    Info: {district.get('info', 'Unknown')}
    """

@mcp.tool()
async def get_historical_districts(lat: float, lon:float) -> str:
    """Get a historical mining district for a given latitude and longitude.

       Args:
           lat: the latitude
           lon: the longitude
    """
    url = f"{API_BASE}/lookup/"
    params = {
        "lat": lat,
        "lon": lon
    }
    data = await make_api_request(url, params=params)

    if not data:
        return "Unable to fetch districts, or no district found."

    districts = [format_district(feature) for feature in data["features"]]
    return "\n---\n".join(districts)


if __name__ == "__main__":
    mcp.run(transport='stdio')
