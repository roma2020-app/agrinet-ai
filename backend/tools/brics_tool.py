import json
from pathlib import Path


DATA_FILE = Path(__file__).parent.parent / "data" / "brics_regions.json"


def load_brics_data():

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_country(country_code: str):

    data = load_brics_data()

    country_code = country_code.upper()

    country = data.get(country_code)

    if not country:
        return {
            "success": False,
            "message": f"Country code {country_code} is not supported"
        }

    return {
        "success": True,
        "country": country
    }


def get_all_countries():

    data = load_brics_data()

    countries = []

    for code, country in data.items():

        countries.append({
            "code": code,
            "country": country["country_name"],
            "region": country["region"],
            "language": country["language"]
        })

    return {
        "success": True,
        "countries": countries
    }
