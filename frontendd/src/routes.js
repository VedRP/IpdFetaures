// Route map mirroring IPD-All/ifind's page structure 1:1 (student/user,
// employer, moderator portals). Every path below matches the folder path
// of the corresponding `page.tsx` in ifind's `app/` directory.
//
// This is a pure frontend restyle — no API calls, no backend connection.
// `kind` selects which shared page shell renders that route; dynamic
// segments (:username, :companyId, :internshipId, :jobId) are filled with
// fixed demo values by the nav links below so the UI is fully clickable.

export const DEMO = {
  username: "suraj",
  companyId: "demo-co",
  internshipId: "demo-intern",
  jobId: "job-001",
};

export const ROUTES = [
  { path: "/", section: "00", title: "Portal Select", kind: "home" },

  // ---------------------------------------------------------------- user
  { path: "/user/login", section: "USER", title: "Sign In", kind: "auth", portal: "user", mode: "login" },
  { path: "/user/register", section: "USER", title: "Register", kind: "auth", portal: "user", mode: "register" },
  { path: "/user/:username/overview", section: "01", title: "Overview", kind: "dashboard", portal: "user" },
  { path: "/user/:username/browse", section: "02", title: "Browse Internships", kind: "browse", portal: "user" },
  { path: "/user/:username/applied-internships", section: "03", title: "Applied Internships", kind: "list", portal: "user", items: "applications" },
  { path: "/user/:username/applied-internships/:internshipId", section: "03", title: "Application Detail", kind: "detail", portal: "user" },
  { path: "/user/:username/saved", section: "04", title: "Saved Internships", kind: "list", portal: "user", items: "internships" },
  { path: "/user/:username/internship-match", section: "05", title: "Internship Match", kind: "detail", portal: "user" },
  { path: "/user/:username/career", section: "06", title: "Career Assistant", kind: "detail", portal: "user" },
  { path: "/user/:username/chat", section: "07", title: "Chat", kind: "detail", portal: "user" },
  { path: "/user/:username/resume", section: "08", title: "Resume", kind: "detail", portal: "user" },
  { path: "/user/:username/notifications", section: "09", title: "Notifications", kind: "list", portal: "user", items: "notifications" },
  { path: "/user/:username/profile", section: "10", title: "Profile", kind: "profile", portal: "user" },
  { path: "/user/:username/settings", section: "11", title: "Settings", kind: "detail", portal: "user" },

  // ------------------------------------------------------------ employer
  { path: "/employer/login", section: "EMPLOYER", title: "Sign In", kind: "auth", portal: "employer", mode: "login" },
  { path: "/employer/register", section: "EMPLOYER", title: "Register", kind: "auth", portal: "employer", mode: "register" },
  { path: "/employer/companies", section: "01", title: "Companies", kind: "companies", portal: "employer" },
  { path: "/employer/companies/new", section: "01", title: "New Company", kind: "detail", portal: "employer" },
  { path: "/employer/company/:companyId/overview", section: "02", title: "Company Overview", kind: "dashboard", portal: "employer" },
  { path: "/employer/company/:companyId/internships", section: "03", title: "Internships", kind: "list", portal: "employer", items: "internships" },
  { path: "/employer/company/:companyId/internships/:internshipId/overview", section: "03", title: "Internship Overview", kind: "detail", portal: "employer" },
  { path: "/employer/company/:companyId/internships/:internshipId/internship-details", section: "03", title: "Internship Details", kind: "detail", portal: "employer" },
  { path: "/employer/company/:companyId/internships/:internshipId/students-applied", section: "03", title: "Students Applied", kind: "list", portal: "employer", items: "applicants" },
  { path: "/employer/company/:companyId/internships/:internshipId/applicants", section: "03", title: "Applicants", kind: "list", portal: "employer", items: "applicants" },
  { path: "/employer/company/:companyId/internships/:internshipId/settings", section: "03", title: "Internship Settings", kind: "detail", portal: "employer" },
  { path: "/employer/company/:companyId/post-new-internship", section: "04", title: "Post New Internship", kind: "detail", portal: "employer" },
  { path: "/employer/company/:companyId/applicants", section: "05", title: "All Applicants", kind: "list", portal: "employer", items: "applicants" },
  { path: "/employer/company/:companyId/team", section: "06", title: "Team", kind: "list", portal: "employer", items: "team" },
  { path: "/employer/company/:companyId/settings", section: "07", title: "Company Settings", kind: "detail", portal: "employer" },
  { path: "/employer/notifications", section: "08", title: "Notifications", kind: "list", portal: "employer", items: "notifications" },
  { path: "/employer/profile", section: "09", title: "Profile", kind: "detail", portal: "employer" },
  { path: "/employer/settings", section: "10", title: "Account Settings", kind: "detail", portal: "employer" },

  // ----------------------------------------------------------- moderator
  { path: "/moderator/login", section: "MODERATOR", title: "Sign In", kind: "auth", portal: "moderator", mode: "login" },
  { path: "/moderator/register", section: "MODERATOR", title: "Register", kind: "auth", portal: "moderator", mode: "register" },
  { path: "/moderator/pending", section: "MODERATOR", title: "Approval Pending", kind: "detail", portal: "moderator" },
  { path: "/moderator/:username", section: "01", title: "Overview", kind: "dashboard", portal: "moderator" },
  { path: "/moderator/:username/internships", section: "02", title: "Internship Queue", kind: "mod-queue", portal: "moderator" },
  { path: "/moderator/:username/scrapes", section: "03", title: "Scrape Jobs", kind: "list", portal: "moderator", items: "scrapes" },
  { path: "/moderator/:username/scrapes/:jobId", section: "03", title: "Scrape Job Detail", kind: "detail", portal: "moderator" },
  { path: "/moderator/:username/users", section: "04", title: "Users", kind: "list", portal: "moderator", items: "users" },
  { path: "/moderator/:username/moderators", section: "05", title: "Moderators", kind: "list", portal: "moderator", items: "moderators" },
];

export function resolveDemoPath(path) {
  return path
    .replace(":username", DEMO.username)
    .replace(":companyId", DEMO.companyId)
    .replace(":internshipId", DEMO.internshipId)
    .replace(":jobId", DEMO.jobId);
}
