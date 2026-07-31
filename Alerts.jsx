import React, { useEffect, useState } from "react";
import api from "./api.js";
import SeverityBadge from "./components/SeverityBadge.jsx";

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [unackOnly, setUnackOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  async function loadAlerts() {
    setLoading(true);
    const res = await api.get("/alerts", { params: { unacknowledged_only: unackOnly } });
    setAlerts(res.data);
    setLoading(false);
  }

  useEffect(() => {
    loadAlerts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [unackOnly]);

  async function acknowledge(id) {
    await api.post(`/alerts/${id}/acknowledge`);
    await loadAlerts();
  }

  return (
    <div className="sx-alerts">
      <div className="sx-page__header">
        <h1 className="sx-page__title">ALERTS</h1>
        <label className="sx-toggle">
          <input
            type="checkbox"
            checked={unackOnly}
            onChange={(e) => setUnackOnly(e.target.checked)}
          />
          Unacknowledged only
        </label>
      </div>

      {loading ? (
        <div className="sx-empty">Loading...</div>
      ) : alerts.length === 0 ? (
        <div className="sx-empty">No alerts to show.</div>
      ) : (
        <div className="sx-alert-list">
          {alerts.map((a) => (
            <div key={a.id} className={`sx-alert-card sx-alert-card--${a.severity}`}>
              <div className="sx-alert-card__top">
                <SeverityBadge severity={a.severity} />
                <span className="sx-alert-card__time">
                  {new Date(a.created_at).toLocaleString()}
                </span>
              </div>
              <div className="sx-alert-card__message">{a.message}</div>
              <div className="sx-alert-card__rec">Recommendation: {a.recommendation}</div>
              {!a.acknowledged ? (
                <button className="sx-btn-sm" onClick={() => acknowledge(a.id)}>
                  ACKNOWLEDGE
                </button>
              ) : (
                <span className="sx-alert-card__ack">✓ Acknowledged</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
