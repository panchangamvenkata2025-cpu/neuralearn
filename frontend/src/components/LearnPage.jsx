import React, { useState } from "react";
import { useRAG } from "../hooks/useRAG";

function LearnPage() {
  const { askQuestion } = useRAG();

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleAsk = async () => {
    const res = await askQuestion({
      question,
      collection_id: "new_pdf",
      level: "beginner",
      cognitive_mode: "visual"
    });

    setAnswer(res.answer);
  };

  return (
    <div>
      <h2>AI Learning</h2>

      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask anything..."
      />

      <button onClick={handleAsk}>Ask</button>

      <div style={{ marginTop: 20 }}>
        <h3>Answer:</h3>
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default LearnPage;