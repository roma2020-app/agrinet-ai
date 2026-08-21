import json
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

logger = logging.getLogger("agrinet-recommendation")


# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise RuntimeError(
        "GOOGLE_API_KEY is not set. Please check your .env file."
    )

client = genai.Client(api_key=api_key)


# ============================================================
# AGRICULTURAL ADVISORY PROMPT
# ============================================================

ADVISORY_PROMPT = """
You are AgriNet AI, an agricultural intelligence assistant
for the BRICS Digital Agriculture Intelligence Network.

Your role is to combine structured agricultural data and provide
a practical, localized and sustainable farming advisory.

IMPORTANT:

The supplied values are the source of truth.

Do NOT invent measurements, weather conditions, soil values,
satellite values, crop conditions or government information.

============================================================
FARMER CONTEXT
============================================================

Country:
{country}

Country Code:
{country_code}

Region:
{region}

Farmer ID:
{farmer_id}

Crop:
{crop}

Response Language:
{language}

============================================================
LANGUAGE RULES
============================================================

Generate ALL natural-language advisory fields in the requested
Response Language.

The following fields must be localized:

- crop_condition
- weather_risk
- soil_health
- vegetation_health
- irrigation_recommendation
- regenerative_farming
- immediate_actions
- data_driven_reasoning
- summary

The field "overall_risk" must remain exactly one of:

low
medium
high

Do not translate the JSON field names.

If the requested language is Hindi:

- Write Hindi using Devanagari script.
- Do NOT use Romanized Hindi.
- Use natural agricultural Hindi.
- English technical terms may be used where appropriate.

If the requested language is English:

- Respond completely in English.

============================================================
SOIL INTELLIGENCE
============================================================

{soil_data}

============================================================
WEATHER INTELLIGENCE
============================================================

{weather_data}

============================================================
SATELLITE INTELLIGENCE
============================================================

{satellite_data}

============================================================
ANALYSIS REQUIREMENTS
============================================================

Analyze all supplied information together.

Consider:

1. Crop condition
2. Soil health
3. Weather risk
4. Rainfall / precipitation risk
5. Soil moisture
6. Satellite vegetation health
7. Satellite vegetation trend
8. Irrigation requirement
9. Water-use efficiency
10. Regenerative agriculture
11. Sustainable farming practices
12. Immediate practical actions

The advisory must explain how the different data sources
influence the recommendation.

Examples:

- Soil information should influence nutrient and soil-health advice.
- Weather information should influence irrigation and weather-risk advice.
- Satellite NDVI and vegetation trend should influence crop-health observations.
- Crop type and region should influence practical recommendations.
- Country should influence localization and agricultural context.

============================================================
DATA INTEGRITY
============================================================

Use only the supplied values.

If a value is missing:

- Do not create a replacement value.
- Clearly state that the information is unavailable.

If information is insufficient for a strong recommendation,
clearly state the limitation.

Never contradict supplied measurements.

Satellite observations must respect the supplied observation
date and source.

Do not describe prototype or historical satellite values as
live measurements.

============================================================
SAFETY RULES
============================================================

1. Never claim a crop disease with certainty.
2. Never invent missing data.
3. Never recommend pesticide dosage.
4. Do not recommend unsafe chemical treatments.
5. Do not claim live market prices unless market data is supplied.
6. Do not promise government scheme approval.
7. If information is insufficient, clearly state the limitation.
8. Prefer sustainable and regenerative practices.
9. Prefer water-efficient irrigation.
10. Recommendations must be practical for farmers.
11. Do not contradict supplied measurements.
12. Do not describe prototype satellite values as live measurements.
13. Keep the advisory concise and actionable.

============================================================
REGENERATIVE AGRICULTURE
============================================================

Where appropriate, consider:

- Soil organic matter improvement
- Crop residue management
- Crop rotation
- Reduced soil disturbance
- Efficient irrigation
- Water conservation
- Soil moisture conservation
- Balanced nutrient management
- Cover crops
- Biodiversity
- Crop resilience

Only recommend practices that make sense for the supplied
crop, soil and weather conditions.

============================================================
OUTPUT REQUIREMENTS
============================================================

Return ONLY valid JSON.

Do not use markdown.

Do not use ```json.

Do not add text before or after the JSON.

Return exactly these fields:

{{
    "crop_condition": "string",
    "weather_risk": "string",
    "soil_health": "string",
    "vegetation_health": "string",
    "irrigation_recommendation": "string",
    "regenerative_farming": [
        "string",
        "string"
    ],
    "immediate_actions": [
        "string",
        "string",
        "string"
    ],
    "overall_risk": "low|medium|high",
    "data_driven_reasoning": "string",
    "summary": "string"
}}

Rules:

- overall_risk MUST be exactly low, medium or high.
- regenerative_farming MUST be an array.
- immediate_actions MUST be an array.
- All fields must contain useful information.
- Do not return null.
- Do not return an empty JSON object.
- summary MUST be written in the requested language.
- data_driven_reasoning MUST explain the relationship between
  soil, weather and satellite information.
"""


# ============================================================
# JSON PARSER
# ============================================================

def parse_advisory_json(raw_text: str) -> dict:
    """
    Safely parse Gemini's JSON response.

    Handles:
    - Empty responses
    - Markdown code fences
    - Surrounding text
    - Invalid JSON
    """

    if not raw_text:
        raise ValueError(
            "Gemini returned an empty advisory response."
        )

    text = raw_text.strip()

    # --------------------------------------------------------
    # Remove markdown fences
    # --------------------------------------------------------

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            first_line = lines[0].strip()

            if first_line.startswith("```"):
                lines = lines[1:]

        if lines:
            last_line = lines[-1].strip()

            if last_line == "```":
                lines = lines[:-1]

        text = "\n".join(lines).strip()

    # --------------------------------------------------------
    # Find JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "Gemini response does not contain a valid JSON object."
        )

    text = text[start:end + 1]

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:
        result = json.loads(text)

    except json.JSONDecodeError as exc:

        logger.error(
            "Invalid Gemini advisory JSON: %s",
            text,
        )

        raise ValueError(
            f"Unable to parse Gemini advisory JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Gemini advisory response is not a JSON object."
        )

    return result


# ============================================================
# VALIDATE ADVISORY
# ============================================================

def validate_advisory(result: dict) -> dict:
    """
    Validate and normalize Gemini advisory output.
    """

    required_fields = [
        "crop_condition",
        "weather_risk",
        "soil_health",
        "vegetation_health",
        "irrigation_recommendation",
        "regenerative_farming",
        "immediate_actions",
        "overall_risk",
        "data_driven_reasoning",
        "summary",
    ]

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    missing_fields = [
        field
        for field in required_fields
        if field not in result
    ]

    if missing_fields:
        raise ValueError(
            "Gemini advisory missing fields: "
            + ", ".join(missing_fields)
        )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    risk = str(
        result.get("overall_risk", "")
    ).lower().strip()

    if risk not in {
        "low",
        "medium",
        "high",
    }:
        risk = "medium"

    result["overall_risk"] = risk

    # --------------------------------------------------------
    # String fields
    # --------------------------------------------------------

    string_fields = [
        "crop_condition",
        "weather_risk",
        "soil_health",
        "vegetation_health",
        "irrigation_recommendation",
        "data_driven_reasoning",
        "summary",
    ]

    for field in string_fields:

        value = result.get(field)

        if value is None:
            result[field] = "Information unavailable."

        else:
            result[field] = str(value).strip()

        if not result[field]:
            result[field] = "Information unavailable."

    # --------------------------------------------------------
    # Regenerative farming
    # --------------------------------------------------------

    regenerative = result.get(
        "regenerative_farming"
    )

    if not isinstance(regenerative, list):

        regenerative = [
            str(regenerative)
        ]

    regenerative = [
        str(item).strip()
        for item in regenerative
        if str(item).strip()
    ]

    if not regenerative:

        regenerative = [
            "Use sustainable soil and water management practices."
        ]

    result["regenerative_farming"] = regenerative

    # --------------------------------------------------------
    # Immediate actions
    # --------------------------------------------------------

    actions = result.get(
        "immediate_actions"
    )

    if not isinstance(actions, list):

        actions = [
            str(actions)
        ]

    actions = [
        str(item).strip()
        for item in actions
        if str(item).strip()
    ]

    if not actions:

        actions = [
            "Monitor the crop condition in the field."
        ]

    result["immediate_actions"] = actions

    return result


# ============================================================
# SAFE FALLBACK
# ============================================================

def _fallback_advisory(
    language: str,
    error: Exception,
) -> dict:
    """
    Safe localized fallback when Gemini advisory generation fails.
    """

    language_lower = (
        language or "English"
    ).lower().strip()

    # ========================================================
    # HINDI FALLBACK
    # ========================================================

    if language_lower in {
        "hindi",
        "hi",
        "हिंदी",
    }:

        return {
            "crop_condition": (
                "एआई फसल मूल्यांकन उपलब्ध नहीं हो सका।"
            ),

            "weather_risk": (
                "मौसम जोखिम का एआई मूल्यांकन पूरा नहीं हो सका।"
            ),

            "soil_health": (
                "मिट्टी की जानकारी प्राप्त हुई, लेकिन एआई विश्लेषण "
                "पूरा नहीं हो सका।"
            ),

            "vegetation_health": (
                "सैटेलाइट जानकारी प्राप्त हुई, लेकिन एआई विश्लेषण "
                "पूरा नहीं हो सका।"
            ),

            "irrigation_recommendation": (
                "उपलब्ध मिट्टी की नमी और सत्यापित स्थानीय कृषि "
                "सलाह के अनुसार सिंचाई करें।"
            ),

            "regenerative_farming": [
                "मिट्टी की नमी संरक्षण की प्रथाओं को बनाए रखें।",
                "सतत मिट्टी और जल प्रबंधन को प्राथमिकता दें।",
            ],

            "immediate_actions": [
                "उपलब्ध मिट्टी, मौसम और सैटेलाइट जानकारी की समीक्षा करें।",
                "खेत में फसल की स्थिति की निगरानी करें।",
                "फसल में तनाव दिखाई देने पर स्थानीय कृषि विशेषज्ञ से सलाह लें।",
            ],

            "overall_risk": "medium",

            "data_driven_reasoning": (
                "एआई सलाह उपलब्ध नहीं हो सकी। मिट्टी, मौसम और "
                "सैटेलाइट जानकारी की संयुक्त समीक्षा के बाद ही "
                "महत्वपूर्ण कृषि निर्णय लें।"
            ),

            "summary": (
                "एआई कृषि सलाह फिलहाल उपलब्ध नहीं है। "
                "कृपया उपलब्ध कृषि जानकारी की समीक्षा करें।"
            ),

            "error": str(error),
        }

    # ========================================================
    # DEFAULT / ENGLISH FALLBACK
    # ========================================================

    return {
        "crop_condition": (
            "Unable to generate AI crop assessment."
        ),

        "weather_risk": (
            "Weather risk could not be assessed by Gemini."
        ),

        "soil_health": (
            "Soil information was received, but AI analysis "
            "could not be completed."
        ),

        "vegetation_health": (
            "Satellite information was received, but AI "
            "analysis could not be completed."
        ),

        "irrigation_recommendation": (
            "Use irrigation according to observed soil "
            "moisture and verified local agricultural guidance."
        ),

        "regenerative_farming": [
            "Maintain soil moisture conservation practices.",
            "Prefer sustainable soil and water management.",
        ],

        "immediate_actions": [
            "Review the available soil, weather and satellite data.",
            "Monitor the crop condition in the field.",
            "Consult a local agriculture expert if crop stress is observed.",
        ],

        "overall_risk": "medium",

        "data_driven_reasoning": (
            "AI advisory generation was temporarily unavailable. "
            "The supplied soil, weather and satellite measurements "
            "should be reviewed before making major farm decisions."
        ),

        "summary": (
            "AI advisory is temporarily unavailable. "
            "Please review the available agricultural information."
        ),

        "error": str(error),
    }


# ============================================================
# GENERATE ADVISORY
# ============================================================

def generate_advisory(
    soil_data,
    weather_data,
    satellite_data,
    country="India",
    region="",
    crop="",
    language="English",
    country_code="",
    farmer_id="",
):
    """
    Generate a localized agricultural advisory using Gemini.

    Inputs:
        soil_data
        weather_data
        satellite_data
        country
        region
        crop
        language
        country_code
        farmer_id

    Returns:
        Structured advisory dictionary.
    """

    try:

        # ====================================================
        # BUILD PROMPT
        # ====================================================

        prompt = ADVISORY_PROMPT.format(
            country=country or "Unknown",
            country_code=country_code or "Unknown",
            region=region or "Unknown",
            farmer_id=farmer_id or "Unknown",
            crop=crop or "Unknown",
            language=language or "English",

            soil_data=json.dumps(
                soil_data,
                ensure_ascii=False,
                indent=2,
            ),

            weather_data=json.dumps(
                weather_data,
                ensure_ascii=False,
                indent=2,
            ),

            satellite_data=json.dumps(
                satellite_data,
                ensure_ascii=False,
                indent=2,
            ),
        )

        # ====================================================
        # LOG REQUEST
        # ====================================================

        logger.info(
            "Generating AgriNet advisory | "
            "country=%s | country_code=%s | region=%s | "
            "farmer_id=%s | crop=%s | language=%s",
            country,
            country_code,
            region,
            farmer_id,
            crop,
            language,
        )

        # ====================================================
        # GEMINI REQUEST
        # ====================================================

        response = client.models.generate_content(
            model="gemini-2.5-flash",

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        # ====================================================
        # RESPONSE VALIDATION
        # ====================================================

        if not response:

            raise ValueError(
                "Gemini returned no response."
            )

        raw_text = getattr(
            response,
            "text",
            None,
        )

        if not raw_text:

            raise ValueError(
                "Gemini returned an empty advisory response."
            )

        raw_text = raw_text.strip()

        logger.debug(
            "Raw Gemini advisory response: %s",
            raw_text,
        )

        # ====================================================
        # PARSE JSON
        # ====================================================

        result = parse_advisory_json(
            raw_text
        )

        # ====================================================
        # VALIDATE
        # ====================================================

        result = validate_advisory(
            result
        )

        # ====================================================
        # SUCCESS LOG
        # ====================================================

        logger.info(
            "AgriNet advisory generated successfully | "
            "country=%s | country_code=%s | language=%s | risk=%s",
            country,
            country_code,
            language,
            result.get("overall_risk"),
        )

        return result

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as exc:

        logger.exception(
            "AgriNet advisory generation failed | "
            "country=%s | country_code=%s | region=%s | "
            "farmer_id=%s | crop=%s | language=%s | error=%s",
            country,
            country_code,
            region,
            farmer_id,
            crop,
            language,
            exc,
        )

        return _fallback_advisory(
            language=language,
            error=exc,
        )
