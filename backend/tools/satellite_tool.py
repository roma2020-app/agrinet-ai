# ============================================================
# AgriNet AI - Satellite Intelligence
# ============================================================
#
# Prototype / demo satellite intelligence layer.
#
# Data is representative Sentinel-2 / NDVI data used to
# demonstrate the interoperable agriculture architecture.
#
# These values should NOT be presented to judges as live
# satellite measurements.
#
# Future production integration:
# Google Earth Engine / Copernicus Sentinel APIs
# ============================================================


SATELLITE_DATA = {

    # ========================================================
    # INDIA
    # ========================================================

    "Jaipur": {
        "source": "Copernicus Sentinel-2",
        "data_type": "Representative NDVI",
        "ndvi": 0.62,
        "vegetation_health": "Moderate",
        "vegetation_trend": "Declining",
        "observation_date": "2026-08-15"
    },

    # ========================================================
    # BRAZIL
    # ========================================================

    "Mato Grosso": {
        "source": "Copernicus Sentinel-2",
        "data_type": "Representative NDVI",
        "ndvi": 0.74,
        "vegetation_health": "Good",
        "vegetation_trend": "Stable",
        "observation_date": "2026-08-15"
    },

    # ========================================================
    # RUSSIA
    # ========================================================

    "Krasnodar": {
        "source": "Copernicus Sentinel-2",
        "data_type": "Representative NDVI",
        "ndvi": 0.68,
        "vegetation_health": "Good",
        "vegetation_trend": "Stable",
        "observation_date": "2026-08-15"
    },

    # ========================================================
    # CHINA
    # ========================================================

    "Henan": {
        "source": "Copernicus Sentinel-2",
        "data_type": "Representative NDVI",
        "ndvi": 0.71,
        "vegetation_health": "Good",
        "vegetation_trend": "Improving",
        "observation_date": "2026-08-15"
    },

    # Keep Heilongjiang as an additional supported region
    "Heilongjiang": {
        "source": "Copernicus Sentinel-2",
        "data_type": "Representative NDVI",
        "ndvi": 0.71,
        "vegetation_health": "Good",
        "vegetation_trend": "Improving",
        "observation_date": "2026-08-15"
    },

    # ========================================================
    # SOUTH AFRICA
    # ========================================================

    "Free State": {
        "source": "Copernicus Sentinel-2",
        "data_type": "Representative NDVI",
        "ndvi": 0.55,
        "vegetation_health": "Moderate",
        "vegetation_trend": "Declining",
        "observation_date": "2026-08-15"
    }
}


# ============================================================
# GET SATELLITE DATA
# ============================================================

def get_satellite_data(region: str):

    if not region:
        return {
            "success": False,
            "message": "Region is required for satellite lookup."
        }

    # --------------------------------------------------------
    # Normalize region
    # --------------------------------------------------------

    region_clean = region.strip()

    # --------------------------------------------------------
    # Exact match first
    # --------------------------------------------------------

    data = SATELLITE_DATA.get(region_clean)

    # --------------------------------------------------------
    # Case-insensitive fallback
    # --------------------------------------------------------

    if not data:

        for key, value in SATELLITE_DATA.items():

            if key.lower() == region_clean.lower():
                data = value
                region_clean = key
                break

    # --------------------------------------------------------
    # No data
    # --------------------------------------------------------

    if not data:

        return {
            "success": False,
            "message": (
                f"No satellite data available for {region}. "
                "Supported prototype regions: "
                + ", ".join(SATELLITE_DATA.keys())
            )
        }

    # --------------------------------------------------------
    # Successful response
    # --------------------------------------------------------

    return {
        "success": True,

        "region": region_clean,

        "data": data
    }

    #This is prototype/demo satellite intelligence. Don't describe these values to judges as live measurements. Describe them as representative Sentinel-2/NDVI data used to demonstrate the interoperable architecture.

#Later, if time permits, we can replace this layer with Google Earth Engine data.