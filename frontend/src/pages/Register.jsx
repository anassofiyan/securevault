import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/api";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser(email, password);

      setSuccess("Account created successfully.");

      setTimeout(() => {
        navigate("/login");
      }, 900);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">

      <div className="auth-decoration">
        <div className="glow glow-one"></div>
        <div className="glow glow-two"></div>

        <div className="auth-brand">
          <div className="brand-mark">◈</div>
          <span>SecureVault</span>
        </div>

        <div className="auth-message">
          <p className="eyebrow">START SECURE</p>

          <h1>
            A safer place
            <br />
            <span>for your files.</span>
          </h1>

          <p>
            Create your private workspace and keep
            your files organized and protected.
          </p>
        </div>

        <div className="auth-security-note">
          <span>●</span>
          Your connection is protected
        </div>
      </div>

      <div className="auth-panel">

        <div className="auth-form-container">

          <div className="mobile-auth-brand">
            <div className="brand-mark">◈</div>
            SecureVault
          </div>

          <div className="auth-heading">
            <p className="eyebrow">GET STARTED</p>

            <h2>Create account</h2>

            <p>
              Set up your secure workspace.
            </p>
          </div>

          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >

            <label>
              Email

              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
              />
            </label>

            <label>
              Password

              <input
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
              />
            </label>

            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}

            {success && (
              <div className="auth-success">
                {success}
              </div>
            )}

            <button
              className="auth-submit"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Creating account..."
                : "Create account"}
            </button>

          </form>

          <div className="auth-switch">
            <span>Already have an account?</span>

            <button
              onClick={() => navigate("/login")}
            >
              Sign in
            </button>
          </div>

          <div className="auth-footer">
            <span>◈ SecureVault</span>
            <span>Private file storage</span>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Register;