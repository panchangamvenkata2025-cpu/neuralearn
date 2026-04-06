import React, { useEffect, useState } from "react";
import axios from "axios";

function AttentionPopup() {
  const [score, setScore] = useState(100);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.post(
          "http://127.0.0.1:8000/api/attention/score",
          { image_base64: "" } // later we send real frames
        );

        setScore(res.data.score);
      } catch (e) {
        console.log(e);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  if (score > 60) return null;

  return (
    <div style={{
      position: "fixed",
      top: 20,
      right: 20,
      background: "orange",
      padding: 10
    }}>
      ⚠️ You seem distracted!
    </div>
  );
}

export default AttentionPopup;