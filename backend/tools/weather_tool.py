# backend/src/tools/weather_tool.py

import logging
import requests

logger = logging.getLogger("weather-tool")


# ============================================================
# OPEN-METEO APIs
# ============================================================

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ============================================================
# WEATHER TOOL
# ============================================================

def get_weather(city: str):
    """
    Get current and tomorrow's weather using Open-Meteo.

    Supports international locations including BRICS regions.

    Example:
        get_weather("Jaipur")
        get_weather("Mato Grosso")
        get_weather("Krasnodar")
        get_weather("Heilongjiang")
        get_weather("Free State")
    """

    if not city or not str(city).strip():
        return {
            "success": False,
            "message": "City or region is required."
        }

    city = str(city).strip()

    try:
        # ====================================================
        # 1. GEOCODING
        # ====================================================

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            GEOCODING_URL,
            params=geo_params,
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {
                "success": False,
                "message": f"Location not found: {city}"
            }

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        resolved_city = location.get(
            "name",
            city
        )

        country = location.get(
            "country",
            ""
        )

        country_code = location.get(
            "country_code",
            ""
        )

        # ====================================================
        # 2. WEATHER API
        # ====================================================

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m"
            ),

            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "precipitation_sum"
            ),

            "timezone": "auto",
            "forecast_days": 2
        }

        weather_response = requests.get(
            WEATHER_URL,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        data = weather_response.json()

        # ====================================================
        # 3. EXTRACT CURRENT WEATHER
        # ====================================================

        current = data.get("current", {})
        daily = data.get("daily", {})

        current_temperature = current.get(
            "temperature_2m"
        )

        current_humidity = current.get(
            "relative_humidity_2m"
        )

        current_rainfall = current.get(
            "precipitation"
        )

        current_wind_speed = current.get(
            "wind_speed_10m"
        )

        # ====================================================
        # 4. EXTRACT TOMORROW WEATHER
        # ====================================================

        tomorrow_min = daily.get(
            "temperature_2m_min",
            [None, None]
        )

        tomorrow_max = daily.get(
            "temperature_2m_max",
            [None, None]
        )

        tomorrow_rain_probability = daily.get(
            "precipitation_probability_max",
            [None, None]
        )

        tomorrow_rainfall = daily.get(
            "precipitation_sum",
            [None, None]
        )

        # ====================================================
        # 5. SAFETY CHECK
        # ====================================================

        if len(tomorrow_min) < 2:
            return {
                "success": False,
                "message": (
                    "Tomorrow's temperature forecast "
                    "is unavailable."
                )
            }

        if len(tomorrow_max) < 2:
            return {
                "success": False,
                "message": (
                    "Tomorrow's temperature forecast "
                    "is unavailable."
                )
            }

        if len(tomorrow_rain_probability) < 2:
            return {
                "success": False,
                "message": (
                    "Tomorrow's rain probability "
                    "is unavailable."
                )
            }

        if len(tomorrow_rainfall) < 2:
            return {
                "success": False,
                "message": (
                    "Tomorrow's rainfall forecast "
                    "is unavailable."
                )
            }

        # ====================================================
        # 6. RETURN STANDARDIZED AGRICULTURE WEATHER DATA
        # ====================================================

        result = {
            "success": True,

            "source": "Open-Meteo",

            "city": resolved_city,

            "country": country,

            "country_code": country_code,

            "region": city,

            "latitude": latitude,

            "longitude": longitude,

            # ------------------------------------------------
            # Current weather
            # ------------------------------------------------

            "current": {
                "temperature": current_temperature,

                "humidity": current_humidity,

                "rainfall": current_rainfall,

                "wind_speed": current_wind_speed
            },

            # ------------------------------------------------
            # Tomorrow forecast
            # ------------------------------------------------

            "tomorrow": {
                "min_temperature": tomorrow_min[1],

                "max_temperature": tomorrow_max[1],

                "rain_probability": (
                    tomorrow_rain_probability[1]
                ),

                "rainfall": tomorrow_rainfall[1]
            },

            # ------------------------------------------------
            # Agriculture-friendly summary
            # ------------------------------------------------

            "agriculture_signal": {
                "rain_expected": (
                    tomorrow_rain_probability[1] is not None
                    and tomorrow_rain_probability[1] >= 60
                ),

                "high_rain_probability": (
                    tomorrow_rain_probability[1] is not None
                    and tomorrow_rain_probability[1] >= 80
                ),

                "forecast_rainfall_mm": (
                    tomorrow_rainfall[1]
                )
            }
        }

        logger.info(
            "Weather retrieved successfully: %s, %s",
            resolved_city,
            country
        )

        return result

    # ========================================================
    # NETWORK ERROR
    # ========================================================

    except requests.exceptions.Timeout:

        logger.exception(
            "Weather API timeout for %s",
            city
        )

        return {
            "success": False,
            "message": (
                f"Weather service timed out for {city}. "
                "Please try again."
            )
        }

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except requests.exceptions.ConnectionError:

        logger.exception(
            "Weather API connection error for %s",
            city
        )

        return {
            "success": False,
            "message": (
                "Unable to connect to the weather service."
            )
        }

    # ========================================================
    # HTTP ERROR
    # ========================================================

    except requests.exceptions.HTTPError as exc:

        logger.exception(
            "Weather API HTTP error for %s: %s",
            city,
            exc
        )

        return {
            "success": False,
            "message": (
                "Weather service returned an error."
            )
        }

    # ========================================================
    # JSON / DATA ERROR
    # ========================================================

    except (KeyError, IndexError, TypeError, ValueError) as exc:

        logger.exception(
            "Invalid weather response for %s: %s",
            city,
            exc
        )

        return {
            "success": False,
            "message": (
                "Weather service returned incomplete data."
            )
        }

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as exc:

        logger.exception(
            "Unexpected weather error for %s: %s",
            city,
            exc
        )

        return {
            "success": False,
            "message": (
                f"Unable to retrieve weather for {city}."
            )
        }