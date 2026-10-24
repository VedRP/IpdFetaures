import { Link, useNavigate } from "react-router-dom";
import { DEMO } from "../routes";
import { GoogleIcon } from "../components/Icon";
import Logo from "../components/Logo";

const PORTAL_LABELS = { user: "Student", employer: "Employer", moderator: "Moderator" };

const PORTAL_DASHBOARD = {
  user: `/user/${DEMO.username}/overview`,
  employer: `/employer/company/${DEMO.companyId}/overview`,
  moderator: `/moderator/${DEMO.username}`,
};

const CROSS_LINKS = {
  user: [
    { label: "Are you a moderator?", to: "/moderator/login", cta: "Sign in here" },
    { label: null, to: "/employer/login", cta: "Employer portal →" },
  ],
  employer: [{ label: null, to: "/user/login", cta: "Student portal →" }],
  moderator: [{ label: null, to: "/user/login", cta: "Student portal →" }],
};

export default function Auth({ portal, mode }) {
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    navigate(PORTAL_DASHBOARD[portal]);
  }

  return (
    <div className="auth-page">
      <Link to="/" className="auth-back">
        &larr; iFind
      </Link>

      <div className="auth-center">
        <div className="auth-header">
          <div className="auth-header-logo">
            <Logo size="md" />
          </div>
          <h1>{mode === "login" ? `Sign in to iFind` : "Create your account"}</h1>
          <p className="sub">
            {PORTAL_LABELS[portal]} portal &middot; frontend-only demo, no backend connected
          </p>
        </div>

        <div className="card auth-card">
          <form onSubmit={handleSubmit}>
            {mode === "register" && (
              <div className="field">
                <label className="label">Full name</label>
                <input placeholder="e.g. Suraj Mehta" />
              </div>
            )}
            <div className="field">
              <label className="label">Email or username</label>
              <input placeholder="you@example.com" />
            </div>
            <div className="field">
              <label className="label">Password</label>
              <input placeholder="Your password" type="password" />
            </div>

            {mode === "login" && (
              <div style={{ textAlign: "right", marginBottom: 16 }}>
                <a href="#forgot" className="auth-link" onClick={(e) => e.preventDefault()}>
                  Forgot password?
                </a>
              </div>
            )}

            <button className="btn-primary" type="submit">
              <span>{mode === "login" ? "Sign in" : "Create account"}</span>
              <span>&rarr;</span>
            </button>

            {CROSS_LINKS[portal]?.map((link) => (
              <p className="auth-footline" key={link.cta}>
                {link.label ? `${link.label} ` : null}
                <Link to={link.to} className="auth-link">
                  {link.cta}
                </Link>
              </p>
            ))}
          </form>

          <div className="auth-divider">
            <span>or continue with</span>
          </div>

          <button className="btn-secondary auth-oauth" type="button">
            Continue with LinkedIn
          </button>
          <button className="btn-secondary auth-oauth auth-oauth-google" type="button">
            <GoogleIcon width={16} height={16} />
            <span>Continue with Google</span>
          </button>
        </div>

        <p className="footnote">
          {mode === "login" ? (
            <>
              Don't have an account? <Link to={`/${portal}/register`}>Register free</Link>
            </>
          ) : (
            <>
              Already have an account? <Link to={`/${portal}/login`}>Sign in</Link>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
