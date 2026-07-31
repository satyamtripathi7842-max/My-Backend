import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import api from "./api.js";
import Card from "./components/Card.jsx";

const SEVERITY_COLOR = {
  low: "#3fb950",
  medium: "#d4a72c",
  high: "#e8833a",
  critical: "#f85149",
};

function severityForScore(score) {
  if (score >= 80) return "critical";
  if (score >= 60) return "high";
  if (score >= 35) return "medium";
  return "low";
}

export default function Dashboard() {
  const [suppliers, setSuppliers] = useState([]);
  const [form, setForm] = useState({
    name: "",
    country: "",
    category: "general",
    lat: 0,
    lng: 0,
    financial_health: 70,
    delivery_delay_days: 0,
    geopolitical_risk: 20,
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  async function loadSuppliers() {
    setLoading(true);
    const res = await api.get("/suppliers");
    setSuppliers(res.data);
    setLoading(false);
  }

  useEffect(() => {
    loadSuppliers();
  }, []);

  const stats = useMemo(() => {
    const total = suppliers.length;
    const avgRisk = total
      ? Math.round(suppliers.reduce((s, x) => s + x.risk_score, 0) / total)
      : 0;
    const critical = suppliers.filter((s) => s.risk_score >= 80).length;
    const watch = suppliers.filter((s) => s.risk_score >= 60 && s.risk_score < 80).length;
    return { total, avgRisk, critical, watch };
  }, [suppliers]);

  async function handleAddSupplier(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/suppliers", form);
      setForm({
        name: "",
        country: "",
        category: "general",
        lat: 0,
        lng: 0,
        financial_health: 70,
        delivery_delay_days: 0,
        geopolitical_risk: 20,
      });
      await loadSuppliers();
    } finally {
      setSubmitting(false);
    }
  }

  async function refreshRisk(id) {
    await api.post(`/suppliers/${id}/refresh`);
    await loadSuppliers();
  }
  async function deleteSupplier(id, name) {
      if (!window.confirm(`Delete ${name}? This cannot be undone.`)) return;
      await api.delete(`/suppliers/${id}`);
      await loadSuppliers();
    }

  return (
    <div className="sx-dashboard">
      <h1 className="sx-page__title">RISK OVERVIEW</h1>

      <div className="sx-cards-row">
        <Card title="TOTAL SUPPLIERS" value={stats.total} tone="neutral" />
        <Card title="AVG RISK SCORE" value={`${stats.avgRisk}/100`} tone="info" />
        <Card title="WATCHLIST" value={stats.watch} tone="warn" />
        <Card title="CRITICAL" value={stats.critical} tone="danger" />
      </div>

      <div className="sx-panel">
        <h2>SUPPLIER RISK CHART</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={suppliers}>
            <CartesianGrid stroke="#20293a" strokeDasharray="3 3" />
            <XAxis dataKey="name" stroke="#8b98ac" tick={{ fontSize: 11 }} />
            <YAxis stroke="#8b98ac" domain={[0, 100]} />
            <Tooltip
              contentStyle={{ background: "#111826", border: "1px solid #20293a", color: "#e6edf3" }}
            />
            <Bar dataKey="risk_score" radius={[3, 3, 0, 0]}>
              {suppliers.map((s, i) => (
                <Cell key={i} fill={SEVERITY_COLOR[severityForScore(s.risk_score)]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
<div className="sx-panel">
        <h2>ADD SUPPLIER</h2>
        <form className="sx-form-grid" onSubmit={handleAddSupplier}>
          <label>
            Name
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>
          <label>
            Country
            <input
              value={form.country}
              onChange={(e) => setForm({ ...form, country: e.target.value })}
              required
            />
          </label>
          <label>
            Category
            <input
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            />
          </label>
          <label>
            Financial Health (0-100)
            <input
              type="number"
              value={form.financial_health}
              onChange={(e) => setForm({ ...form, financial_health: Number(e.target.value) })}
            />
          </label>
          <label>
            Avg Delivery Delay (days)
            <input
              type="number"
              value={form.delivery_delay_days}
              onChange={(e) => setForm({ ...form, delivery_delay_days: Number(e.target.value) })}
            />
          </label>
          <label>
            Geopolitical Risk (0-100)
            <input
              type="number"
              value={form.geopolitical_risk}
              onChange={(e) => setForm({ ...form, geopolitical_risk: Number(e.target.value) })}
            />
          </label>
          <label>
            Latitude
            <input
              type="number"
              value={form.lat}
              onChange={(e) => setForm({ ...form, lat: Number(e.target.value) })}
            />
          </label>
          <label>
            Longitude
            <input
              type="number"
              value={form.lng}
              onChange={(e) => setForm({ ...form, lng: Number(e.target.value) })}
            />
          </label>
          <button type="submit" disabled={submitting}>
            {submitting ? "ADDING..." : "ADD SUPPLIER"}
          </button>
        </form>
      </div>

      <div className="sx-panel">
        <h2>SUPPLIERS</h2>
        {loading ? (
          <div className="sx-empty">Loading...</div>
        ) : (
          <table className="sx-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Country</th>
                <th>Category</th>
                <th>Risk</th>
                <th>Sentiment</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{s.country}</td>
                  <td>{s.category}</td>
                  <td>
                    <span className={`sx-badge sx-badge--${severityForScore(s.risk_score)}`}>
                      {s.risk_score}
                    </span>
                  </td>
                  <td>{s.news_sentiment}</td>
                  <td>
                    <button className="sx-btn-sm" onClick={() => refreshRisk(s.id)}>
                      REFRESH
                    </button>{" "}
                    <button className="sx-btn-sm" onClick={() => deleteSupplier(s.id, s.name)}>
                      DELETE
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
