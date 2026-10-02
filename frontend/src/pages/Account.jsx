import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser } from "../services/api";

function Account() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await getCurrentUser(token);
        setUser(data);
      } catch {
        localStorage.removeItem("access_token");
        navigate("/login");
      }
    }

    loadUser();
  }, []);

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
          <p className="eyebrow">ACCOUNT</p>
          <h1>Your Account</h1>
          <p>
            Manage your SecureVault account information.
          </p>
        </div>

        <div className="settings-card">
          <div className="settings-row">
            <div>
              <span className="settings-label">
                Email
              </span>

              <strong>
                {user?.email || "Loading..."}
              </strong>
            </div>
          </div>

          <div className="settings-row">
            <div>
              <span className="settings-label">
                Account ID
              </span>

              <strong>
                {user?.id || "Loading..."}
              </strong>
            </div>
          </div>

          <div className="settings-row">
            <div>
              <span className="settings-label">
                Account status
              </span>

              <strong className="status-text">
                Active
              </strong>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default Account;