import { useState } from "react";

function App() {
  const [url, setUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await fetch("http://localhost:5000/archive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
    } catch (error) {
      console.error("Error submitting URL:", error);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Website Archiver</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL"
          style={{ width: "300px", marginRight: "1rem" }}
        />
        <button type="submit">Archive</button>
      </form>
    </div>
  );
}

export default App;
