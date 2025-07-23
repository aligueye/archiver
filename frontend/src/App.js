import { useState, useEffect } from "react";
import ArchiveList from "./ArchiveList";
import SnapshotViewer from "./SnapshotViewer";

function App() {
  const [url, setUrl] = useState("");
  const [archives, setArchives] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingArchives, setIsLoadingArchives] = useState(true);
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage("");
    setIsSubmitting(true);
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
      setSuccessMessage("Successfully archived!");
      setUrl("");
      await fetchArchives(); // Refresh list after archiving
    } catch (error) {
      console.error("Error submitting URL:", error);
      setError(
        error?.message || "Failed to archive the URL. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const fetchArchives = async () => {
    setIsLoadingArchives(true);
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
    } finally {
      setIsLoadingArchives(false);
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
          disabled={isSubmitting}
        />
        <button type="submit" disabled={isSubmitting || !url.trim()}>
          {isSubmitting ? "Archiving..." : "Archive"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

      <h2>Archived URLs</h2>
      {isLoadingArchives ? (
        <p>Loading archives...</p>
      ) : (
        <ArchiveList archives={archives} onSelect={setSelected} />
      )}

      <SnapshotViewer selected={selected} />
    </div>
  );
}

export default App;
