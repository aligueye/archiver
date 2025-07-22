import { useState, useEffect } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [archives, setArchives] = useState([]);
  const [selected, setSelected] = useState(null);
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

  const fetchArchives = async () => {
    try {
      const res = await fetch("http://localhost:5000/archives");
      if (!res.ok) {
        throw new Error("Failed to fetch archives.");
      }
      const data = await res.json();
      setArchives(data);
    } catch (error) {
      console.error("Error fetching archives:", error);
      setError("Failed to load archives. Please try again later.");
    }
  };

  useEffect(() => {
    fetchArchives();
  }, []);

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

      <h2>Archived URLs</h2>
      <ul>
        {archives.map((archive) => (
          <li key={archive.domain}>
            <strong>{archive.domain}</strong>
            <ul>
              {archive.versions.map((timestamp) => (
                <li key={timestamp}>
                  <button
                    onClick={() =>
                      setSelected({
                        domain: archive.domain,
                        timestamp,
                      })
                    }
                  >
                    {timestamp}
                  </button>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
      {archives.length === 0 && <p>No archives available.</p>}
      {selected && (
        <>
          <h2>Snapshot Preview</h2>
          <p>
            Viewing snapshot from <strong>{selected.domain}</strong> at{" "}
            <strong>{selected.timestamp}</strong>
          </p>
          <iframe
            title="snapshot"
            src={`http://localhost:5000/archive/${selected.domain}/${selected.timestamp}/`}
            style={{ width: "100%", height: "600px", border: "1px solid #ccc" }}
          />
        </>
      )}
    </div>
  );
}

export default App;
