"use client";

interface IntelligenceCardsProps {
  data: any;
}

export default function IntelligenceCards({
  data,
}: IntelligenceCardsProps) {
  const soil = data?.soil;
  const weather = data?.weather;
  const satellite = data?.satellite;

  return (
    <div className="intelligence-grid">

      {/* SOIL */}

      <div className="intelligence-card">
        <div className="card-icon">
          🧪
        </div>

        <div>
          <div className="card-title">
            Soil Intelligence
          </div>

          <div className="card-value">
            pH {soil?.ph ?? "-"}
          </div>

          <div className="card-details">
            <span>
              N: {soil?.nitrogen ?? "-"}
            </span>

            <span>
              P: {soil?.phosphorus ?? "-"}
            </span>

            <span>
              K: {soil?.potassium ?? "-"}
            </span>

            <span>
              Moisture: {soil?.moisture ?? "-"}%
            </span>
          </div>
        </div>
      </div>

      {/* WEATHER */}

      <div className="intelligence-card">
        <div className="card-icon">
          🌦️
        </div>

        <div>
          <div className="card-title">
            Weather Intelligence
          </div>

          <div className="card-value">
            {weather?.temperature ?? "-"}°C
          </div>

          <div className="card-details">
            <span>
              Rain Probability:{" "}
              {weather?.rain_probability ?? "-"}%
            </span>

            <span>
              Rainfall:{" "}
              {weather?.rainfall ?? "-"} mm
            </span>
          </div>
        </div>
      </div>

      {/* SATELLITE */}

      <div className="intelligence-card">
        <div className="card-icon">
          🛰️
        </div>

        <div>
          <div className="card-title">
            Satellite Intelligence
          </div>

          <div className="card-value">
            NDVI {satellite?.ndvi ?? "-"}
          </div>

          <div className="card-details">
            <span>
              Health:{" "}
              {satellite?.vegetation_health ??
                "-"}
            </span>

            <span>
              Trend:{" "}
              {satellite?.vegetation_trend ??
                "-"}
            </span>
          </div>
        </div>
      </div>

    </div>
  );
}