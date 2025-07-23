import React, { useState } from "react";

function SnapshotViewer({ selected }) {
  const [isIframeLoading, setIsIframeLoading] = useState(true);

  if (!selected) return null;

  return (
    <>
      <h2>Snapshot Preview</h2>
      <p>
        Viewing snapshot from <strong>{selected.domain}</strong> at{" "}
        <strong>{selected.timestamp}</strong>
      </p>
      {isIframeLoading && <p>Loading snapshot...</p>}
      <iframe
        title="snapshot"
        src={`http://localhost:5000/archive/${selected.domain}/${selected.timestamp}/`}
        style={{
          width: "100%",
          height: "600px",
          border: "1px solid #ccc",
          display: isIframeLoading ? "none" : "block",
        }}
        onLoad={() => setIsIframeLoading(false)}
      />
    </>
  );
}

export default SnapshotViewer;
