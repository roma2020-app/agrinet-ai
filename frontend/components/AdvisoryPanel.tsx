"use client";

interface AdvisoryPanelProps {
  advisory: any;
  onSpeak: () => void;
  speaking: boolean;
}

export default function AdvisoryPanel({
  advisory,
  onSpeak,
  speaking,
}: AdvisoryPanelProps) {
  if (!advisory) {
    return null;
  }

  const risk =
    advisory.overall_risk || "medium";

  return (
    <div className="advisory-section">

      <div className="advisory-header">
        <div>
          <div className="section-label">
            GOOGLE GEMINI
          </div>

          <h2>
            🤖 AI Agricultural Advisory
          </h2>
        </div>

        <button
          className="speak-button"
          onClick={onSpeak}
        >
          {speaking
            ? "⏹ Stop"
            : "🔊 Listen"}
        </button>
      </div>

      {/* RISK */}

      <div
        className={`risk-banner risk-${risk}`}
      >
        <span>
          Overall Risk
        </span>

        <strong>
          {risk.toUpperCase()}
        </strong>
      </div>

      {/* MAIN GRID */}

      <div className="advisory-grid">

        <div className="advisory-card">
          <div className="advisory-card-icon">
            🌾
          </div>

          <h3>
            Crop Condition
          </h3>

          <p>
            {advisory.crop_condition}
          </p>
        </div>

        <div className="advisory-card">
          <div className="advisory-card-icon">
            🌦️
          </div>

          <h3>
            Weather Risk
          </h3>

          <p>
            {advisory.weather_risk}
          </p>
        </div>

        <div className="advisory-card">
          <div className="advisory-card-icon">
            🧪
          </div>

          <h3>
            Soil Health
          </h3>

          <p>
            {advisory.soil_health}
          </p>
        </div>

        <div className="advisory-card">
          <div className="advisory-card-icon">
            🛰️
          </div>

          <h3>
            Vegetation Health
          </h3>

          <p>
            {advisory.vegetation_health}
          </p>
        </div>

      </div>

      {/* IRRIGATION */}

      <div className="recommendation-card">
        <div className="recommendation-title">
          💧 Irrigation Recommendation
        </div>

        <p>
          {advisory.irrigation_recommendation}
        </p>
      </div>

      {/* REGENERATIVE */}

      <div className="recommendation-card">
        <div className="recommendation-title">
          🌱 Regenerative Farming
        </div>

        <ul>
          {advisory.regenerative_farming?.map(
            (
              item: string,
              index: number
            ) => (
              <li key={index}>
                {item}
              </li>
            )
          )}
        </ul>
      </div>

      {/* ACTIONS */}

      <div className="recommendation-card">
        <div className="recommendation-title">
          ⚡ Immediate Farmer Actions
        </div>

        <ol>
          {advisory.immediate_actions?.map(
            (
              item: string,
              index: number
            ) => (
              <li key={index}>
                {item}
              </li>
            )
          )}
        </ol>
      </div>

      {/* REASONING */}

      <div className="reasoning-card">
        <div className="recommendation-title">
          🧠 Data-Driven Reasoning
        </div>

        <p>
          {advisory.data_driven_reasoning}
        </p>
      </div>

      {/* SUMMARY */}

      <div className="summary-card">
        <div className="recommendation-title">
          💬 Farmer Summary
        </div>

        <p>
          {advisory.summary}
        </p>
      </div>

    </div>
  );
}