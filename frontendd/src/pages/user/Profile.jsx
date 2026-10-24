// Mirrors ifind's real Profile page structure (header card + quick-links
// nav + stacked panels: Preferences, Education, Skills, Languages,
// Internships, Projects, Summary, Accomplishments) — static display only,
// no edit drawer, using only fields this app actually collects.

import {
  DiamondIcon,
  GraduationCapIcon,
  BookOpenIcon,
  GlobeIcon,
  BriefcaseIcon,
  ToolIcon,
  EditIcon,
  AwardIcon,
} from "../../components/Icon";
import PageHeader from "../../components/PageHeader";

const QUICK_LINKS = [
  ["preferences", "Preference"],
  ["education", "Education"],
  ["skills", "Key skills"],
  ["languages", "Languages"],
  ["internships", "Internships"],
  ["projects", "Projects"],
  ["summary", "Profile summary"],
  ["accomplishments", "Accomplishments"],
];

const SKILL_GROUPS = [
  { field: "Programming Languages", skills: ["C", "C++", "Java", "Python"] },
  { field: "Web & Frameworks", skills: ["React", "Node.js", "HTML", "CSS"] },
  { field: "Data & Tools", skills: ["NumPy", "Git", "MySQL"] },
];

const EDUCATION = [
  {
    type: "B.Tech",
    course: "Computer Engineering",
    institution: "Dwarkadas J. Sanghvi College of Engineering",
    period: "2023 – 2027",
    output: "8.4 CGPA",
  },
  {
    type: "Higher Secondary",
    course: "Science (PCM)",
    institution: "Ramniranjan Jhunjhunwala Junior College",
    period: "2021 – 2023",
    output: "92%",
  },
];

const LANGUAGES = [
  { name: "English", level: "Professional" },
  { name: "Hindi", level: "Native" },
  { name: "Marathi", level: "Native" },
];

const INTERNSHIPS = [
  {
    role: "Frontend Development Intern",
    company: "PixelCraft Studio",
    period: "May 2025 – Jul 2025",
    points: ["Built reusable React components for the client dashboard", "Improved page load time by 30%"],
  },
];

const PROJECTS = [
  {
    name: "Scam Detector for Internship Listings",
    stack: "Python, scikit-learn, FastAPI",
    desc: "Rule-based + anomaly detection pipeline flagging fraudulent internship postings.",
  },
  {
    name: "Campus Event Tracker",
    stack: "React, Node.js, MongoDB",
    desc: "Full-stack app for discovering and RSVPing to college events.",
  },
];

const CERTIFICATIONS = [
  { name: "Meta Front-End Developer", issuer: "Coursera", year: "2025" },
  { name: "Python for Data Science", issuer: "NPTEL", year: "2024" },
];

function Panel({ id, icon, title, children }) {
  return (
    <section id={id} className="profile-panel card">
      <div className="profile-panel-head">
        <span className="profile-panel-icon">{icon}</span>
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Empty({ text }) {
  return <p className="profile-empty">{text}</p>;
}

export default function Profile({ section = "10", title = "Profile" }) {
  const missing = ["Upload photo", "Add certificates"];

  return (
    <>
      <PageHeader step={section} title={title} />

      <div className="card profile-header">
        <div className="profile-header-avatar">SM</div>
        <div className="profile-header-info">
          <div className="profile-header-name">Suraj Mehta</div>
          <div className="profile-header-sub">B.Tech in Computer Engineering &middot; Student profile</div>
          <div className="profile-header-sub">Mumbai, Maharashtra, India</div>
          {missing.length > 0 && (
            <div className="profile-missing-row">
              {missing.map((m) => (
                <span className="badge badge-warning" key={m}>
                  {m}
                </span>
              ))}
            </div>
          )}
        </div>
        <button className="btn-secondary" type="button">
          Edit profile
        </button>
      </div>

      <div className="profile-layout">
        <aside className="profile-quicklinks card">
          <div className="label" style={{ marginBottom: 10 }}>
            Quick links
          </div>
          <nav className="profile-quicklinks-nav">
            {QUICK_LINKS.map(([id, label]) => (
              <a key={id} href={`#${id}`}>
                {label}
              </a>
            ))}
          </nav>
        </aside>

        <div className="profile-panels">
          <Panel id="preferences" icon={<DiamondIcon />} title="Your career preferences">
            <div className="profile-pref-grid">
              <div>
                <div className="label">Preferred work</div>
                <div className="profile-pref-value">Internships</div>
              </div>
              <div>
                <div className="label">Availability</div>
                <div className="profile-pref-value muted">Add work availability</div>
              </div>
              <div>
                <div className="label">Preferred location</div>
                <div className="profile-pref-value">Mumbai, Maharashtra, India</div>
              </div>
            </div>
          </Panel>

          <Panel id="education" icon={<GraduationCapIcon />} title="Education">
            <div className="profile-entry-list">
              {EDUCATION.map((e) => (
                <div className="profile-entry" key={e.course}>
                  <div className="profile-entry-title">
                    {e.type} in {e.course}
                  </div>
                  <div className="profile-entry-sub">{e.institution}</div>
                  <div className="profile-entry-meta">
                    {e.period} &middot; {e.output}
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel id="skills" icon={<BookOpenIcon />} title="Key skills">
            <div className="profile-skill-groups">
              {SKILL_GROUPS.map((g) => (
                <div key={g.field}>
                  <div className="profile-skill-group-label">{g.field}</div>
                  <div className="talent-skill-row">
                    {g.skills.map((s) => (
                      <span className="talent-skill-chip" key={s}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel id="languages" icon={<GlobeIcon />} title="Languages">
            <div className="profile-lang-list">
              {LANGUAGES.map((l) => (
                <div className="profile-lang-row" key={l.name}>
                  <span>{l.name}</span>
                  <span className="pill">{l.level}</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel id="internships" icon={<BriefcaseIcon />} title="Internships">
            {INTERNSHIPS.length ? (
              <div className="profile-entry-list">
                {INTERNSHIPS.map((i) => (
                  <div className="profile-entry" key={i.role}>
                    <div className="profile-entry-title">{i.role}</div>
                    <div className="profile-entry-sub">{i.company}</div>
                    <div className="profile-entry-meta">{i.period}</div>
                    <ul className="profile-bullet-list">
                      {i.points.map((p) => (
                        <li key={p}>{p}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ) : (
              <Empty text="Add an internship to show your work experience." />
            )}
          </Panel>

          <Panel id="projects" icon={<ToolIcon />} title="Projects">
            <div className="profile-entry-list">
              {PROJECTS.map((p) => (
                <div className="profile-entry" key={p.name}>
                  <div className="profile-entry-title">{p.name}</div>
                  <div className="profile-entry-meta">{p.stack}</div>
                  <p className="profile-entry-desc">{p.desc}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel id="summary" icon={<EditIcon />} title="Profile summary">
            <p className="profile-entry-desc">
              Computer Engineering student passionate about building reliable full-stack products. Comfortable
              across the stack from React UIs to Python-based ML pipelines, with a growing interest in fraud
              detection and trust & safety systems.
            </p>
          </Panel>

          <Panel id="accomplishments" icon={<AwardIcon />} title="Accomplishments">
            <div className="profile-entry-list">
              {CERTIFICATIONS.map((c) => (
                <div className="profile-entry" key={c.name}>
                  <div className="profile-entry-title">{c.name}</div>
                  <div className="profile-entry-meta">
                    {c.issuer} &middot; {c.year}
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </>
  );
}
