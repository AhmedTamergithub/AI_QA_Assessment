from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class WeatherData(BaseModel):
    """Detailed weather information."""
    city: str = Field(description="The name of the city")
    temperature: float = Field(description="Current temperature")
    wind_speed: Optional[float] = Field(default=None, description="Current wind speed")
    weather_code: Optional[int] = Field(default=None, description="WMO weather code")
    unit: Optional[str] = Field(default="celsius", description="Temperature unit (celsius/fahrenheit)")

class ExchangeRateData(BaseModel):
    """Detailed exchange rate information."""
    base: str = Field(description="Base currency code")
    target: str = Field(description="Target currency code")
    rate: float = Field(description="Exchange rate value")

class APIFetchingOutput(BaseModel):
    """Deterministic output schema for the API Fetching Agent."""
    conversational_response: str = Field(description="A helpful conversational response for the user summarizing the results.")
    weather: Optional[WeatherData] = Field(default=None, description="The weather data returned by the tool")
    exchange_rate: Optional[ExchangeRateData] = Field(default=None, description="The exchange rate data returned by the tool")
