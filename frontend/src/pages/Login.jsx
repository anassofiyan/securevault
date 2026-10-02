import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await loginUser(email, password);

      localStorage.setItem("access_token", data.access_token);

      navigate("/dashboard");
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
          <p className="eyebrow">PRIVATE. SECURE. SIMPLE.</p>

          <h1>
            Your files.
            <br />
            <span>Under your control.</span>
          </h1>

          <p>
            Securely store, manage and access your files
            from anywhere.
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
            <p className="eyebrow">WELCOME BACK</p>

            <h2>Sign in</h2>

            <p>
              Access your secure workspace.
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
                placeholder="Enter your password"
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

            <button
              className="auth-submit"
              type="submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>

          </form>

          <div className="auth-switch">
            <span>Don't have an account?</span>

            <button
              onClick={() => navigate("/register")}
            >
              Create account
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

export default Login;