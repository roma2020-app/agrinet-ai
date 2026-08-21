import json
from pathlib import Path


# ============================================================
# FARMERS DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FARMERS_FILE = BASE_DIR / "data" / "farmers.json"


def load_farmers():

    if not FARMERS_FILE.exists():
        return {
            "success": False,
            "message": f"Farmers file not found: {FARMERS_FILE}"
        }

    try:

        with open(FARMERS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return {
            "success": True,
            "data": data.get("farmers", [])
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Unable to read farmers.json: {str(e)}"
        }


# ============================================================
# GET SOIL DATA
# ============================================================

def get_soil_data(farmer_id: str):

    result = load_farmers()

    if not result["success"]:
        return result

    farmers = result["data"]

    farmer = next(
        (
            farmer
            for farmer in farmers
            if farmer.get("farmer_id", "").lower()
            == farmer_id.lower()
        ),
        None
    )

    if not farmer:

        return {
            "success": False,
            "message": f"No farmer found for ID: {farmer_id}"
        }

    soil = farmer.get("soil")

    if not soil:

        return {
            "success": False,
            "message": f"No soil data available for {farmer_id}"
        }

    return {
        "success": True,
        "data": {
            "farmer_id": farmer.get("farmer_id"),
            "name": farmer.get("name"),

            "country_code": farmer.get("country_code"),
            "country": farmer.get("country"),

            "region": farmer.get("region"),
            "state": farmer.get("state"),
            "district": farmer.get("district"),

            "crop": farmer.get("crop"),
            "crops": farmer.get("crops"),

            "land_size": farmer.get("land_size"),
            "land_unit": farmer.get("land_unit"),

            "irrigation_type": farmer.get("irrigation_type"),
            "season": farmer.get("season"),

            "soil": soil,

            # Keep these available for your existing code
            "ph": soil.get("ph"),
            "nitrogen": soil.get("nitrogen"),
            "phosphorus": soil.get("phosphorus"),
            "potassium": soil.get("potassium"),
            "organic_carbon": soil.get("organic_carbon"),
            "moisture": soil.get("moisture"),

            "last_interaction": farmer.get("last_interaction")
        }
    }