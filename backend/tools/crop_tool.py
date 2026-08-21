# ============================================================
# AgriNet AI - BRICS Crop Intelligence
# ============================================================
#
# Country-specific crop options for the AgriNet AI prototype.
#
# This provides localized crop options based on country context.
# In a production deployment, these can be connected to
# national agricultural datasets and crop suitability models.
# ============================================================


# ============================================================
# BRICS CROP OPTIONS
# ============================================================

CROP_OPTIONS = {

    "India": [
        "Millet",
        "Pulses",
        "Wheat",
        "Mustard",
        "Groundnut"
    ],

    "Brazil": [
        "Soybean",
        "Maize",
        "Beans",
        "Sorghum"
    ],

    "Russia": [
        "Wheat",
        "Barley",
        "Sunflower",
        "Rapeseed"
    ],

    "China": [
        "Rice",
        "Maize",
        "Soybean",
        "Wheat"
    ],

    "South Africa": [
        "Maize",
        "Sorghum",
        "Sunflower",
        "Wheat"
    ]
}


# ============================================================
# COUNTRY CODE → COUNTRY NAME
# ============================================================

COUNTRY_CODES = {

    "IN": "India",
    "BR": "Brazil",
    "RU": "Russia",
    "CN": "China",
    "ZA": "South Africa"
}


# ============================================================
# GET CROP OPTIONS
# ============================================================

def get_crop_options(country: str):

    if not country:
        return {
            "success": False,
            "message": "Country is required."
        }

    country_clean = country.strip()

    # --------------------------------------------------------
    # Direct country name lookup
    # --------------------------------------------------------

    matched_country = None

    for country_name in CROP_OPTIONS:

        if country_name.lower() == country_clean.lower():

            matched_country = country_name
            break

    # --------------------------------------------------------
    # Country code lookup
    # --------------------------------------------------------

    if not matched_country:

        country_code = country_clean.upper()

        matched_country = COUNTRY_CODES.get(country_code)

    # --------------------------------------------------------
    # No country found
    # --------------------------------------------------------

    if not matched_country:

        return {
            "success": False,
            "message": (
                f"No crop data available for {country}."
            )
        }

    # --------------------------------------------------------
    # Get crops
    # --------------------------------------------------------

    crops = CROP_OPTIONS.get(matched_country, [])

    if not crops:

        return {
            "success": False,
            "message": (
                f"No crop options configured for "
                f"{matched_country}."
            )
        }

    # --------------------------------------------------------
    # Successful response
    # --------------------------------------------------------

    return {

        "success": True,

        "country": matched_country,

        "country_code": next(
            (
                code
                for code, name in COUNTRY_CODES.items()
                if name == matched_country
            ),
            None
        ),

        "recommended_crop_options": crops
    }


# ============================================================
# GET ALL COUNTRY CROP OPTIONS
# ============================================================

def get_all_crop_options():

    return {
        "success": True,
        "countries": [
            {
                "country_code": code,
                "country": country,
                "recommended_crop_options": CROP_OPTIONS[country]
            }
            for code, country in COUNTRY_CODES.items()
        ]
    }