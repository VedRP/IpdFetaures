import {
  SendIcon,
  BookmarkIcon,
  StarIcon,
  UserIcon,
  BriefcaseIcon,
  InboxIcon,
  UsersIcon,
  CheckIcon,
  GraduationCapIcon,
  RefreshIcon,
  FlagIcon,
  ShieldIcon,
} from "../components/Icon";
import PageHeader from "../components/PageHeader";
import { accentColor } from "../accentColors";

const OVERVIEW_COPY = {
  user: {
    cardLabel: "Your talent card",
    cardSub: "Your talent card is visible to employers only when you are actively interviewing",
    name: "Suraj Mehta",
    metaLines: ["Can join immediately", "Bengaluru, Karnataka, India", "Dwarkadas J. Sanghvi College of Engineering"],
    skills: ["C", "C++", "Java", "Python", "NumPy", "Node.js", "React"],
    stats: [
      { Icon: SendIcon, color: "var(--color-tag-blue)", value: 5, label: "Applied" },
      { Icon: BookmarkIcon, color: "var(--color-tag-purple)", value: 4, label: "Saved" },
      { Icon: StarIcon, color: "var(--color-tag-green)", value: 0, label: "Shortlisted" },
      { Icon: UserIcon, color: "var(--color-tag-amber)", value: "100%", label: "Profile" },
    ],
    checklist: ["Add profile photo", "Upload resume", "Resume has skills", "Resume has education", "Add phone number"],
    gridLabel: "Best internships for you",
    grid: [
      { code: "A", role: "Software Development", company: "Anakin · via Web", loc: "India · ₹20,000/mo" },
      { code: "G", role: "Full Stack Development", company: "Gateway Software Solutions", loc: "India · ₹6,500/mo" },
      { code: "A", role: "Flutter Development", company: "Adigos Technologies LLP", loc: "India · ₹5,000/mo" },
    ],
  },
  employer: {
    cardLabel: "Your company card",
    cardSub: "Visible to students once your company is verified",
    name: "Veridex Labs",
    metaLines: ["Verified employer", "Bengaluru, Karnataka, India", "4 active internship postings"],
    skills: ["Robotics", "Embedded Systems", "AI/ML", "Hiring now"],
    stats: [
      { Icon: BriefcaseIcon, color: "var(--color-tag-blue)", value: 4, label: "Open roles" },
      { Icon: InboxIcon, color: "var(--color-tag-purple)", value: 12, label: "Applicants" },
      { Icon: UsersIcon, color: "var(--color-tag-green)", value: 3, label: "Team" },
      { Icon: CheckIcon, color: "var(--color-tag-amber)", value: "Yes", label: "Verified" },
    ],
    checklist: ["Add company logo", "Verify domain", "Post first internship", "Invite teammate", "Add billing details"],
    gridLabel: "Recent applicants",
    grid: [
      { code: "A", role: "Ananya Rao", company: "Applied 2 days ago", loc: "Resume attached" },
      { code: "D", role: "Dev Patel", company: "Applied 4 days ago", loc: "Shortlisted" },
      { code: "M", role: "Meera Iyer", company: "Applied 1 week ago", loc: "Interview scheduled" },
    ],
  },
  moderator: {
    cardLabel: "Queue summary",
    cardSub: "Pending items across internships, scrapes, and user reports",
    name: "Moderator desk",
    metaLines: ["18 internships pending review", "3 scrape jobs running", "2 user reports open"],
    skills: ["Scam detector", "Rules engine", "Reputation store"],
    stats: [
      { Icon: GraduationCapIcon, color: "var(--color-tag-blue)", value: 18, label: "Internships" },
      { Icon: RefreshIcon, color: "var(--color-tag-purple)", value: 3, label: "Scrapes" },
      { Icon: FlagIcon, color: "var(--color-tag-green)", value: 2, label: "User reports" },
      { Icon: ShieldIcon, color: "var(--color-tag-amber)", value: 2, label: "Moderators" },
    ],
    checklist: ["Review flagged internships", "Approve pending scrapes", "Resolve user reports", "Weekly audit", "Sync reputation store"],
    gridLabel: "Latest scrape jobs",
    grid: [
      { code: "J1", role: "job-001 · internshala", company: "Completed", loc: "212 records" },
      { code: "J2", role: "job-002 · naukri", company: "Running", loc: "64 records so far" },
      { code: "J3", role: "job-003 · freshersworld", company: "Queued", loc: "—" },
    ],
  },
};

export default function Overview({ portal, section = "01", title = "Overview" }) {
  const c = OVERVIEW_COPY[portal] ?? OVERVIEW_COPY.user;

  return (
    <>
      <PageHeader step={section} title={title} />

      <div className="label" style={{ marginBottom: 10 }}>
        {c.cardLabel}
      </div>
      <p style={{ marginTop: -4, marginBottom: 10, fontSize: 12, color: "var(--color-ink-soft)" }}>{c.cardSub}</p>

      <div className="card">
        <div className="talent-card">
          <div className="talent-card-main">
            <div className="talent-avatar">{c.name.charAt(0)}</div>
            <div>
              <div className="talent-name">{c.name.toUpperCase()}</div>
              {c.metaLines.map((line) => (
                <div className="talent-meta-row" key={line}>
                  {line}
                </div>
              ))}
              <div className="talent-skill-row">
                {c.skills.map((s) => (
                  <span className="talent-skill-chip" key={s}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <button className="btn-secondary" type="button">
            Edit
          </button>
        </div>
      </div>

      <div className="stat-tile-row">
        {c.stats.map((s) => (
          <div className="stat-tile" key={s.label} style={{ "--stat-color": s.color }}>
            <div className="stat-icon" style={{ background: s.color }}>
              <s.Icon width={17} height={17} />
            </div>
            <div className="stat-text">
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="breadcrumb" style={{ marginBottom: 4 }}>
          <span className="path">Profile completion</span>
          <span className="status" style={{ color: "var(--color-ink)" }}>
            100%
          </span>
        </div>
        <div className="mini-progress" style={{ background: "var(--color-border)" }}>
          <div className="mini-progress-fill" style={{ background: "var(--color-ink)", width: "100%" }} />
        </div>
        <ul className="checklist">
          {c.checklist.map((item) => (
            <li key={item}>
              <span className="checklist-check">
                <CheckIcon width={11} height={11} />
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="label" style={{ margin: "22px 0 12px" }}>
        {c.gridLabel}
      </div>
      <div className="internship-grid">
        {c.grid.map((item) => (
          <div className="internship-tile" key={item.role}>
            <div className="internship-tile-top">
              <div className="internship-logo" style={{ background: accentColor(item.role) }}>
                {item.code}
              </div>
              <div>
                <div className="role">{item.role}</div>
                <div className="company">{item.company}</div>
              </div>
            </div>
            <div className="loc">{item.loc}</div>
            <span className="pill">View</span>
          </div>
        ))}
      </div>
    </>
  );
}
