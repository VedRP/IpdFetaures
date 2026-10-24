import { Link } from "react-router-dom";
import { SearchIcon, ZapIcon, UserIcon, StarIcon } from "../components/Icon";
import CountUp from "../components/CountUp";
import Logo from "../components/Logo";
import { accentColor } from "../accentColors";

const POPULAR = ["React Developer", "Data Science", "UI/UX Design", "Marketing", "Finance", "Machine Learning"];

const CATEGORIES = [
  { code: "TC", label: "Technology" },
  { code: "DS", label: "Design" },
  { code: "MK", label: "Marketing" },
  { code: "FN", label: "Finance" },
  { code: "OP", label: "Operations" },
  { code: "CN", label: "Content" },
];

const FEATURES = [
  { Icon: SearchIcon, label: "Personalized Job Matching" },
  { Icon: ZapIcon, label: "Top Companies & Startups" },
  { Icon: UserIcon, label: "Build Your Profile" },
  { Icon: StarIcon, label: "Kickstart Your Career" },
];

const STATS = [
  { value: "50,000+", label: "Active Internships" },
  { value: "2M+", label: "Students Registered" },
  { value: "10,000+", label: "Partner Companies" },
  { value: "95%", label: "Placement Rate" },
];

export default function Home() {
  return (
    <div className="landing">
      <div className="bg-sphere bg-sphere-1" aria-hidden="true" />
      <div className="bg-sphere bg-sphere-2" aria-hidden="true" />
      <div className="bg-sphere bg-sphere-3" aria-hidden="true" />
      <div className="bg-sphere bg-sphere-4" aria-hidden="true" />

      <header className="landing-topbar">
        <Link to="/" className="brand">
          <Logo size="md" />
        </Link>

        <nav className="landing-nav">
          <Link to="/user/login">Internships</Link>
          <Link to="/user/login">How it works</Link>
        </nav>

        <div className="landing-auth-actions">
          <Link to="/user/login" className="btn-secondary">
            Login
          </Link>
          <Link to="/user/register" className="btn-primary landing-register">
            <span>Register</span>
          </Link>
        </div>
      </header>

      <section className="hero-grid">
        <div className="hero-copy">
          <div className="hero-eyebrow">From Campus to Career</div>

          <h1 className="hero-title2">
            Your Skills.
            <br />
            Real <span className="accent">Opportunities.</span>
            <br />A Brighter Future.
          </h1>

          <p className="hero-sub2">
            Discover internships and job opportunities that match your skills, interests and goals.
          </p>

          <div className="hero-feature-row">
            {FEATURES.map((f) => (
              <div className="hero-feature" key={f.label}>
                <div className="hero-feature-icon">
                  <f.Icon />
                </div>
                <span>{f.label}</span>
              </div>
            ))}
          </div>

        </div>

        <div className="hero-visual">
          <img
            src="/hero-scene.png"
            alt="Graduate on campus with a Google internship offer"
            className="hero-scene-img"
          />
        </div>
      </section>

      <section className="hero-search-section">
        <div className="hero-search">
          <input placeholder="Role, skill, or company..." />
          <input placeholder="City or Work from Home" />
          <button className="btn-primary hero-search-btn" type="button">
            <span>Search</span>
            <span>&rarr;</span>
          </button>
        </div>

        <div className="hero-popular">
          <span className="label">Popular:</span>
          {POPULAR.map((p) => (
            <span className="pill" key={p}>
              {p}
            </span>
          ))}
        </div>

        <div className="hero-categories">
          {CATEGORIES.map((c) => (
            <span className="category-chip" key={c.label}>
              <span className="category-icon" style={{ background: accentColor(c.label) }}>
                {c.code}
              </span>
              {c.label}
            </span>
          ))}
        </div>
      </section>

      <section className="landing-stats">
        {STATS.map((s) => (
          <div className="landing-stat" key={s.label}>
            <div className="value">
              <CountUp value={s.value} />
            </div>
            <div className="label">{s.label}</div>
          </div>
        ))}
      </section>

      <div className="landing-footer-label">Internships from top companies</div>

      <div className="portal-links-row">
        <span className="label">Looking for a different portal?</span>
        <Link to="/employer/login" className="pill">
          Employer portal &rarr;
        </Link>
        <Link to="/moderator/login" className="pill">
          Moderator portal &rarr;
        </Link>
      </div>
    </div>
  );
}
