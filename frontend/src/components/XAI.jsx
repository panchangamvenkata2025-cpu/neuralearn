import React, { useState } from "react";
import axios from "axios";

function XAI() {
  const [result, setResult] = useState(null);

  const getExplanation = async () => {
    const res = await axios.post("http://127.0.0.1:8000/api/xai/explain", {
      quiz_accuracy: 0.7,
      avg_time_per_q: 0.5,
      hint_requests: 2
    });

    setResult(res.data);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Explainable AI</h2>

      <button onClick={getExplanation}>
        Analyze Student Level
      </button>

      {result && (
        <div>
          <p>Prediction: {result.prediction === 1 ? "Advanced" : "Beginner"}</p>

          <h4>SHAP Values</h4>
          <pre>{JSON.stringify(result.shap_values, null, 2)}</pre>

          <h4>LIME Explanation</h4>
          <pre>{JSON.stringify(result.lime_explanation, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default XAI;