"use client";

import {
  useCallback,
  useEffect,
  useState,
  ChangeEvent,
} from "react";

import VoiceAssistant from "../components/VoiceAssistant";
import IntelligenceCards from "../components/IntelligenceCards";
import AdvisoryPanel from "../components/AdvisoryPanel";

import {
  generateAdvisory,
  diagnoseCropDisease,
  AgricultureRequest,
  AdvisoryResponse,
  DiseaseDiagnosis,
} from "../lib/api";

// ============================================================
// FARMER DEMO DATA
// ============================================================

const FARMERS: Record<string, AgricultureRequest> = {
  farmer001: {
    country_code: "IN",
    region: "Jaipur",
    farmer_id: "farmer001",
    crop: "Wheat",
    soil: {
      ph: 7.8,
      nitrogen: "Low",
      phosphorus: "Medium",
      potassium: "High",
      organic_carbon: "Low",
      moisture: 32,
    },
    weather: {
      temperature: 32,
      rain_probability: 94,
      rainfall: 15.9,
    },
    satellite: {
      ndvi: 0.62,
      vegetation_health: "Moderate",
      vegetation_trend: "Declining",
    },
    language: "Hindi",
  },

  farmer002: {
    country_code: "BR",
    region: "Mato Grosso",
    farmer_id: "farmer002",
    crop: "Soybean",
    soil: {
      ph: 6.4,
      nitrogen: "Medium",
      phosphorus: "Medium",
      potassium: "Medium",
      organic_carbon: "Medium",
      moisture: 48,
    },
    weather: {
      temperature: 28,
      rain_probability: 72,
      rainfall: 18.4,
    },
    satellite: {
      ndvi: 0.74,
      vegetation_health: "Good",
      vegetation_trend: "Stable",
    },
    language: "Portuguese",
  },

  farmer003: {
    country_code: "RU",
    region: "Krasnodar",
    farmer_id: "farmer003",
    crop: "Wheat",
    soil: {
      ph: 6.8,
      nitrogen: "Medium",
      phosphorus: "High",
      potassium: "Medium",
      organic_carbon: "Medium",
      moisture: 44,
    },
    weather: {
      temperature: 24,
      rain_probability: 48,
      rainfall: 6.2,
    },
    satellite: {
      ndvi: 0.68,
      vegetation_health: "Good",
      vegetation_trend: "Stable",
    },
    language: "Russian",
  },

  farmer004: {
    country_code: "CN",
    region: "Heilongjiang",
    farmer_id: "farmer004",
    crop: "Rice",
    soil: {
      ph: 6.2,
      nitrogen: "Medium",
      phosphorus: "Medium",
      potassium: "Medium",
      organic_carbon: "High",
      moisture: 61,
    },
    weather: {
      temperature: 23,
      rain_probability: 66,
      rainfall: 12.8,
    },
    satellite: {
      ndvi: 0.71,
      vegetation_health: "Good",
      vegetation_trend: "Improving",
    },
    language: "Chinese",
  },

  farmer005: {
    country_code: "ZA",
    region: "Free State",
    farmer_id: "farmer005",
    crop: "Maize",
    soil: {
      ph: 6.5,
      nitrogen: "Low",
      phosphorus: "Medium",
      potassium: "Medium",
      organic_carbon: "Low",
      moisture: 29,
    },
    weather: {
      temperature: 19,
      rain_probability: 35,
      rainfall: 3.4,
    },
    satellite: {
      ndvi: 0.55,
      vegetation_health: "Moderate",
      vegetation_trend: "Declining",
    },
    language: "English",
  },
};

// ============================================================
// LANGUAGE TEXT
// ============================================================

const LANGUAGE_TEXT: Record<
  string,
  {
    uploadTitle: string;
    uploadDescription: string;
    uploadHint: string;
    analyze: string;
    analyzing: string;
    resultLabel: string;
    resultTitle: string;
    analyzed: string;
    possibleCondition: string;
    confidence: string;
    crop: string;
    severity: string;
    imageQuality: string;
    observations: string;
    likelyCause: string;
    recommendations: string;
    expertNeeded: string;
    summary: string;
    safety: string;
    uploadError: string;
    imageError: string;
    imageSizeError: string;
  }
> = {
  English: {
    uploadTitle: "Upload a crop or leaf image",

    uploadDescription:
      "AgriNet AI uses Google Gemini Vision to screen the image for visible crop-health symptoms.",

    uploadHint:
      "JPG, PNG, WEBP • Maximum 20 MB",

    analyze: "🔬 Analyze Crop Health",

    analyzing: "Gemini is analyzing...",

    resultLabel: "GEMINI VISION RESULT",

    resultTitle: "Crop Health Screening",

    analyzed: "✓ Analysis Complete",

    possibleCondition: "POSSIBLE CONDITION",

    confidence: "Confidence",

    crop: "Crop",

    severity: "Severity",

    imageQuality: "Image Quality",

    observations: "🔎 Visible Symptoms",

    likelyCause: "🔍 Possible Cause",

    recommendations: "🌱 Recommended Actions",

    expertNeeded: "🧑‍🌾 Agricultural Expert",

    summary: "Summary",

    safety:
      "⚠️ AI image analysis is a screening aid. It does not confirm a disease with certainty. For serious crop damage or low-confidence results, consult a qualified agricultural expert.",

    uploadError:
      "Please select a valid crop or leaf image.",

    imageError:
      "Please upload a crop or leaf image first.",

    imageSizeError:
      "Image is too large. Please upload an image below 20 MB.",
  },

  Hindi: {
    uploadTitle:
      "फसल या पत्ते की तस्वीर अपलोड करें",

    uploadDescription:
      "AgriNet AI Google Gemini Vision का उपयोग करके तस्वीर में दिखाई देने वाले फसल स्वास्थ्य संबंधी लक्षणों की स्क्रीनिंग करता है।",

    uploadHint:
      "JPG, PNG, WEBP • अधिकतम 20 MB",

    analyze:
      "🔬 फसल के स्वास्थ्य का विश्लेषण करें",

    analyzing:
      "Gemini विश्लेषण कर रहा है...",

    resultLabel:
      "GEMINI VISION परिणाम",

    resultTitle:
      "फसल स्वास्थ्य स्क्रीनिंग",

    analyzed:
      "✓ विश्लेषण पूरा हुआ",

    possibleCondition:
      "संभावित स्थिति",

    confidence:
      "विश्वसनीयता",

    crop:
      "फसल",

    severity:
      "गंभीरता",

    imageQuality:
      "तस्वीर की गुणवत्ता",

    observations:
      "🔎 दिखाई देने वाले लक्षण",

    likelyCause:
      "🔍 संभावित कारण",

    recommendations:
      "🌱 सुझाए गए कदम",

    expertNeeded:
      "🧑‍🌾 कृषि विशेषज्ञ",

    summary:
      "सारांश",

    safety:
      "⚠️ AI द्वारा किया गया छवि विश्लेषण केवल स्क्रीनिंग और सलाह के लिए है। यह किसी बीमारी की निश्चित पुष्टि नहीं करता। गंभीर क्षति या कम विश्वसनीयता होने पर कृषि विशेषज्ञ से सलाह लें।",

    uploadError:
      "कृपया फसल या पत्ते की सही तस्वीर चुनें।",

    imageError:
      "कृपया पहले फसल या पत्ते की तस्वीर अपलोड करें।",

    imageSizeError:
      "तस्वीर बहुत बड़ी है। कृपया 20 MB से कम की तस्वीर अपलोड करें।",
  },

  Portuguese: {
    uploadTitle:
      "Envie uma imagem da cultura ou folha",

    uploadDescription:
      "O AgriNet AI usa o Google Gemini Vision para fazer uma triagem dos sintomas visíveis na cultura.",

    uploadHint:
      "JPG, PNG, WEBP • Máximo de 20 MB",

    analyze:
      "🔬 Analisar a Saúde da Cultura",

    analyzing:
      "Gemini está analisando...",

    resultLabel:
      "RESULTADO DO GEMINI VISION",

    resultTitle:
      "Triagem da Saúde da Cultura",

    analyzed:
      "✓ Análise concluída",

    possibleCondition:
      "POSSÍVEL CONDIÇÃO",

    confidence:
      "Confiança",

    crop:
      "Cultura",

    severity:
      "Gravidade",

    imageQuality:
      "Qualidade da Imagem",

    observations:
      "🔎 Sintomas Visíveis",

    likelyCause:
      "🔍 Possível Causa",

    recommendations:
      "🌱 Ações Recomendadas",

    expertNeeded:
      "🧑‍🌾 Especialista Agrícola",

    summary:
      "Resumo",

    safety:
      "⚠️ A análise de imagem por IA é apenas uma triagem. Ela não confirma uma doença com certeza. Em caso de danos graves ou baixa confiança, consulte um especialista agrícola qualificado.",

    uploadError:
      "Selecione uma imagem válida da cultura ou folha.",

    imageError:
      "Envie primeiro uma imagem da cultura ou folha.",

    imageSizeError:
      "A imagem é muito grande. Envie uma imagem com menos de 20 MB.",
  },

  Russian: {
    uploadTitle:
      "Загрузите изображение культуры или листа",

    uploadDescription:
      "AgriNet AI использует Google Gemini Vision для скрининга видимых симптомов состояния культуры.",

    uploadHint:
      "JPG, PNG, WEBP • Максимум 20 МБ",

    analyze:
      "🔬 Анализ состояния культуры",

    analyzing:
      "Gemini выполняет анализ...",

    resultLabel:
      "РЕЗУЛЬТАТ GEMINI VISION",

    resultTitle:
      "Скрининг состояния культуры",

    analyzed:
      "✓ Анализ завершён",

    possibleCondition:
      "ВОЗМОЖНОЕ СОСТОЯНИЕ",

    confidence:
      "Уверенность",

    crop:
      "Культура",

    severity:
      "Степень тяжести",

    imageQuality:
      "Качество изображения",

    observations:
      "🔎 Видимые симптомы",

    likelyCause:
      "🔍 Возможная причина",

    recommendations:
      "🌱 Рекомендуемые действия",

    expertNeeded:
      "🧑‍🌾 Агрономический специалист",

    summary:
      "Резюме",

    safety:
      "⚠️ Анализ изображения с помощью ИИ является только скринингом. Он не подтверждает заболевание с полной уверенностью. При серьёзном повреждении или низкой уверенности обратитесь к квалифицированному специалисту.",

    uploadError:
      "Выберите корректное изображение культуры или листа.",

    imageError:
      "Сначала загрузите изображение культуры или листа.",

    imageSizeError:
      "Изображение слишком большое. Загрузите изображение размером менее 20 МБ.",
  },

  Chinese: {
    uploadTitle:
      "上传作物或叶片图片",

    uploadDescription:
      "AgriNet AI 使用 Google Gemini Vision 对图片中的可见作物健康症状进行筛查。",

    uploadHint:
      "JPG、PNG、WEBP • 最大 20 MB",

    analyze:
      "🔬 分析作物健康状况",

    analyzing:
      "Gemini 正在分析...",

    resultLabel:
      "GEMINI VISION 分析结果",

    resultTitle:
      "作物健康筛查",

    analyzed:
      "✓ 分析完成",

    possibleCondition:
      "可能的状况",

    confidence:
      "置信度",

    crop:
      "作物",

    severity:
      "严重程度",

    imageQuality:
      "图片质量",

    observations:
      "🔎 可见症状",

    likelyCause:
      "🔍 可能原因",

    recommendations:
      "🌱 建议措施",

    expertNeeded:
      "🧑‍🌾 农业专家",

    summary:
      "摘要",

    safety:
      "⚠️ AI 图像分析仅用于筛查和提供建议，不能确定诊断疾病。如果作物出现严重损害或置信度较低，请咨询合格的农业专家。",

    uploadError:
      "请选择有效的作物或叶片图片。",

    imageError:
      "请先上传作物或叶片图片。",

    imageSizeError:
      "图片太大。请上传小于 20 MB 的图片。",
  },
};

// ============================================================
// HOME
// ============================================================

export default function Home() {
  // ==========================================================
  // ADVISORY STATE
  // ==========================================================

  const [farmerId, setFarmerId] =
    useState("farmer001");

  const [request, setRequest] =
    useState<AgricultureRequest>(
      FARMERS.farmer001
    );

  const [result, setResult] =
    useState<AdvisoryResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [transcript, setTranscript] =
    useState("");

  const [error, setError] =
    useState("");

  const [speaking, setSpeaking] =
    useState(false);

  // ==========================================================
  // DISEASE DIAGNOSIS STATE
  // ==========================================================

  const [selectedImage, setSelectedImage] =
    useState<File | null>(null);

  const [imagePreview, setImagePreview] =
    useState<string | null>(null);

  const [diagnosisLoading, setDiagnosisLoading] =
    useState(false);

  const [diagnosisResult, setDiagnosisResult] =
    useState<DiseaseDiagnosis | null>(null);

  const [diagnosisError, setDiagnosisError] =
    useState("");

  // ==========================================================
  // CURRENT LANGUAGE TEXT
  // ==========================================================

  const languageText =
    LANGUAGE_TEXT[request.language] ||
    LANGUAGE_TEXT.English;

  // ==========================================================
  // CLEAN IMAGE PREVIEW URL
  // ==========================================================

  useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  // ==========================================================
  // FARMER SELECTION
  // ==========================================================

  const selectFarmer = (id: string) => {
    const farmer = FARMERS[id];

    if (!farmer) {
      return;
    }

    setFarmerId(id);
    setRequest(farmer);
    setResult(null);
    setTranscript("");
    setError("");

    // Clear old diagnosis
    setSelectedImage(null);
    setImagePreview(null);
    setDiagnosisResult(null);
    setDiagnosisError("");
  };

  // ==========================================================
  // GENERATE AGRICULTURAL ADVISORY
  // ==========================================================

  const generate = useCallback(
    async (
      customRequest?: AgricultureRequest
    ) => {
      setLoading(true);
      setError("");

      try {
        const data =
          await generateAdvisory(
            customRequest || request
          );

        setResult(data);
      } catch (err: any) {
        setError(
          err?.message ||
            "Unable to generate advisory."
        );
      } finally {
        setLoading(false);
      }
    },
    [request]
  );

  // ==========================================================
  // VOICE TRANSCRIPT
  // ==========================================================

  const handleTranscript =
    useCallback(
      (text: string) => {
        setTranscript(text);

        setTimeout(() => {
          generate(request);
        }, 300);
      },
      [generate, request]
    );

  // ==========================================================
  // SPEAK ADVISORY
  // ==========================================================

  const speakAdvisory = () => {
    if (!result?.ai_advisory) {
      return;
    }

    if (
      typeof window === "undefined" ||
      !window.speechSynthesis
    ) {
      return;
    }

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    const advisory =
      result.ai_advisory;

    const text = [
      advisory.crop_condition,
      advisory.weather_risk,
      advisory.soil_health,
      advisory.irrigation_recommendation,
      advisory.summary,
    ].join(". ");

    const utterance =
      new SpeechSynthesisUtterance(text);

    switch (request.language) {
      case "Hindi":
        utterance.lang = "hi-IN";
        break;

      case "Portuguese":
        utterance.lang = "pt-BR";
        break;

      case "Russian":
        utterance.lang = "ru-RU";
        break;

      case "Chinese":
        utterance.lang = "zh-CN";
        break;

      default:
        utterance.lang = "en-IN";
    }

    utterance.rate = 0.9;

    utterance.onend = () => {
      setSpeaking(false);
    };

    utterance.onerror = () => {
      setSpeaking(false);
    };

    window.speechSynthesis.speak(
      utterance
    );

    setSpeaking(true);
  };

  // ==========================================================
  // IMAGE SELECT
  // ==========================================================

  const handleImageSelect = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    // Validate image
    if (!file.type.startsWith("image/")) {
      setDiagnosisError(
        languageText.uploadError
      );

      setSelectedImage(null);
      setImagePreview(null);

      return;
    }

    // 20 MB limit
    const maxSize =
      20 * 1024 * 1024;

    if (file.size > maxSize) {
      setDiagnosisError(
        languageText.imageSizeError
      );

      setSelectedImage(null);
      setImagePreview(null);

      return;
    }

    setDiagnosisError("");
    setDiagnosisResult(null);

    // Revoke previous preview
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setSelectedImage(file);

    const previewUrl =
      URL.createObjectURL(file);

    setImagePreview(previewUrl);
  };

  // ==========================================================
// DIAGNOSE CROP DISEASE
// ==========================================================

const handleDiagnosis = async () => {
  if (!selectedImage) {
    setDiagnosisError(
      languageText.imageError
    );
    return;
  }

  setDiagnosisLoading(true);
  setDiagnosisError("");
  setDiagnosisResult(null);

  try {
    // ========================================================
    // diagnoseCropDisease() now returns DiseaseDiagnosis
    // directly.
    //
    // No need for:
    // response.result
    // response.diagnosis
    // response
    //
    // This fixes the TypeScript union error.
    // ========================================================

    const diagnosis =
      await diagnoseCropDisease(
        selectedImage,
        request.language,
        request.country_code
      );

    setDiagnosisResult(diagnosis);
  } catch (err: any) {
    setDiagnosisError(
      err?.message ||
        languageText.imageError
    );
  } finally {
    setDiagnosisLoading(false);
  }
};

  // ==========================================================
  // CURRENT FARMER
  // ==========================================================

  const currentFarmer =
    FARMERS[farmerId];

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <main className="page">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="header">

        <div className="brand">

          <div className="logo">
            🌾
          </div>

          <div>
            <h1>
              AgriNet AI
            </h1>

            <p>
              BRICS Digital Agriculture
              Intelligence Network
            </p>
          </div>

        </div>

        <div className="header-badge">
          Google Gemini
        </div>

      </header>

      {/* ======================================================
          HERO
          ====================================================== */}

      <section className="hero">

        <div className="hero-content">

          <div className="hero-label">
            🌍 CROSS-BORDER AGRICULTURE
          </div>

          <h2>
            Talk to your
            <br />
            <span>
              Agricultural Intelligence
            </span>
          </h2>

          <p>
            Ask about your crop, soil,
            weather or field condition.
            AgriNet combines agricultural
            data with Google Gemini to
            generate localized advice.
          </p>

          <VoiceAssistant
            language={request.language}
            onTranscript={
              handleTranscript
            }
          />

          {transcript && (
            <div className="transcript">

              <div className="transcript-label">
                YOU SAID
              </div>

              <div className="transcript-text">
                “{transcript}”
              </div>

            </div>
          )}

        </div>

        <div className="hero-visual">

          <div className="orbit orbit-one">
            🧪
          </div>

          <div className="orbit orbit-two">
            🌦️
          </div>

          <div className="orbit orbit-three">
            🛰️
          </div>

          <div className="earth">
            🌍
          </div>

          <div className="ai-core">
            AI
          </div>

        </div>

      </section>

      {/* ======================================================
          FARMER SELECTOR
          ====================================================== */}

      <section className="control-panel">

        <div className="control-title">
          👨‍🌾 Farmer Context
        </div>

        <div className="controls">

          <div className="field">

            <label>
              Farmer
            </label>

            <select
              value={farmerId}
              onChange={(event) =>
                selectFarmer(
                  event.target.value
                )
              }
            >

              <option value="farmer001">
                🇮🇳 farmer001 — Jaipur
              </option>

              <option value="farmer002">
                🇧🇷 farmer002 — Mato Grosso
              </option>

              <option value="farmer003">
                🇷🇺 farmer003 — Krasnodar
              </option>

              <option value="farmer004">
                🇨🇳 farmer004 — Heilongjiang
              </option>

              <option value="farmer005">
                🇿🇦 farmer005 — Free State
              </option>

            </select>

          </div>

          <div className="context-item">
            <span>
              Country
            </span>

            <strong>
              {currentFarmer.country_code}
            </strong>
          </div>

          <div className="context-item">
            <span>
              Region
            </span>

            <strong>
              {currentFarmer.region}
            </strong>
          </div>

          <div className="context-item">
            <span>
              Crop
            </span>

            <strong>
              {currentFarmer.crop}
            </strong>
          </div>

          <div className="context-item">
            <span>
              Language
            </span>

            <strong>
              {currentFarmer.language}
            </strong>
          </div>

        </div>

      </section>

      {/* ======================================================
          LOADING
          ====================================================== */}

      {loading && (
        <div className="loading-card">

          <div className="spinner" />

          <div>
            <strong>
              AgriNet AI is analyzing...
            </strong>

            <p>
              Combining soil + weather +
              satellite intelligence with
              Google Gemini.
            </p>
          </div>

        </div>
      )}

      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && (
        <div className="error-card">
          ⚠️ {error}
        </div>
      )}

      {/* ======================================================
          INTELLIGENCE CARDS
          ====================================================== */}

      <section className="section">

        <div className="section-heading">

          <div>

            <span>
              DATA SOURCES
            </span>

            <h2>
              Agricultural Intelligence
            </h2>

          </div>

          <div className="source-status">
            ● Connected
          </div>

        </div>

        <IntelligenceCards
          data={currentFarmer}
        />

      </section>

      {/* ======================================================
          GENERATE ADVISORY
          ====================================================== */}

      {!loading && (
        <div className="generate-container">

          <button
            className="generate-button"
            onClick={() =>
              generate()
            }
          >
            🧠 Generate AI Advisory
          </button>

        </div>
      )}

      {/* ======================================================
          ADVISORY RESULT
          ====================================================== */}

      {result && (
        <section className="section">

          <AdvisoryPanel
            advisory={
              result.ai_advisory
            }
            onSpeak={
              speakAdvisory
            }
            speaking={
              speaking
            }
          />

        </section>
      )}

      {/* ======================================================
          GEMINI VISION
          ====================================================== */}

      <section className="section disease-section">

        <div className="section-heading">

          <div>

            <span>
              GEMINI VISION
            </span>

            <h2>
              🌿 Crop Disease Screening
            </h2>

          </div>

          <div className="source-status">
            ● AI Vision Ready
          </div>

        </div>

        <div className="disease-card">

          {/* ==================================================
              INTRO
              ================================================== */}

          <div className="disease-intro">

            <div className="disease-icon">
              📷
            </div>

            <div>

              <h3>
                {languageText.uploadTitle}
              </h3>

              <p>
                {languageText.uploadDescription}
              </p>

              <small>
                {languageText.uploadHint}
              </small>

            </div>

          </div>

          {/* ==================================================
              UPLOAD AREA
              ================================================== */}

          <label
            htmlFor="crop-image-upload"
            className="upload-area"
          >

            {imagePreview ? (

              <div className="image-preview-container">

                <img
                  src={imagePreview}
                  alt="Selected crop"
                  className="crop-preview"
                />

                <div className="change-image-text">
                  Click to change image
                </div>

              </div>

            ) : (

              <div className="upload-placeholder">

                <div className="upload-icon">
                  📤
                </div>

                <strong>
                  {languageText.uploadTitle}
                </strong>

                <span>
                  Click here to select an image
                </span>

                <span className="upload-hint">
                  {languageText.uploadHint}
                </span>

              </div>

            )}

          </label>

          <input
            id="crop-image-upload"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={
              handleImageSelect
            }
            style={{
              display: "none",
            }}
          />

          {/* ==================================================
              SELECTED IMAGE
              ================================================== */}

          {selectedImage && (

            <div className="selected-file">

              <span>
                📎 {selectedImage.name}
              </span>

              <span>
                {(
                  selectedImage.size /
                  1024 /
                  1024
                ).toFixed(2)}{" "}
                MB
              </span>

            </div>

          )}

          {/* ==================================================
              ERROR
              ================================================== */}

          {diagnosisError && (

            <div className="error-card">
              ⚠️ {diagnosisError}
            </div>

          )}

          {/* ==================================================
              BUTTON
              ================================================== */}

          <div className="diagnosis-button-container">

            <button
              className="diagnose-button"
              onClick={
                handleDiagnosis
              }
              disabled={
                !selectedImage ||
                diagnosisLoading
              }
            >

              {diagnosisLoading ? (

                <>
                  <span className="button-spinner" />

                  {languageText.analyzing}
                </>

              ) : (

                languageText.analyze

              )}

            </button>

          </div>

          {/* ==================================================
              DIAGNOSIS RESULT
              ================================================== */}

          {diagnosisResult && (

            <div className="diagnosis-result">

              {/* RESULT HEADER */}

              <div className="diagnosis-result-header">

                <div>

                  <span>
                    {languageText.resultLabel}
                  </span>

                  <h3>
                    {languageText.resultTitle}
                  </h3>

                </div>

                <div className="diagnosis-status">
                  {languageText.analyzed}
                </div>

              </div>

              {/* ==================================================
                  CROP
                  ================================================== */}

              <div className="diagnosis-info">

                <span>
                  {languageText.crop}
                </span>

                <strong>
                  {diagnosisResult.crop ||
                    "Unknown crop"}
                </strong>

              </div>

              {/* ==================================================
                  POSSIBLE CONDITION
                  ================================================== */}

              <div className="diagnosis-main">

                <div className="diagnosis-label">
                  {languageText.possibleCondition}
                </div>

                <div className="diagnosis-value">

                  {diagnosisResult.possible_condition ||
                    "Insufficient visual evidence"}

                </div>

              </div>

              {/* ==================================================
                  CONFIDENCE
                  ================================================== */}

              <div className="diagnosis-info">

                <span>
                  {languageText.confidence}
                </span>

                <strong>
                  {diagnosisResult.confidence ||
                    "low"}
                </strong>

              </div>

              {/* ==================================================
                  SEVERITY
                  ================================================== */}

              <div className="diagnosis-info">

                <span>
                  {languageText.severity}
                </span>

                <strong>
                  {diagnosisResult.severity ||
                    "unknown"}
                </strong>

              </div>

              {/* ==================================================
                  IMAGE QUALITY
                  ================================================== */}

              <div className="diagnosis-info">

                <span>
                  {languageText.imageQuality}
                </span>

                <strong>
                  {diagnosisResult.image_quality ||
                    "poor"}
                </strong>

              </div>

              {/* ==================================================
                  VISIBLE SYMPTOMS
                  ================================================== */}

              {Array.isArray(
                diagnosisResult.visible_symptoms
              ) &&
                diagnosisResult.visible_symptoms
                  .length > 0 && (

                  <div className="diagnosis-list">

                    <h4>
                      {languageText.observations}
                    </h4>

                    <ul>

                      {diagnosisResult.visible_symptoms.map(
                        (
                          symptom,
                          index
                        ) => (

                          <li
                            key={index}
                          >
                            {symptom}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}

              {/* ==================================================
                  LIKELY CAUSE
                  ================================================== */}

              {diagnosisResult.likely_cause && (

                <div className="diagnosis-list">

                  <h4>
                    {languageText.likelyCause}
                  </h4>

                  <p>
                    {diagnosisResult.likely_cause}
                  </p>

                </div>

              )}

              {/* ==================================================
                  RECOMMENDED NEXT STEPS
                  ================================================== */}

              {Array.isArray(
                diagnosisResult.recommended_next_steps
              ) &&
                diagnosisResult
                  .recommended_next_steps
                  .length > 0 && (

                  <div className="diagnosis-list">

                    <h4>
                      {languageText.recommendations}
                    </h4>

                    <ul>

                      {diagnosisResult.recommended_next_steps.map(
                        (
                          step,
                          index
                        ) => (

                          <li
                            key={index}
                          >
                            {step}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}

              {/* ==================================================
                  EXPERT NEEDED
                  ================================================== */}

              <div className="diagnosis-info">

                <span>
                  {languageText.expertNeeded}
                </span>

                <strong>

                  {diagnosisResult.expert_needed
                    ? "YES"
                    : "NO"}

                </strong>

              </div>

              {/* ==================================================
                  SUMMARY
                  ================================================== */}

              {diagnosisResult.summary && (

                <div className="diagnosis-list">

                  <h4>
                    {languageText.summary}
                  </h4>

                  <p>
                    {diagnosisResult.summary}
                  </p>

                </div>

              )}

              {/* ==================================================
                  HINDI SUMMARY
                  ================================================== */}

              {request.language === "Hindi" &&
                diagnosisResult.summary_hindi && (

                  <div className="diagnosis-list">

                    <h4>
                      हिंदी सारांश
                    </h4>

                    <p>
                      {
                        diagnosisResult.summary_hindi
                      }
                    </p>

                  </div>

                )}

              {/* ==================================================
                  SAFETY
                  ================================================== */}

              <div className="diagnosis-warning">

                {languageText.safety}

              </div>

            </div>

          )}

        </div>

      </section>

      {/* ======================================================
          FOOTER
          ====================================================== */}

      <footer>

        <div>
          🌾 AgriNet AI
        </div>

        <div>
          BRICS Digital Agriculture
          Intelligence Network
        </div>

        <div>
          Powered by Google Gemini
        </div>

      </footer>

    </main>
  );
}
