import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getCurrentUser,
  getFiles,
  uploadFile,
  deleteFile,
  downloadFile,
} from "../services/api";

function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [userData, fileData] = await Promise.all([
        getCurrentUser(token),
        getFiles(token),
      ]);

      setUser(userData);
      setFiles(fileData);
    } catch (error) {
      setError(error.message);

      if (
        error.message.includes("Invalid") ||
        error.message.includes("expired")
      ) {
        localStorage.removeItem("access_token");
        navigate("/login");
      }
    } finally {
      setLoading(false);
    }
  }

  async function processFile(file) {
    if (!file) return;

    try {
      setUploading(true);
      setError("");

      await uploadFile(token, file);
      await loadDashboard();
    } catch (error) {
      setError(error.message);
    } finally {
      setUploading(false);
    }
  }

  function handleFileSelect(event) {
    const file = event.target.files[0];

    if (file) {
      processFile(file);
    }

    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);

    const file = event.dataTransfer.files[0];

    if (file) {
      processFile(file);
    }
  }

  async function handleDownload(file) {
    try {
      setError("");

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
    const confirmed = window.confirm(
      "Are you sure you want to delete this file?"
    );

    if (!confirmed) return;

    try {
      setError("");

      await deleteFile(token, fileId);

      setFiles((currentFiles) =>
        currentFiles.filter((file) => file.id !== fileId)
      );
    } catch (error) {
      setError(error.message);
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    navigate("/login");
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

  function getFileIcon(contentType) {
    if (contentType?.startsWith("image/")) {
      return "▧";
    }

    if (contentType === "application/pdf") {
      return "▤";
    }

    return "≡";
  }

  function getGreeting() {
    const hour = new Date().getHours();

    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";

    return "Good evening";
  }

  const totalSize = files.reduce(
    (total, file) => total + file.size,
    0
  );

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-logo">◈</div>
        <p>Loading SecureVault...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-shell">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-mark">◈</div>
          <span>SecureVault</span>
        </div>

        <div className="sidebar-section">
          <p className="sidebar-label">WORKSPACE</p>

          <button
            className="nav-item active"
            onClick={() => navigate("/dashboard")}
          >
            <span>◉</span>
            Overview
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/files")}
          >
            <span>▣</span>
            My Files
          </button>
        </div>

        <div className="sidebar-section">
          <p className="sidebar-label">SETTINGS</p>

          <button
            className="nav-item"
            onClick={() => navigate("/account")}
          >
            <span>⚙</span>
            Account
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/security")}
          >
            <span>◉</span>
            Security
          </button>
        </div>

        <div className="sidebar-bottom">

          <div className="security-status">
            <div className="status-dot"></div>

            <div>
              <strong>Session active</strong>
              <span>Authenticated</span>
            </div>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            ⇥ Sign out
          </button>

        </div>

      </aside>


      {/* MAIN */}

      <main className="dashboard-main">

        {/* TOPBAR */}

        <header className="topbar">

          <div className="mobile-brand">
            <div className="brand-mark">◈</div>
            <span>SecureVault</span>
          </div>

          <div className="topbar-actions">

            <button className="icon-button">
              ◌
            </button>

            <div className="avatar">
              {user?.email?.charAt(0).toUpperCase()}
            </div>

          </div>

        </header>


        {/* CONTENT */}

        <div className="dashboard-content">

          {/* WELCOME */}

          <section className="welcome-section">

            <div>

              <p className="eyebrow">
                SECURE WORKSPACE
              </p>

              <h1>
                {getGreeting()}.
              </h1>

              <p className="welcome-email">
                {user?.email}
              </p>

            </div>

          </section>


          {/* STATS */}

          <section className="stats-grid">

            <div className="stat-card">

              <div className="stat-icon">
                ▣
              </div>

              <div>
                <span>Total files</span>

                <strong>
                  {files.length}
                </strong>
              </div>

            </div>


            <div className="stat-card">

              <div className="stat-icon">
                ◫
              </div>

              <div>
                <span>Storage used</span>

                <strong>
                  {formatFileSize(totalSize)}
                </strong>
              </div>

            </div>


            <div className="stat-card security-card">

              <div className="stat-icon security-icon">
                ✓
              </div>

              <div>
                <span>Security</span>

                <strong>
                  Protected
                </strong>
              </div>

            </div>

          </section>


          {/* ERROR */}

          {error && (
            <div className="error-banner">
              <span>!</span>
              {error}
            </div>
          )}


          {/* UPLOAD */}

          <section
            className={`upload-zone ${
              dragging ? "dragging" : ""
            }`}
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >

            <div className="upload-icon">
              ↑
            </div>

            <div>

              <h3>
                {uploading
                  ? "Uploading file..."
                  : "Drop files here"}
              </h3>

              <p>
                or click below to browse from your computer
              </p>

            </div>


            <label className="upload-button">

              {uploading
                ? "Uploading..."
                : "+ Choose file"}

              <input
                type="file"
                onChange={handleFileSelect}
                disabled={uploading}
                hidden
              />

            </label>


            <span className="upload-hint">
              PDF · PNG · JPG · TXT · Max 10 MB
            </span>

          </section>


          {/* FILES */}

          <section className="files-section">

            <div className="section-heading">

              <div>

                <p className="eyebrow">
                  YOUR STORAGE
                </p>

                <h2>
                  Your Files
                  <span>
                    {files.length}
                  </span>
                </h2>

              </div>

            </div>


            {files.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  ▣
                </div>

                <h3>
                  No files yet
                </h3>

                <p>
                  Upload your first file to start using
                  SecureVault.
                </p>

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
                        {getFileIcon(file.content_type)}
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

          </section>


          {/* FOOTER */}

          <footer className="dashboard-footer">

            <span>
              ◈ SecureVault
            </span>

            <span>
              Your files stay private.
            </span>

          </footer>

        </div>

      </main>

    </div>
  );
}

export default Dashboard;