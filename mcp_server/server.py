#!/usr/bin/env python3
"""
MCP Server for Bixi API - Provides tools to access bike sharing data directly from bixi web services.
"""

import httpx
import math
from mcp.server.fastmcp import FastMCP
from client import BixiGBFSClient

# Create MCP instance
mcp = FastMCP("bixi")

# Global client instance
_bixi_client = None

async def get_client() -> BixiGBFSClient:
    """Get or create global GBFS client instance."""
    global _bixi_client
    if not _bixi_client:
        http_client = httpx.AsyncClient(timeout=30.0)
        _bixi_client = BixiGBFSClient(http_client)
    return _bixi_client

@mcp.tool()
async def get_stations(language: str = "en"):
    """Get all bike stations with their information.
    
    Args:
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        return await client.get_station_information(language)
    except Exception as e:
        raise Exception(f"Error fetching stations: {str(e)}")

@mcp.tool()
async def get_stations_status(station_ids: str = None, language: str = "en"):
    """
    Get real-time status of stations.
    
    Args:
        station_ids: Comma-separated list of station IDs (optional)
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        statuses = await client.get_station_status(language)
        
        if station_ids:
            # Filter for specific station IDs
            requested_ids = [sid.strip() for sid in station_ids.split(",")]
            filtered_statuses = [s for s in statuses if s["station_id"] in requested_ids]
            return filtered_statuses
        
        return statuses
    except Exception as e:
        raise Exception(f"Error fetching station status: {str(e)}")

@mcp.tool()
async def find_nearby_stations(lat: float, lon: float, radius: float = 1000, language: str = "en"):
    """
    Find stations near a given position.
    
    Args:
        lat: Latitude
        lon: Longitude 
        radius: Search radius in meters (default: 1000)
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        stations = await client.get_station_information(language)
        
        def distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points using Haversine formula."""
            R = 6371000  # Earth radius in meters
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)

            a = (
                math.sin(delta_phi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        # Filter stations within radius and add distance info
        nearby_stations = []
        for station in stations:
            dist = distance(lat, lon, station["lat"], station["lon"])
            if dist <= radius:
                station_with_distance = station.copy()
                station_with_distance["distance_meters"] = round(dist, 2)
                nearby_stations.append(station_with_distance)

        # Sort by distance (closest first)
        nearby_stations.sort(key=lambda x: x["distance_meters"])
        return nearby_stations
    except Exception as e:
        raise Exception(f"Error finding nearby stations: {str(e)}")

@mcp.tool()
async def search_stations(query: str, limit: int = 20, language: str = "en"):
    """
    Search stations by name.
    
    Args:
        query: Search term
        limit: Maximum number of results (default: 20)
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        stations = await client.get_station_information(language)
        
        # Perform case-insensitive search on station names
        query_lower = query.lower()
        matching_stations = [
            station for station in stations 
            if query_lower in station["name"].lower()
        ]
        
        # Sort by relevance (exact matches first, then alphabetical)
        matching_stations.sort(key=lambda s: (
            not s["name"].lower().startswith(query_lower),  # Starts with query first
            s["name"].lower()  # Then alphabetical
        ))
        
        # Limit results
        return {
            "query": query,
            "total_matches": len(matching_stations),
            "results": matching_stations[:limit]
        }
    except Exception as e:
        raise Exception(f"Error searching stations: {str(e)}")

@mcp.tool()
async def get_available_stations(min_bikes: int = 1, language: str = "en"):
    """
    Find stations that have at least the specified number of available bikes.
    
    Args:
        min_bikes: Minimum number of available bikes (default: 1)
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        statuses = await client.get_station_status(language)
        available_stations = [
            s for s in statuses if s["num_bikes_available"] >= min_bikes and s["is_renting"]
        ]
        return available_stations
    except Exception as e:
        raise Exception(f"Error fetching available stations: {str(e)}")

@mcp.tool()
async def get_system_summary(language: str = "en"):
    """Get system-wide statistics summary.
    
    Args:
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        stations_info = await client.get_station_information(language)
        stations_status = await client.get_station_status(language)
        
        # Calculate statistics
        total_stations = len(stations_info)
        total_capacity = sum(s["capacity"] for s in stations_info)
        
        online_stations = sum(1 for s in stations_status if s["is_installed"])
        total_bikes_available = sum(s["num_bikes_available"] for s in stations_status)
        total_ebikes_available = sum(s["num_ebikes_available"] for s in stations_status)
        total_docks_available = sum(s["num_docks_available"] for s in stations_status)
        
        # Calculate percentages
        utilization_rate = ((total_capacity - total_docks_available) / total_capacity * 100) if total_capacity > 0 else 0
        online_percentage = (online_stations / total_stations * 100) if total_stations > 0 else 0
        
        return {
            "total_stations": total_stations,
            "online_stations": online_stations,
            "offline_stations": total_stations - online_stations,
            "online_percentage": round(online_percentage, 1),
            "total_capacity": total_capacity,
            "total_bikes_available": total_bikes_available,
            "total_ebikes_available": total_ebikes_available,
            "total_docks_available": total_docks_available,
            "system_utilization_rate": round(utilization_rate, 1)
        }
    except Exception as e:
        raise Exception(f"Error fetching system summary: {str(e)}")

@mcp.tool()
async def get_stations_with_issues(language: str = "en"):
    """Find stations with operational issues.
    
    Args:
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        stations_info = await client.get_station_information(language)
        stations_status = await client.get_station_status(language)
        
        # Create lookup for station names
        station_names = {s["station_id"]: s["name"] for s in stations_info}
        
        problem_stations = []
        
        for status in stations_status:
            issues = []
            
            # Check for various types of issues
            if not status["is_installed"]:
                issues.append("Station not installed")
            
            if not status["is_renting"]:
                issues.append("Not renting bikes")
                
            if not status["is_returning"]:
                issues.append("Not accepting bike returns")
                
            # Check if station is completely full or empty
            if status["num_bikes_available"] == 0 and status["num_docks_available"] == 0:
                issues.append("Station appears to be offline (no bikes or docks available)")
            elif status["num_bikes_available"] == 0 and status["is_renting"]:
                issues.append("No bikes available")
            elif status["num_docks_available"] == 0 and status["is_returning"]:
                issues.append("No docks available")
                
            # Check for high number of disabled equipment
            total_capacity = status["num_bikes_available"] + status["num_docks_available"] + status["num_bikes_disabled"] + status["num_docks_disabled"]
            if total_capacity > 0:
                disabled_rate = (status["num_bikes_disabled"] + status["num_docks_disabled"]) / total_capacity
                if disabled_rate > 0.3:  # More than 30% disabled
                    issues.append(f"High equipment failure rate ({round(disabled_rate * 100, 1)}% disabled)")
            
            # If any issues found, add to problem stations
            if issues:
                problem_stations.append({
                    "station_id": status["station_id"],
                    "station_name": station_names.get(status["station_id"], "Unknown"),
                    "issues": issues,
                    "status": {
                        "is_installed": status["is_installed"],
                        "is_renting": status["is_renting"],
                        "is_returning": status["is_returning"],
                        "bikes_available": status["num_bikes_available"],
                        "docks_available": status["num_docks_available"],
                        "bikes_disabled": status["num_bikes_disabled"],
                        "docks_disabled": status["num_docks_disabled"]
                    }
                })
        
        return {
            "total_problem_stations": len(problem_stations),
            "stations": problem_stations
        }
    except Exception as e:
        raise Exception(f"Error fetching stations with issues: {str(e)}")

@mcp.tool()
async def get_system_alerts(language: str = "en"):
    """Get active system alerts.
    
    Args:
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        return await client.get_system_alerts(language)
    except Exception as e:
        raise Exception(f"Error fetching system alerts: {str(e)}")
@mcp.tool()
async def get_station(station_id: str, language: str = "en"):
    """Get information about a specific bike station by its ID.
    
    Args:
        station_id: Station ID to look up
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        stations = await client.get_station_information(language)
        station = next((s for s in stations if s["station_id"] == station_id), None)
        
        if not station:
            raise Exception(f"Station with ID '{station_id}' not found")
        
        return station
    except Exception as e:
        raise Exception(f"Error fetching station: {str(e)}")

@mcp.tool()
async def get_station_status(station_id: str, language: str = "en"):
    """Get real-time status of a specific station (available bikes/docks).
    
    Args:
        station_id: Station ID to look up
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        statuses = await client.get_station_status(language)
        status = next((s for s in statuses if s["station_id"] == station_id), None)
        
        if not status:
            raise Exception(f"Station status for ID '{station_id}' not found")
        
        return status
    except Exception as e:
        raise Exception(f"Error fetching station status: {str(e)}")

@mcp.tool()
async def get_system_info(language: str = "en"):
    """Get general information about the Bixi bike-sharing system.
    
    Args:
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        return await client.get_system_information(language)
    except Exception as e:
        raise Exception(f"Error fetching system info: {str(e)}")

@mcp.tool()
async def get_vehicle_types(language: str = "en"):
    """Get information about different types of bikes/vehicles available.
    
    Args:
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        return await client.get_vehicle_types(language)
    except Exception as e:
        raise Exception(f"Error fetching vehicle types: {str(e)}")

@mcp.tool()
async def get_raw_gbfs_feed(feed_name: str, language: str = "en"):
    """Get raw GBFS feed data directly.
    
    Args:
        feed_name: Name of the GBFS feed (e.g., 'station_information', 'station_status')
        language: Language code (en/fr)
    """
    try:
        client = await get_client()
        return await client._fetch_feed(feed_name, language)
    except Exception as e:
        raise Exception(f"Error fetching raw GBFS feed: {str(e)}")


if __name__ == "__main__":
    print("Starting Bixi MCP server with direct GBFS access...")
    mcp.run(transport='stdio')