// ============================================================
// API CONFIGURATION
// ============================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

// ============================================================
// AGRICULTURE TYPES
// ============================================================

export interface SoilData {
  ph: number;
  nitrogen: string;
  phosphorus: string;
  potassium: string;
  organic_carbon: string;
  moisture: number;
}

export interface WeatherData {
  temperature: number;
  rain_probability: number;
  rainfall: number;
}

export interface SatelliteData {
  ndvi: number;
  vegetation_health: string;
  vegetation_trend: string;
}

export interface AgricultureRequest {
  country_code: string;
  region: string;
  farmer_id: string;
  crop: string;
  soil: SoilData;
  weather: WeatherData;
  satellite: SatelliteData;
  language: string;
}

// ============================================================
// AI ADVISORY TYPES
// ============================================================

export interface Advisory {
  crop_condition: string;
  weather_risk: string;
  soil_health: string;
  vegetation_health: string;
  irrigation_recommendation: string;
  regenerative_farming: string[];
  immediate_actions: string[];
  overall_risk: "low" | "medium" | "high";
  data_driven_reasoning: string;
  summary: string;
  error?: string;
}

// ============================================================
// ADVISORY RESPONSE
// ============================================================

export interface AdvisoryResponse {
  success: boolean;
  network: string;
  service?: string;
  country: string;
  country_code: string;
  region: string;
  farmer_id: string;
  crop: string;
  language: string;

  data_sources: {
    farmer_context?: boolean;
    soil: boolean;
    weather: boolean;
    satellite: boolean;
    ai_engine?: string;
  };

  ai?: {
    provider: string;
    model: string;
    capability: string;
  };

  interoperability?: {
    standard_api: string;
    country_code: string;
    localized_language: string;
    cross_border_ready: boolean;
  };

  agricultural_data?: {
    country: string;
    country_code: string;
    region: string;
    farmer_id: string;
    crop: string;
    language: string;
    soil: SoilData;
    weather: WeatherData;
    satellite: SatelliteData;
  };

  soil?: SoilData;
  weather?: WeatherData;
  satellite?: SatelliteData;

  ai_advisory: Advisory;

  regenerative_agriculture?: {
    enabled: boolean;
    description: string;
  };
}

// ============================================================
// DISEASE DIAGNOSIS
//
// MUST MATCH backend/src/tools/disease_diagnosis.py
// ============================================================

export interface DiseaseDiagnosis {
  // Identified crop
  crop: string;

  // Most likely visible condition
  possible_condition: string;

  // low | medium | high
  confidence: "low" | "medium" | "high";

  // low | moderate | high | unknown
  severity: "low" | "moderate" | "high" | "unknown";

  // good | acceptable | poor
  image_quality: "good" | "acceptable" | "poor";

  // Symptoms actually visible in image
  visible_symptoms: string[];

  // Possible cause
  likely_cause: string;

  // Safe recommended actions
  recommended_next_steps: string[];

  // Whether agricultural expert should be consulted
  expert_needed: boolean;

  // Farmer-facing summary
  summary: string;

  // Hindi summary
  summary_hindi: string;
}

// ============================================================
// DISEASE DIAGNOSIS RESPONSE
//
// Backend response:
//
// {
//   success: true,
//   service: "...",
//   country: "IN",
//   language: "Hindi",
//   result: {
//     crop: "...",
//     possible_condition: "...",
//     confidence: "...",
//     severity: "...",
//     image_quality: "...",
//     visible_symptoms: [],
//     likely_cause: "...",
//     recommended_next_steps: [],
//     expert_needed: false,
//     summary: "...",
//     summary_hindi: "..."
//   }
// }
// ============================================================

export interface DiseaseDiagnosisResponse {
  success: boolean;
  service?: string;
  country?: string;
  language?: string;
  result?: DiseaseDiagnosis;
  message?: string;
}

// ============================================================
// GENERATE AGRICULTURAL ADVISORY
// ============================================================

export async function generateAdvisory(
  request: AgricultureRequest
): Promise<AdvisoryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/agriculture/advisory`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  let data: any;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Backend returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        "Unable to generate agricultural advisory."
    );
  }

  return data as AdvisoryResponse;
}

// ============================================================
// CROP DISEASE DIAGNOSIS
//
// Sends:
//   1. crop image
//   2. farmer language
//   3. farmer country
//
// Backend:
// POST /api/v1/agriculture/disease-diagnosis
//
// IMPORTANT:
// Do NOT manually set Content-Type.
// Browser automatically creates:
//
// multipart/form-data; boundary=...
//
// IMPORTANT FIX:
// This function now returns ONLY DiseaseDiagnosis.
//
// This keeps page.tsx state strongly typed:
// DiseaseDiagnosis | null
// ============================================================

export async function diagnoseCropDisease(
  image: File,
  language: string,
  country: string = "India"
): Promise<DiseaseDiagnosis> {
  const formData = new FormData();

  // Crop / leaf image
  formData.append("image", image);

  // Farmer language
  formData.append("language", language);

  // Farmer country
  formData.append("country", country);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/agriculture/disease-diagnosis`,
    {
      method: "POST",

      // DO NOT ADD:
      // "Content-Type": "multipart/form-data"
      //
      // Browser must create the boundary automatically.

      body: formData,
    }
  );

  let data: DiseaseDiagnosisResponse;

  try {
    data =
      (await response.json()) as DiseaseDiagnosisResponse;
  } catch {
    throw new Error(
      "Backend returned an invalid diagnosis response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.message ||
        "Crop disease diagnosis failed."
    );
  }

  // ==========================================================
  // IMPORTANT:
  // Backend returns:
  //
  // {
  //   success: true,
  //   result: {
  //     crop: "...",
  //     possible_condition: "...",
  //     ...
  //   }
  // }
  //
  // React state expects DiseaseDiagnosis, NOT the wrapper.
  // ==========================================================

  if (!data.result) {
    throw new Error(
      data?.message ||
        "Disease diagnosis result was not returned by the backend."
    );
  }

  return data.result;
}

// ============================================================
// GET BRICS COUNTRIES
// ============================================================

export async function getBricsCountries() {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/brics/countries`
  );

  let data: any;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Backend returned an invalid country response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        "Unable to retrieve BRICS countries."
    );
  }

  return data;
}

// ============================================================
// GET SINGLE BRICS COUNTRY
// ============================================================

export async function getBricsCountry(
  countryCode: string
) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/brics/country/${countryCode.toUpperCase()}`
  );

  let data: any;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Backend returned an invalid country response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        "Unable to retrieve country information."
    );
  }

  return data;
}
