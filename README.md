AgriNet AI is an interoperable digital agriculture platform inspired by the BRICS AgriN initiative, designed to empower small and marginal farmers with real-time, localized, data-driven agricultural intelligence.

The platform combines Google Gemini/Vertex AI, satellite data, soil health analytics, weather forecasting, and AI-based crop disease detection to provide actionable recommendations for sustainable and regenerative farming.

It is designed as a scalable Digital Public Good (DPG), enabling agricultural data, AI models, and advisory frameworks to be adapted across countries, languages, crops, and climatic conditions.

Key capabilities:

🌱 AI-powered regenerative crop recommendations
🛰️ Satellite-based crop and field intelligence
🌍 Soil health and farm-condition analysis
🌦️ Real-time weather and climate-risk intelligence
🍃 AI-based crop disease detection
📈 Localized agricultural advisories
🗣️ Multilingual and voice-enabled farmer assistance
🌐 Cross-border interoperability for BRICS nations

#This is prototype/demo satellite intelligence as representative Sentinel-2/NDVI data used to demonstrate the interoperable architecture.

#Later, if time permits, we can replace this layer with Google Earth Engine data.
# AgriNet AI Frontend

Simple voice-enabled frontend for the AgriNet AI
BRICS Digital Agriculture Intelligence Network.

## Requirements

- Node.js 18+
- Backend FastAPI running on port 8000
- Google Chrome or Microsoft Edge for voice input

## Start backend
fastapi
uvicorn
google-genai
python-dotenv
requests
pydantic

From backend:

```bash
uvicorn main:app --reload


## How AgriNet Works?
                    ┌─────────────────────────┐
                    │       Farmer/User       │
                    │  Voice / Web Interface  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      AgriNet AI         │
                    │    Advisory Engine      │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌────────────┐     ┌────────────┐     ┌────────────┐
       │  Satellite │     │    Soil    │     │  Weather   │
       │    Data     │     │   Health   │     │ Forecast   │
       └──────┬─────┘     └──────┬─────┘     └──────┬─────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Google Gemini / Vertex  │
                    │       AI Reasoning      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Localized Agro-Advisory │
                    │ Crop / Soil / Weather   │
                    │ Disease / Regenerative  │
                    └─────────────────────────┘
AgriNet AI is designed to promote sustainable and regenerative farming practices.

Recommendations can consider:

Soil health improvement
Crop rotation
Water conservation
Reduced resource dependency
Climate resilience
Sustainable crop selection
Soil-friendly farming practices

The objective is not only to maximize short-term yield but also to support long-term soil and ecosystem health.

Crop Disease Detection

The platform includes an AI-based crop disease diagnostic capability.

A farmer can provide a crop/leaf image, which can be analyzed by the AI pipeline to identify potential disease symptoms and provide appropriate next steps.

