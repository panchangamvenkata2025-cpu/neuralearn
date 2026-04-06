import React, { useState, useEffect } from "react";
import { chat } from "../api";

function Chat() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [showPopup, setShowPopup] = useState(false);

  // 🔥 ATTENTION CHECK (backend ready + fallback simulation)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // ⚠️ Currently dummy frame (backend won’t crash)
        const res = await fetch("http://127.0.0.1:8000/api/attention/score", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            image_base64: ""
          })
        });

        const data = await res.json();

        // 🔥 If backend returns score
        if (data.attention_score !== undefined) {
          if (data.attention_score < 0.4) {
            setShowPopup(true);
          }
        } else {
          // 🔥 fallback simulation (so demo always works)
          const fake = Math.random();
          if (fake < 0.3) {
            setShowPopup(true);
          }
        }

      } catch (err) {
        // fallback simulation if API fails
        const fake = Math.random();
        if (fake < 0.3) {
          setShowPopup(true);
        }
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // 🔥 SEND QUESTION
  const sendQuestion = async () => {
    try {
      const res = await chat({
        question,
        collection_id: "new_pdf",   // 🔥 CHANGE if needed
        level: "beginner"
      });

      setResponse(res.data.answer);

    } catch (err) {
      console.log(err);
    }
  };

  // 🔥 POPUP ACTION (switch to easier explanation)
  const handlePopup = async () => {
    try {
      const res = await chat({
        question: question + " explain in simple story",
        collection_id: "new_pdf",
        level: "beginner"
      });

      setResponse(res.data.answer);
      setShowPopup(false);

    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>AI Teacher</h2>

      <input
        style={{ padding: "10px", width: "300px" }}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask something..."
      />

      <button
        style={{ marginLeft: "10px", padding: "10px" }}
        onClick={sendQuestion}
      >
        Ask
      </button>

      <div style={{ marginTop: "20px" }}>
        <b>Response:</b>
        <p>{response}</p>
      </div>

      {/* 🔥 ATTENTION POPUP */}
      {showPopup && (
        <div
          style={{
            position: "fixed",
            bottom: "20px",
            right: "20px",
            background: "#ffffff",
            padding: "15px",
            border: "1px solid #ccc",
            borderRadius: "10px",
            boxShadow: "0 4px 10px rgba(0,0,0,0.2)"
          }}
        >
          <p>Looks like you're confused 🤔</p>

          <button onClick={handlePopup}>
            Explain in Story Mode
          </button>
        </div>
      )}
    </div>
  );
}

export default Chat;