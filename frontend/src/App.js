import { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch("http://localhost:5000/archive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.message || "Failed to archive the URL.");
      }
    } catch (error) {
      console.error("Error submitting URL:", error);
      setError(
        error?.message || "Failed to archive the URL. Please try again."
      );
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
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default App;
