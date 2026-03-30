import React, { useEffect, useState } from "react";
import axios from "axios";
import DashboardEmbed from "./components/DashboardEmbed";
import "./App.css";

const App = () => {
  const [dashboardConfig, setDashboardConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardConfig = async () => {
      try {
        setLoading(true);
        setError(null);

        const API_BASE = import.meta.env.VITE_API_BASE_URL;
        console.log(API_BASE);
        const response = await axios.get(`${API_BASE}/api/dashboard/embed-config`);;
        console.log(response);
        setDashboardConfig(response.data);
      } catch (err) {
        console.error("Dashboard config error:", err);
        setError("Failed to load dashboard.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardConfig();
  }, []);

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="app">
      {dashboardConfig && (
        <DashboardEmbed
          config={dashboardConfig}
          onError={(message) => setError(message)}
        />
      )}
    </div>
  );
};

export default App;
