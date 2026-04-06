import React, { useState } from "react";
import { useRAG } from "../hooks/useRAG";

function UploadPage() {
  const { uploadFile } = useRAG();
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await uploadFile(formData);
    setMsg(res.message);
  };

  return (
    <div>
      <h2>Upload Study Material</h2>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>

      <p>{msg}</p>
    </div>
  );
}

export default UploadPage;