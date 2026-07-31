import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api.js";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login"); // login | register
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      let res;
      if (mode === "login") {
        const form = new URLSearchParams();
        form.append("username", username);
        form.append("password", password);
        res = await api.post("/auth/login", form, {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
      } else {
        res = await api.post("/auth/register", { username, password });
      }
      localStorage.setItem("sx_token", res.data.access_token);
      localStorage.setItem("sx_username", username);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="sx-login">
      <div className="sx-login__panel">
        <div className="sx-login__brand">
          <span className="sx-navbar__dot" />
          SENTINELX-AI
        </div>
        <div className="sx-login__subtitle">Supply Chain Risk Intelligence Console</div>

        <form onSubmit={handleSubmit} className="sx-login__form">
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>

          {error && <div className="sx-login__error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "PLEASE WAIT..." : mode === "login" ? "SIGN IN" : "CREATE ACCOUNT"}
          </button>
        </form>

        <button
          className="sx-login__toggle"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Need an account? Register" : "Have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
