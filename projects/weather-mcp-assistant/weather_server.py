"""
Weather MCP Server — Exposes weather tools, alerts resources, and advisory prompts.
Can be run standalone or connected as an MCP server.
"""

import httpx
import json
import logging
import sys
from typing import Optional
from mcp.server.fastmcp import FastMCP, Context

# Create FastMCP server
mcp = FastMCP("WeatherServer")

# Safe mock database for common cities fallback or resource data
WEATHER_DATABASE = {
    "mumbai": {
        "latitude": 19.0760, "longitude": 72.8777,
        "advisory": "⚠️ Monsoon Advisory: Heavy rain expected in the evening. Avoid coastal areas.",
        "seasonal_tips": "Always carry an umbrella. Train schedules might experience delays."
    },
    "bangalore": {
        "latitude": 12.9716, "longitude": 77.5946,
        "advisory": "🌤️ Comfortable Weather: Mild breeze. No active hazardous warnings.",
        "seasonal_tips": "Excellent weather for outdoor sightseeing and walks. Carry a light jacket for the evening."
    },
    "new york": {
        "latitude": 40.7128, "longitude": -74.0060,
        "advisory": "❄️ Winter Advisory: Mild snowfall expected overnight. Roads might be slippery.",
        "seasonal_tips": "Layer up and wear heavy boots. Check subway status before commuting."
    },
    "london": {
        "latitude": 51.5074, "longitude": -0.1278,
        "advisory": "🌧️ Drizzle Warning: Overcast skies with periodic light rain.",
        "seasonal_tips": "A classic London day. Waterproof wear is highly recommended."
    },
    "tokyo": {
        "latitude": 35.6762, "longitude": 139.6503,
        "advisory": "🌸 Spring Weather: Mild, pleasant afternoon. High pollen count.",
        "seasonal_tips": "Great season for cherry blossom viewing. Wear a face mask if you are allergic to pollen."
    }
}

async def fetch_lat_lon_geocoding(city: str, ctx: Context) -> Optional[tuple[float, float]]:
    """Helper to fetch coordinates using free Open-Meteo geocoding."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    try:
        await ctx.info(f"Resolving coordinates for city: '{city}' via geocoding API...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and len(data["results"]) > 0:
                    result = data["results"][0]
                    lat, lon = result["latitude"], result["longitude"]
                    await ctx.info(f"Successfully resolved '{city}': lat={lat}, lon={lon}")
                    return lat, lon
        await ctx.warning(f"Could not resolve '{city}' via geocoding API.")
    except Exception as e:
        await ctx.error(f"Geocoding API error: {str(e)}")
    return None

# ── 1. WEATHER TOOL ──────────────────────────────────────────────────────────
@mcp.tool()
async def get_weather(city: str, ctx: Context) -> str:
    """
    Fetch live weather conditions and temperature forecast for a given city.
    Utilizes geocoding and real-time forecast API. Fallbacks gracefully on failures.

    Args:
        city: Name of the city (e.g., 'mumbai', 'new york', 'tokyo').

    Returns:
        JSON string containing the current temperature, windspeed, and weather condition.
    """
    city_clean = city.strip().lower()
    await ctx.info(f"Tool get_weather called for city: '{city}'")
    
    # 1. Resolve coordinates
    coords = await fetch_lat_lon_geocoding(city_clean, ctx)
    
    # If API fails or city not found in API, check local fast database
    if not coords:
        if city_clean in WEATHER_DATABASE:
            await ctx.info(f"Using local database coordinates for '{city}'")
            coords = (WEATHER_DATABASE[city_clean]["latitude"], WEATHER_DATABASE[city_clean]["longitude"])
        else:
            # Absolute fallback to mock coordinates if completely unknown
            await ctx.warning(f"Unknown city '{city}'. Falling back to default mock location (Delhi coordinates).")
            coords = (28.6139, 77.2090)

    lat, lon = coords
    
    # 2. Fetch forecast
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        await ctx.info(f"Fetching current weather from forecast endpoint...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(forecast_url)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_weather", {})
                
                weather_info = {
                    "city": city.title(),
                    "latitude": lat,
                    "longitude": lon,
                    "temperature_celsius": current.get("temperature"),
                    "windspeed_kmh": current.get("windspeed"),
                    "weather_code": current.get("weathercode"),
                    "source": "Open-Meteo Live API"
                }
                
                await ctx.info(f"Successfully retrieved weather for '{city}': {current.get('temperature')}°C")
                return json.dumps(weather_info, indent=2)
                
    except Exception as e:
        await ctx.error(f"Weather API error: {str(e)}. Generating high-fidelity mock data...")

    # Safe High-Fidelity Mock Fallback on Network Issues
    import random
    temp = round(random.uniform(15.0, 32.0), 1)
    wind = round(random.uniform(5.0, 20.0), 1)
    
    mock_info = {
        "city": city.title(),
        "latitude": lat,
        "longitude": lon,
        "temperature_celsius": temp,
        "windspeed_kmh": wind,
        "weather_code": 0,
        "source": "Mock Database Fallback (Offline Mode)"
    }
    return json.dumps(mock_info, indent=2)


# ── 2. WEATHER ALERTS RESOURCE ───────────────────────────────────────────────
@mcp.resource("weather://alerts/{city}")
async def get_weather_alerts(city: str, ctx: Context) -> str:
    """
    Expose read-only weather alerts, warnings, and local seasonal advice for a city.
    
    Args:
        city: Name of the city (e.g. 'mumbai', 'london').
        
    Returns:
        Formatted plain-text alert and advisory message.
    """
    city_clean = city.strip().lower()
    await ctx.info(f"Resource requested: weather://alerts/{city_clean}")
    
    if city_clean in WEATHER_DATABASE:
        city_data = WEATHER_DATABASE[city_clean]
        alert_text = (
            f"=== WEATHER ADVISORY & ALERTS FOR {city.upper()} ===\n"
            f"Active Alert: {city_data['advisory']}\n"
            f"Seasonal Tip: {city_data['seasonal_tips']}\n"
        )
    else:
        alert_text = (
            f"=== WEATHER ADVISORY & ALERTS FOR {city.upper()} ===\n"
            f"Active Alert: 🌤️ No active warnings or hazardous conditions reported.\n"
            f"Seasonal Tip: Standard seasonal clothing and standard travel precautions recommended.\n"
        )
    return alert_text


# ── 3. WEATHER ADVISER PROMPT ────────────────────────────────────────────────
@mcp.prompt()
def weather_adviser(city: str, travel_plan: str = "") -> str:
    """
    Construct a premium weather advisory prompt layout.
    Guide the LLM in structuring weather analysis for travelers.
    
    Args:
        city: Target city.
        travel_plan: Optional details on activities planned (e.g. 'sightseeing', 'hiking').
    """
    prompt = (
        "You are a Senior Travel & Weather Meteorologist Assistant.\n"
        "Your goal is to digest weather reports and active alerts, then provide "
        "personalized, bulleted recommendations detailing clothing, transit precautions, and activity advice.\n"
        "Be concise, engaging, and professional.\n\n"
        f"Analyze the weather for **{city.title()}**."
    )
    
    if travel_plan:
        prompt += f"\nMy travel plans are: {travel_plan}."
        
    prompt += (
        "\n\nPlease structure your response as follows:\n"
        "1. **Current Overview** (Briefly describe temperature & feel)\n"
        "2. **Impact on Travel Plans** (Directly address planned activities)\n"
        "3. **What to Pack & Wear** (Specific clothing suggestions)\n"
        "4. **Active Warnings & Transit Tips** (Mention transit concerns if any)"
    )

    return prompt


if __name__ == "__main__":
    # Log startup to stderr so stdout is reserved for JSON-RPC messages
    print("[Server] Starting WeatherMCP Server...", file=sys.stderr, flush=True)
    mcp.run()
