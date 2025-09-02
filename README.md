# Bixi MCP Server

MCP server providing access to Montreal's Bixi bike-sharing data through GBFS API.

## Installation

```bash
# Install with uv
uv sync
```

## Local Usage

```bash
# Start the server
cd mcp_server
uv run python server.py
```

## Docker Usage

```bash
# Build
docker build -t bixi-mcp .

# Run
docker run -i bixi-mcp
```

## Claude Desktop Configuration

### Local Server
```json
{
  "mcpServers": {
    "bixi": {
      "command": "uv",
      "args": ["--directory", "/path/to/bixi-mcp/mcp_server", "run", "python", "server.py"]
    }
  }
}
```

### Docker Server
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

## Available Tools

- **Station Info**: `get_stations()`, `get_station(id)`, `search_stations(query)`
- **Real-time Status**: `get_stations_status()`, `get_station_status(id)`, `get_available_stations(min_bikes)`
- **Location**: `find_nearby_stations(lat, lon, radius)`
- **System**: `get_system_info()`, `get_system_alerts()`, `get_system_summary()`
- **Analytics**: `get_stations_with_issues()`, `get_vehicle_types()`

All tools support English (`en`) and French (`fr`) languages.

## License

MIT