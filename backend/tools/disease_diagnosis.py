# backend/src/tools/disease_diagnosis.py

import json
import logging
import os
import time

from google import genai
from google.genai import types
from google.genai import errors


logger = logging.getLogger("disease-diagnosis")


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

SUPPORTED_LANGUAGES = {
    "English": "English",
    "Hindi": "Hindi",
    "Portuguese": "Portuguese",
    "Russian": "Russian",
    "Chinese": "Chinese",
}


def normalize_language(language: str) -> str:
    """
    Normalize language received from frontend/backend.

    Supported:
        English
        Hindi
        Portuguese
        Russian
        Chinese

    Unknown values fall back to English.
    """

    if not language:
        return "English"

    language_clean = str(language).strip().lower()

    language_map = {
        "english": "English",
        "en": "English",

        "hindi": "Hindi",
        "hi": "Hindi",

        "portuguese": "Portuguese",
        "pt": "Portuguese",
        "pt-br": "Portuguese",
        "brazilian portuguese": "Portuguese",

        "russian": "Russian",
        "ru": "Russian",

        "chinese": "Chinese",
        "zh": "Chinese",
        "zh-cn": "Chinese",
        "simplified chinese": "Chinese",
    }

    return language_map.get(
        language_clean,
        "English",
    )


# ============================================================
# GEMINI DISEASE DIAGNOSIS PROMPT
# ============================================================

DISEASE_PROMPT = """
You are AgriNet AI, a multilingual agricultural crop-health
screening assistant for farmers across BRICS countries.

Analyze the supplied crop or leaf image carefully.

This is agricultural SCREENING, NOT a guaranteed diagnosis.

Identify the most likely visible crop problem only when there
is sufficient visual evidence.

If the image is unclear, blurry, poorly framed, or does not
contain a recognizable crop or leaf, clearly state that the
image is insufficient.

============================================================
SAFETY RULES
============================================================

1. Never claim a guaranteed diagnosis.

2. Never invent symptoms that are not visible in the image.

3. Never recommend pesticide dosage.

4. Never recommend unsafe chemical treatment.

5. Prefer practical non-chemical actions.

6. Recommend an agricultural expert when confidence is low.

7. Recommend an agricultural expert when the crop appears
   seriously damaged.

8. If the crop cannot be identified confidently, use:
   "Unknown crop".

9. The farmer-facing summary MUST be written in the requested
   farmer language.

10. Recommendations MUST also be written in the requested
    farmer language.

11. Keep recommendations concise and practical.

12. Do not provide medical advice.

13. Do not make government-scheme eligibility guarantees.

============================================================
VISUAL EVIDENCE RULE
============================================================

Only describe symptoms that can actually be observed in the
supplied image.

Do not invent:

- leaf spots
- discoloration
- insects
- fungus
- wilting
- nutrient deficiency
- disease symptoms
- pest damage

unless they are visually supported by the image.

If there is not enough visual evidence, explicitly state that
the image is insufficient.

============================================================
LANGUAGE RULE
============================================================

The requested farmer language is provided separately.

You MUST follow it.

Supported languages:

- English
- Hindi
- Portuguese
- Russian
- Chinese

IMPORTANT:

ALL farmer-facing textual fields MUST use the requested language.

These fields must be translated:

- possible_condition
- visible_symptoms
- likely_cause
- recommended_next_steps
- summary

The crop field should also use the requested language when
a natural crop name exists.

For example:

English:
Rice

Hindi:
धान

Portuguese:
Arroz

Russian:
Рис

Chinese:
水稻

If the crop cannot be identified, use the appropriate
translation of "Unknown crop".

For example:

English:
Unknown crop

Hindi:
अज्ञात फसल

Portuguese:
Cultura desconhecida

Russian:
Неизвестная культура

Chinese:
未知作物

============================================================
HINDI RULE
============================================================

For Hindi:

- Use Devanagari script.
- Do NOT write Hindi using Roman letters.
- Technical agricultural terms such as NDVI, AI and
  satellite may remain in English when natural.

============================================================
PORTUGUESE RULE
============================================================

For Portuguese:

- Use natural Brazilian Portuguese.
- Do NOT return English sentences.
- Farmer-facing content must be Portuguese.

============================================================
RUSSIAN RULE
============================================================

For Russian:

- Use natural Russian.
- Do NOT return English sentences.
- Farmer-facing content must be Russian.

============================================================
CHINESE RULE
============================================================

For Chinese:

- Use Simplified Chinese.
- Do NOT return English sentences.
- Farmer-facing content must be Simplified Chinese.

============================================================
ENGLISH RULE
============================================================

For English:

- Use natural English.

============================================================
IMPORTANT
============================================================

Do NOT generate multiple language versions.

Generate ONLY the requested farmer language.

Return ONLY valid JSON matching the requested schema.
"""


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

DIAGNOSIS_SCHEMA = {
    "type": "object",
    "properties": {

        "crop": {
            "type": "string",
            "description": (
                "Identified crop written in the requested "
                "farmer language. If unknown, translate "
                "Unknown crop into the requested language."
            ),
        },

        "possible_condition": {
            "type": "string",
            "description": (
                "Most likely visible crop condition. "
                "Must be written in the requested farmer "
                "language and must not claim certainty."
            ),
        },

        "confidence": {
            "type": "string",
            "enum": [
                "low",
                "medium",
                "high",
            ],
        },

        "severity": {
            "type": "string",
            "enum": [
                "low",
                "moderate",
                "high",
                "unknown",
            ],
        },

        "image_quality": {
            "type": "string",
            "enum": [
                "good",
                "acceptable",
                "poor",
            ],
        },

        "visible_symptoms": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": (
                "Only symptoms actually visible in the image. "
                "Write in requested farmer language."
            ),
        },

        "likely_cause": {
            "type": "string",
            "description": (
                "Possible cause based only on visible evidence. "
                "Write in requested farmer language."
            ),
        },

        "recommended_next_steps": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": (
                "Practical safe next steps. "
                "Write in requested farmer language."
            ),
        },

        "expert_needed": {
            "type": "boolean",
        },

        "summary": {
            "type": "string",
            "description": (
                "Short farmer-facing summary in the "
                "requested language."
            ),
        },

    },

    "required": [
        "crop",
        "possible_condition",
        "confidence",
        "severity",
        "image_quality",
        "visible_symptoms",
        "likely_cause",
        "recommended_next_steps",
        "expert_needed",
        "summary",
    ],
}


# ============================================================
# GEMINI CLIENT
# ============================================================

def _get_client():
    """
    Create Gemini client.

    Supports:
        GEMINI_API_KEY
        GOOGLE_API_KEY
    """

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY or GOOGLE_API_KEY is not configured."
        )

    return genai.Client(
        api_key=api_key
    )


# ============================================================
# VALIDATE / NORMALIZE DIAGNOSIS
# ============================================================

def validate_diagnosis(
    result: dict,
    language: str = "English",
) -> dict:

    required_fields = [
        "crop",
        "possible_condition",
        "confidence",
        "severity",
        "image_quality",
        "visible_symptoms",
        "likely_cause",
        "recommended_next_steps",
        "expert_needed",
        "summary",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in result
    ]

    if missing_fields:
        raise ValueError(
            "Gemini response missing fields: "
            + ", ".join(missing_fields)
        )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = str(
        result["confidence"]
    ).lower().strip()

    if confidence not in {
        "low",
        "medium",
        "high",
    }:
        confidence = "low"

    result["confidence"] = confidence

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    severity = str(
        result["severity"]
    ).lower().strip()

    if severity not in {
        "low",
        "moderate",
        "high",
        "unknown",
    }:
        severity = "unknown"

    result["severity"] = severity

    # --------------------------------------------------------
    # Image Quality
    # --------------------------------------------------------

    image_quality = str(
        result["image_quality"]
    ).lower().strip()

    if image_quality not in {
        "good",
        "acceptable",
        "poor",
    }:
        image_quality = "poor"

    result["image_quality"] = image_quality

    # --------------------------------------------------------
    # Visible Symptoms
    # --------------------------------------------------------

    if not isinstance(
        result["visible_symptoms"],
        list,
    ):
        result["visible_symptoms"] = [
            str(result["visible_symptoms"])
        ]

    result["visible_symptoms"] = [
        str(item).strip()
        for item in result["visible_symptoms"]
        if str(item).strip()
    ]

    # --------------------------------------------------------
    # Recommended Next Steps
    # --------------------------------------------------------

    if not isinstance(
        result["recommended_next_steps"],
        list,
    ):
        result["recommended_next_steps"] = [
            str(result["recommended_next_steps"])
        ]

    result["recommended_next_steps"] = [
        str(item).strip()
        for item in result["recommended_next_steps"]
        if str(item).strip()
    ]

    # --------------------------------------------------------
    # Expert Needed
    # --------------------------------------------------------

    expert_needed = result["expert_needed"]

    if isinstance(expert_needed, bool):

        result["expert_needed"] = expert_needed

    elif isinstance(expert_needed, str):

        result["expert_needed"] = (
            expert_needed.lower().strip()
            == "true"
        )

    else:

        result["expert_needed"] = bool(
            expert_needed
        )

    # --------------------------------------------------------
    # Safety Normalization
    # --------------------------------------------------------

    if result["confidence"] == "low":
        result["expert_needed"] = True

    if result["severity"] == "high":
        result["expert_needed"] = True

    if result["image_quality"] == "poor":
        result["expert_needed"] = True

    # --------------------------------------------------------
    # String Fields
    # --------------------------------------------------------

    string_fields = [
        "crop",
        "possible_condition",
        "likely_cause",
        "summary",
    ]

    for field in string_fields:

        result[field] = str(
            result[field]
        ).strip()

    # --------------------------------------------------------
    # Language-specific fallback values
    # --------------------------------------------------------

    fallback_values = {

        "English": {
            "crop": "Unknown crop",
            "condition": "Insufficient visual evidence",
            "summary": (
                "The image does not provide enough "
                "visual evidence for reliable screening."
            ),
        },

        "Hindi": {
            "crop": "अज्ञात फसल",
            "condition": "पर्याप्त दृश्य प्रमाण उपलब्ध नहीं है",
            "summary": (
                "तस्वीर में विश्वसनीय स्क्रीनिंग के लिए "
                "पर्याप्त दृश्य प्रमाण उपलब्ध नहीं है।"
            ),
        },

        "Portuguese": {
            "crop": "Cultura desconhecida",
            "condition": "Evidência visual insuficiente",
            "summary": (
                "A imagem não apresenta evidências visuais "
                "suficientes para uma triagem confiável."
            ),
        },

        "Russian": {
            "crop": "Неизвестная культура",
            "condition": "Недостаточно визуальных данных",
            "summary": (
                "На изображении недостаточно визуальных "
                "данных для надежного скрининга."
            ),
        },

        "Chinese": {
            "crop": "未知作物",
            "condition": "视觉证据不足",
            "summary": (
                "图片中的视觉信息不足，无法进行可靠的作物健康筛查。"
            ),
        },
    }

    fallback = fallback_values.get(
        language,
        fallback_values["English"],
    )

    # --------------------------------------------------------
    # Prevent Empty Crop
    # --------------------------------------------------------

    if not result["crop"]:

        result["crop"] = fallback["crop"]

    # --------------------------------------------------------
    # Prevent Empty Condition
    # --------------------------------------------------------

    if not result["possible_condition"]:

        result["possible_condition"] = (
            fallback["condition"]
        )

    # --------------------------------------------------------
    # Prevent Empty Summary
    # --------------------------------------------------------

    if not result["summary"]:

        result["summary"] = (
            fallback["summary"]
        )

    # --------------------------------------------------------
    # If image is poor, force insufficient evidence
    # when Gemini returned no symptoms.
    # --------------------------------------------------------

    if (
        result["image_quality"] == "poor"
        and not result["visible_symptoms"]
    ):

        result["possible_condition"] = (
            fallback["condition"]
        )

        result["expert_needed"] = True

    # --------------------------------------------------------
    # Language Metadata
    # --------------------------------------------------------

    result["language"] = language

    return result


# ============================================================
# GEMINI VISION CALL
# ============================================================

def _generate_diagnosis(
    client,
    image_part,
    language="English",
    country="India",
):

    max_attempts = 3

    normalized_language = normalize_language(
        language
    )

    prompt = f"""
{DISEASE_PROMPT}

============================================================
REQUEST CONTEXT
============================================================

COUNTRY:
{country}

FARMER LANGUAGE:
{normalized_language}

============================================================
STRICT LANGUAGE REQUIREMENT
============================================================

The farmer selected:

{normalized_language}

Therefore:

ALL farmer-facing textual fields MUST be written in:

{normalized_language}

Do NOT answer in English unless the requested language
is English.

Do NOT return multiple translations.

Do NOT mix languages.

The following fields MUST be translated:

- crop
- possible_condition
- visible_symptoms
- likely_cause
- recommended_next_steps
- summary

The following fields must remain machine-readable:

- confidence
- severity
- image_quality
- expert_needed

============================================================
IMAGE ANALYSIS
============================================================

Analyze the supplied crop or leaf image carefully.

If the image is:

- blurry
- too dark
- too distant
- poorly framed
- not a crop
- not a leaf
- not recognizable

then:

1. Set image_quality to "poor".
2. Set confidence to "low".
3. Set severity to "unknown".
4. Set expert_needed to true.
5. Use the appropriate translated version of
   "Unknown crop".
6. Use the appropriate translated version of
   "Insufficient visual evidence".
7. Do NOT invent symptoms.

============================================================
TASK
============================================================

Return a structured agricultural crop-health screening result.

Remember:

- This is NOT a guaranteed diagnosis.
- Only mention visually observable symptoms.
- Use safe practical recommendations.
- Do not provide pesticide dosage.
- Recommend an agricultural expert when appropriate.

Return ONLY JSON.
"""

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        try:

            logger.info(
                "Calling Gemini Vision. "
                "Attempt %s/%s. language=%s country=%s",
                attempt,
                max_attempts,
                normalized_language,
                country,
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    image_part,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=DIAGNOSIS_SCHEMA,
                ),
            )

            return response

        except errors.ServerError as exc:

            logger.warning(
                "Gemini ServerError attempt %s/%s: %s",
                attempt,
                max_attempts,
                exc,
            )

            if attempt >= max_attempts:
                raise

            wait_seconds = 2 ** (
                attempt - 1
            )

            time.sleep(
                wait_seconds
            )

        except Exception:

            logger.exception(
                "Unexpected Gemini Vision error."
            )

            raise


# ============================================================
# DISEASE DIAGNOSIS
# ============================================================

def diagnose_crop_disease(
    image_bytes: bytes,
    mime_type: str,
    language: str = "English",
    country: str = "India",
) -> dict:

    # --------------------------------------------------------
    # Normalize language
    # --------------------------------------------------------

    language = normalize_language(
        language
    )

    # --------------------------------------------------------
    # Validate Image
    # --------------------------------------------------------

    if not image_bytes:

        return {
            "success": False,
            "message": "No image was provided.",
            "language": language,
        }

    # --------------------------------------------------------
    # Validate MIME
    # --------------------------------------------------------

    if not mime_type:

        return {
            "success": False,
            "message": "Image MIME type is missing.",
            "language": language,
        }

    if not mime_type.startswith("image/"):

        return {
            "success": False,
            "message": (
                "Please upload a valid crop or leaf image."
            ),
            "language": language,
        }

    # --------------------------------------------------------
    # Maximum Image Size
    # --------------------------------------------------------

    max_size = 20 * 1024 * 1024

    if len(image_bytes) > max_size:

        return {
            "success": False,
            "message": (
                "Image is too large. "
                "Please upload an image below 20 MB."
            ),
            "language": language,
        }

    try:

        # ====================================================
        # Gemini Client
        # ====================================================

        client = _get_client()

        logger.info(
            "Gemini client initialized."
        )

        # ====================================================
        # Image Part
        # ====================================================

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        logger.info(
            "Image prepared. mime_type=%s size=%s",
            mime_type,
            len(image_bytes),
        )

        # ====================================================
        # Gemini Vision
        # ====================================================

        response = _generate_diagnosis(
            client=client,
            image_part=image_part,
            language=language,
            country=country,
        )

        # ====================================================
        # Extract Response
        # ====================================================

        raw_text = (
            response.text
            if response is not None
            else ""
        )

        raw_text = (
            raw_text.strip()
            if raw_text
            else ""
        )

        if not raw_text:

            logger.error(
                "Gemini returned empty response."
            )

            return {
                "success": False,
                "message": (
                    "Gemini Vision returned an "
                    "empty response."
                ),
                "language": language,
            }

        logger.info(
            "Gemini Vision response received."
        )

        # ====================================================
        # Parse JSON
        # ====================================================

        try:

            result = json.loads(
                raw_text
            )

            result = validate_diagnosis(
                result,
                language=language,
            )

        except (
            json.JSONDecodeError,
            ValueError,
        ) as exc:

            logger.exception(
                "Invalid Gemini diagnosis JSON: %s",
                exc,
            )

            return {
                "success": False,
                "message": (
                    "Gemini Vision returned an "
                    "unexpected diagnosis response."
                ),
                "language": language,
            }

        # ====================================================
        # Successful Result
        # ====================================================

        logger.info(
            "Diagnosis completed. "
            "crop=%s condition=%s confidence=%s "
            "language=%s",
            result.get("crop"),
            result.get("possible_condition"),
            result.get("confidence"),
            language,
        )

        return {
            "success": True,

            "service": (
                "Gemini Vision Crop Disease Screening"
            ),

            "country": country,

            "language": language,

            "ai": {
                "provider": "Google",
                "model": "Gemini 2.5 Flash",
                "capability": (
                    "Multilingual Crop Image Analysis"
                ),
            },

            "data_sources": {
                "crop_image": True,
                "computer_vision": True,
            },

            "result": result,
        }

    # ========================================================
    # Gemini Server Error
    # ========================================================

    except errors.ServerError as exc:

        logger.exception(
            "Gemini Vision service unavailable: %s",
            exc,
        )

        return {
            "success": False,
            "message": (
                "Gemini Vision is temporarily unavailable. "
                "Please try again in a few seconds."
            ),
            "language": language,
        }

    # ========================================================
    # Gemini API Error
    # ========================================================

    except errors.APIError as exc:

        logger.exception(
            "Gemini API error: %s",
            exc,
        )

        return {
            "success": False,
            "message": (
                "Gemini Vision could not analyze the image. "
                "Please try again."
            ),
            "language": language,
        }

    # ========================================================
    # Configuration Error
    # ========================================================

    except RuntimeError as exc:

        logger.exception(
            "Gemini configuration error: %s",
            exc,
        )

        return {
            "success": False,
            "message": (
                "Gemini API configuration is missing. "
                "Please check GEMINI_API_KEY or "
                "GOOGLE_API_KEY."
            ),
            "language": language,
        }

    # ========================================================
    # Unexpected Error
    # ========================================================

    except Exception as exc:

        logger.exception(
            "Crop disease diagnosis failed: %s",
            exc,
        )

        return {
            "success": False,
            "message": (
                "Crop image analysis is temporarily "
                "unavailable."
            ),
            "language": language,
        }