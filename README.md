# Bixi MCP Server

A Model Context Protocol (MCP) server that provides direct access to Montreal's Bixi bike-sharing system data through GBFS (General Bikeshare Feed Specification).

## Overview

This MCP server connects directly to the Bixi GBFS API, providing 13 comprehensive tools for accessing real-time and static bike-sharing data. It includes intelligent caching, bilingual support (English/French), and all the analytical capabilities from the bixi-api project.

## Features

- **Direct GBFS Access**: No dependency on external API servers
- **Bilingual Support**: All tools support English (`en`) and French (`fr`)
- **Intelligent Caching**: 60-second caching to minimize API calls
- **Complete Coverage**: All station data, system info, and analytics
- **Real-time Data**: Live bike and dock availability
- **Advanced Analytics**: System summaries, issue detection, and proximity search

## Available Tools

### Station Information

#### `get_stations(language="en")`
Get all bike stations with their static information (location, capacity, etc.)
```python
# Get all stations in English
stations = await get_stations()

# Get all stations in French  
stations = await get_stations("fr")
```

#### `get_station(station_id, language="en")`
Get information about a specific station by ID
```python
station = await get_station("1001")
```

#### `search_stations(query, limit=20, language="en")`
Search stations by name with intelligent ranking
```python
# Search for stations containing "McGill"
results = await search_stations("McGill", limit=10)
```

### Real-time Status

#### `get_stations_status(station_ids=None, language="en")`
Get real-time status of all stations or specific stations
```python
# Get all station statuses
all_status = await get_stations_status()

# Get status for specific stations
some_status = await get_stations_status("1001,1002,1003")
```

#### `get_station_status(station_id, language="en")`
Get real-time status of a specific station
```python
status = await get_station_status("1001")
```

#### `get_available_stations(min_bikes=1, language="en")`
Find stations with available bikes for rental
```python
# Find stations with at least 1 bike
available = await get_available_stations()

# Find stations with at least 5 bikes
available = await get_available_stations(5)
```

### Location-based Search

#### `find_nearby_stations(lat, lon, radius=1000, language="en")`
Find stations within a specified radius of coordinates
```python
# Find stations within 500m of downtown Montreal
nearby = await find_nearby_stations(45.5017, -73.5673, 500)
```

### System Information

#### `get_system_info(language="en")`
Get general information about the Bixi system
```python
system_info = await get_system_info()
```

#### `get_system_alerts(language="en")`
Get active system-wide alerts and notifications
```python
alerts = await get_system_alerts()
```

#### `get_vehicle_types(language="en")`
Get information about different bike types (regular, electric, etc.)
```python
bikes = await get_vehicle_types()
```

### Analytics & Monitoring

#### `get_system_summary(language="en")`
Get comprehensive system statistics
```python
summary = await get_system_summary()
# Returns: total stations, capacity, utilization rates, etc.
```

#### `get_stations_with_issues(language="en")`
Find stations with operational problems
```python
issues = await get_stations_with_issues()
# Detects: offline stations, no bikes/docks, equipment failures
```

### Raw Data Access

#### `get_raw_gbfs_feed(feed_name, language="en")`
Get raw GBFS feed data directly
```python
# Get raw station information feed
raw_data = await get_raw_gbfs_feed("station_information")

# Available feeds: station_information, station_status, 
# system_information, system_alerts, vehicle_types
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install mcp fastmcp httpx
   ```

## Usage

### As MCP Server
Run the server to provide tools to MCP-compatible applications:
```bash
python mcp_server/server.py
```

### Configuration
The server automatically manages HTTP connections and caching. No additional configuration is required.

## Docker Usage

### Prerequisites
- Docker installed on your system
- This project uses `uv` for dependency management

### Building the Docker Image
```bash
docker build -t bixi-mcp .
```

### Running the Container
```bash
docker run -i bixi-mcp
```

### Claude Desktop Configuration
To use the Dockerized MCP server with Claude Desktop, update your configuration file:

```json
{
  "mcpServers": {
    "bixi": {
      "command": "docker",
      "args": ["run", "-i", "bixi-mcp"]
    }
  }
}
```

### Troubleshooting
- Ensure Docker is running before building or running the container
- The container runs in interactive mode (`-i`) to handle MCP's stdio communication
- If you encounter permission issues, make sure your user is in the docker group

## Data Structure Examples

### Station Information
```json
{
  "station_id": "1001",
  "name": "Métro Champ-de-Mars (Viger / Saint-Antoine)",
  "short_name": "1001",
  "lat": 45.508183,
  "lon": -73.554094,
  "capacity": 35,
  "rental_methods": ["KEY", "CREDITCARD"]
}
```

### Station Status
```json
{
  "station_id": "1001", 
  "num_bikes_available": 12,
  "num_ebikes_available": 3,
  "num_docks_available": 20,
  "is_installed": true,
  "is_renting": true,
  "is_returning": true,
  "last_reported": 1703123456
}
```

### System Summary
```json
{
  "total_stations": 794,
  "online_stations": 791,
  "total_capacity": 19237,
  "total_bikes_available": 8934,
  "total_ebikes_available": 1247,
  "system_utilization_rate": 53.5
}
```

## Language Support

All tools support both English and French:
- `language="en"` (default) - English station names and data
- `language="fr"` - French station names and data

## Error Handling

All tools provide detailed error messages for:
- Network connectivity issues
- Invalid station IDs
- API rate limits
- Missing data

## Caching

The client implements intelligent 60-second caching to:
- Minimize API requests to Bixi GBFS
- Improve response times
- Reduce bandwidth usage
- Respect API rate limits

## Contributing

This MCP server provides comprehensive access to Montreal's Bixi bike-sharing data. For issues or enhancements, please submit via the project repository.

## License

Licensed under the MIT License.