import React, { useEffect, useState } from "react";
import api from "./api.js";
import SeverityBadge from "./components/SeverityBadge.jsx";

function severityForScore(score) {
  if (score >= 80) return "critical";
  if (score >= 60) return "high";
  if (score >= 35) return "medium";
  return "low";
}

// Projects lat/lng (-90..90, -180..180) onto a 0..100% box for a simple
// dependency-free equirectangular plot. Swap for Leaflet/Mapbox for real tiles.
function project(lat, lng) {
  const x = ((lng + 180) / 360) * 100;
  const y = ((90 - lat) / 180) * 100;
  return { x, y };
}

export default function Map() {
  const [suppliers, setSuppliers] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.get("/suppliers").then((res) => setSuppliers(res.data));
  }, []);

  return (
    <div className="sx-map">
      <h1 className="sx-page__title">GLOBAL SUPPLIER MAP</h1>
      <div className="sx-map__canvas">
        <div className="sx-map__grid" />
        {suppliers.map((s) => {
          const { x, y } = project(s.lat, s.lng);
          const sev = severityForScore(s.risk_score);
          return (
            <button
              key={s.id}
              className={`sx-map__pin sx-map__pin--${sev}`}
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => setSelected(s)}
              title={s.name}
            />
          );
        })}
      </div>

      {selected && (
        <div className="sx-panel sx-map__detail">
          <div className="sx-map__detail-header">
            <h2>{selected.name}</h2>
            <SeverityBadge severity={severityForScore(selected.risk_score)} />
          </div>
          <p>Country: {selected.country}</p>
          <p>Category: {selected.category}</p>
          <p>Risk Score: {selected.risk_score}/100</p>
          <p>News Sentiment: {selected.news_sentiment}</p>
          <p>Avg Delivery Delay: {selected.delivery_delay_days} days</p>
        </div>
      )}
    </div>
  );
}
