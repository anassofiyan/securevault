import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getFiles,
  downloadFile,
  deleteFile,
} from "../services/api";

function MyFiles() {
  const navigate = useNavigate();

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    loadFiles();
  }, []);

  async function loadFiles() {
    try {
      setLoading(true);
      setError("");

      const data = await getFiles(token);
      setFiles(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload(file) {
    try {
      const blob = await downloadFile(token, file.id);

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = file.filename;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError(error.message);
    }
  }

  async function handleDelete(fileId) {
    if (!window.confirm("Delete this file?")) {
      return;
    }

    try {
      await deleteFile(token, fileId);

      setFiles((currentFiles) =>
        currentFiles.filter((file) => file.id !== fileId)
      );
    } catch (error) {
      setError(error.message);
    }
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div className="simple-page">
      <div className="simple-page-inner">

        <button
          className="back-button"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>

        <div className="simple-page-heading">
          <p className="eyebrow">YOUR STORAGE</p>
          <h1>My Files</h1>
          <p>
            Manage your securely stored files.
          </p>
        </div>

        {error && (
          <div className="error-banner">
            <span>!</span>
            {error}
          </div>
        )}

        {loading ? (
          <div className="empty-state">
            <h3>Loading files...</h3>
          </div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">▣</div>

            <h3>No files yet</h3>

            <p>
              Upload a file from your dashboard.
            </p>

            <button
              className="auth-submit"
              onClick={() => navigate("/dashboard")}
            >
              Upload a file
            </button>
          </div>
        ) : (
          <div className="file-list">
            {files.map((file) => (
              <article
                className="file-card"
                key={file.id}
              >
                <div className="file-info">
                  <div className="file-icon">
                    ▣
                  </div>

                  <div className="file-details">
                    <strong title={file.filename}>
                      {file.filename}
                    </strong>

                    <span>
                      {file.content_type || "Unknown"} ·{" "}
                      {formatFileSize(file.size)}
                    </span>
                  </div>
                </div>

                <div className="file-actions">
                  <button
                    className="download-button"
                    onClick={() =>
                      handleDownload(file)
                    }
                  >
                    ↓ Download
                  </button>

                  <button
                    className="delete-button"
                    onClick={() =>
                      handleDelete(file.id)
                    }
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default MyFiles;