import React, { useState } from "react";
import Learn from "./components/LearnPage";
import XAI from "./components/XAI";
import Analytics from "./components/AnalyticsPage";

function App() {
  const [page, setPage] = useState("learn");

  return (
    <div className="flex h-screen">

      {/* Sidebar */}
      <div className="w-20 bg-white border-r flex flex-col items-center py-6 gap-6 shadow-card">
        <button onClick={() => setPage("learn")} className="hover:scale-110 transition">📘</button>
        <button onClick={() => setPage("xai")} className="hover:scale-110 transition">🧠</button>
        <button onClick={() => setPage("analytics")} className="hover:scale-110 transition">📊</button>
      </div>

      {/* Main */}
      <div className="flex-1 p-6 overflow-auto">
        {page === "learn" && <Learn />}
        {page === "xai" && <XAI />}
        {page === "analytics" && <Analytics />}
      </div>
    </div>
  );
}

export default App;