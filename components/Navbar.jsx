import React from 'react';
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const username = localStorage.getItem("sx_username");

  function logout() {
    localStorage.removeItem("sx_token");
    localStorage.removeItem("sx_username");
    navigate("/login");
  }

  return (
    <nav className="sx-navbar">
      <div className="sx-navbar__brand">
        <span className="sx-navbar__dot" />
        SENTINELX-AI
      </div>
      <div className="sx-navbar__links">
        <Link to="/">DASHBOARD</Link>
        <Link to="/alerts">ALERTS</Link>
        <Link to="/map">MAP</Link>
        <Link to="/chat">AI CHAT</Link>
      </div>
      <div className="sx-navbar__user">
        {username && <span>{username}</span>}
        <button onClick={logout}>LOGOUT</button>
      </div>
    </nav>
  );
}
