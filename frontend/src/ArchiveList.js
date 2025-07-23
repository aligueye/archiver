import { useState } from "react";

function ArchiveList({ archives, onSelect }) {
  const [expanded, setExpanded] = useState({});

  const toggleExpand = (domain) => {
    setExpanded((prev) => ({
      ...prev,
      [domain]: !prev[domain],
    }));
  };

  if (archives.length === 0) {
    return <p>No archives available.</p>;
  }

  return (
    <ul>
      {archives.map((archive) => (
        <li key={archive.domain}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <strong>{archive.domain}</strong>
            <button
              onClick={() => toggleExpand(archive.domain)}
              style={{ marginLeft: "1rem" }}
            >
              {expanded[archive.domain] ? "Hide" : "Show"} Versions
            </button>
          </div>
          {expanded[archive.domain] && (
            <ul>
              {archive.versions.map((timestamp) => (
                <li key={timestamp}>
                  <button
                    onClick={() =>
                      onSelect({ domain: archive.domain, timestamp })
                    }
                  >
                    {timestamp}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </li>
      ))}
    </ul>
  );
}

export default ArchiveList;
