import httpx
from typing import Dict, List
import asyncio


class BixiGBFSClient:
    """HTTP client for fetching Bixi GBFS bike-sharing data with caching."""
    
    BASE_URL = "https://gbfs.velobixi.com/gbfs/2-2"

    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self._cache: Dict[str, tuple] = {}  # Simple in-memory cache: {key: (data, timestamp)}

    async def _fetch_feed(self, feed_name: str, language: str = "en") -> dict:
        """Fetch GBFS feed with 60-second caching to reduce API calls."""
        cache_key = f"{language}_{feed_name}"

        # Check if cached data is still valid (< 60 seconds old)
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if (asyncio.get_event_loop().time() - timestamp) < 60:
                return data

        # Fetch fresh data from GBFS API
        url = f"{self.BASE_URL}/{language}/{feed_name}.json"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            # Cache the response with current timestamp
            self._cache[cache_key] = (data, asyncio.get_event_loop().time())
            return data
        except httpx.RequestError as e:
            raise Exception(f"Failed to fetch {feed_name}: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"GBFS API error ({e.response.status_code}): {e.response.text}")

    async def get_station_information(self, language: str = "en") -> List[dict]:
        """Get static information about all bike stations (locations, capacity, etc.)."""
        data = await self._fetch_feed("station_information", language)
        return data.get("data", {}).get("stations", [])

    async def get_station_status(self, language: str = "en") -> List[dict]:
        """Get real-time status of all stations (available bikes/docks)."""
        data = await self._fetch_feed("station_status", language)
        return data.get("data", {}).get("stations", [])

    async def get_system_information(self, language: str = "en") -> dict:
        """Get general information about the Bixi bike-sharing system."""
        data = await self._fetch_feed("system_information", language)
        return data.get("data", {})

    async def get_system_alerts(self, language: str = "en") -> List[dict]:
        """Get active system-wide alerts and notifications."""
        data = await self._fetch_feed("system_alerts", language)
        return data.get("data", {}).get("alerts", [])

    async def get_vehicle_types(self, language: str = "en") -> List[dict]:
        """Get information about different types of bikes/vehicles available."""
        data = await self._fetch_feed("vehicle_types", language)
        return data.get("data", {}).get("vehicle_types", [])