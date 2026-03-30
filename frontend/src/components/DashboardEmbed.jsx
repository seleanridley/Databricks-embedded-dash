import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { DatabricksDashboard } from "@databricks/aibi-client";

const DashboardEmbed = ({ config, onError }) => {
  const containerRef = useRef(null);
  const dashboardInstance = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!config || !containerRef.current) return;

    let mounted = true;

    const initializeDashboard = async () => {
      try {
        setLoading(true);
        containerRef.current.innerHTML = "";

        dashboardInstance.current = new DatabricksDashboard({
          instanceUrl: config.workspace_url,
          workspaceId: config.workspace_id,
          dashboardId: config.dashboard_id,
          token: config.embed_token,
          container: containerRef.current,
          getNewToken: async () => {
            const response = await axios.get("/api/dashboard/embed-config");
            return response.data.embed_token;
          },
        });

        await dashboardInstance.current.initialize();

        if (mounted) {
          setLoading(false);
        }
      } catch (err) {
        console.error("Error initializing dashboard:", err);
        setLoading(false);
        onError?.(`Failed to load dashboard: ${err.message}`);
      }
    };

    initializeDashboard();

    return () => {
      mounted = false;
      if (
        dashboardInstance.current &&
        typeof dashboardInstance.current.destroy === "function"
      ) {
        dashboardInstance.current.destroy();
      }
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [config, onError]);

  return (
    <>
      {loading && <div className="loading">Loading dashboard...</div>}
      <div
        ref={containerRef}
        className="dashboard-embed"
        style={{ width: "100%", height: "100vh" }}
      />
    </>
  );
};

export default DashboardEmbed;
