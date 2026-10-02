import { useNavigate } from "react-router-dom";

function Security() {
  const navigate = useNavigate();

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
          <p className="eyebrow">SECURITY</p>
          <h1>Security Center</h1>
          <p>
            Your SecureVault security status.
          </p>
        </div>

        <div className="security-grid">

          <div className="settings-card">
            <div className="security-large-icon">
              ✓
            </div>

            <h3>Authentication</h3>

            <p>
              Your account is protected using
              JWT-based authentication.
            </p>

            <span className="security-status-badge">
              Protected
            </span>
          </div>

          <div className="settings-card">
            <div className="security-large-icon">
              ◈
            </div>

            <h3>File isolation</h3>

            <p>
              File access is restricted to the
              authenticated owner.
            </p>

            <span className="security-status-badge">
              Enabled
            </span>
          </div>

          <div className="settings-card">
            <div className="security-large-icon">
              ✓
            </div>

            <h3>File validation</h3>

            <p>
              Uploaded files are checked for
              type, signature and size.
            </p>

            <span className="security-status-badge">
              Enabled
            </span>
          </div>

        </div>

      </div>
    </div>
  );
}

export default Security;