// Sidebar nav structure per portal — mirrors ifind's actual left-nav
// grouping (Internships / Tools / System for the student portal, etc),
// restyled in cream/black instead of ifind's dark theme.

export const SIDEBAR_NAV = {
  user: [
    { group: null, items: [{ label: "Home", to: "overview" }] },
    {
      group: "Internships",
      items: [
        { label: "Browse", to: "browse" },
        { label: "Applied", to: "applied-internships" },
        { label: "Saved", to: "saved" },
      ],
    },
    {
      group: "Tools",
      items: [
        { label: "Resume Analyzer", to: "resume" },
        { label: "Career Assistant", to: "career" },
        { label: "Chat", to: "chat" },
      ],
    },
    {
      group: "System",
      items: [
        { label: "Profile", to: "profile" },
        { label: "Settings", to: "settings" },
        { label: "Notifications", to: "notifications" },
      ],
    },
  ],
  employer: [
    { group: null, items: [{ label: "Home", to: "overview" }] },
    {
      group: "Company",
      items: [
        { label: "Internships", to: "internships" },
        { label: "Post New Internship", to: "post-new-internship" },
        { label: "Applicants", to: "applicants" },
        { label: "Team", to: "team" },
      ],
    },
    {
      group: "System",
      items: [
        { label: "Settings", to: "settings" },
      ],
    },
  ],
  moderator: [
    { group: null, items: [{ label: "Home", to: "" }] },
    {
      group: "Queue",
      items: [
        { label: "Internships", to: "internships" },
        { label: "Scrapes", to: "scrapes" },
        { label: "Users", to: "users" },
        { label: "Moderators", to: "moderators" },
      ],
    },
  ],
};

export const PORTAL_LABEL = { user: "Student", employer: "Employer", moderator: "Moderator" };
