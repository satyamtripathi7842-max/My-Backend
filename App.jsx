import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./Login.jsx";
import Dashboard from "./Dashboard.jsx";
import Alerts from "./Alerts.jsx";
import Map from "./Map.jsx";
import AIChat from "./AIChat.jsx";
import Navbar from "./components/Navbar.jsx";

function isAuthed() {
  return !!localStorage.getItem("sx_token");
}

function Protected({ children }) {
  if (!isAuthed()) return <Navigate to="/login" replace />;
  return (
    <>
      <Navbar />
      <div className="sx-page">{children}</div>
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Protected>
            <Dashboard />
          </Protected>
        }
      />
      <Route
        path="/alerts"
        element={
          <Protected>
            <Alerts />
          </Protected>
        }
      />
      <Route
        path="/map"
        element={
          <Protected>
            <Map />
          </Protected>
        }
      />
      <Route
        path="/chat"
        element={
          <Protected>
            <AIChat />
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
