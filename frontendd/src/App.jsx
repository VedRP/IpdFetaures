import { BrowserRouter, Routes, Route } from "react-router-dom";
import PortalShell from "./components/PortalShell";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import Overview from "./pages/Overview";
import Browse from "./pages/user/Browse";
import Profile from "./pages/user/Profile";
import ListPage from "./pages/ListPage";
import DetailStub from "./pages/DetailStub";
import NotFound from "./pages/NotFound";
import Companies from "./pages/employer/Companies";
import InternshipQueue from "./pages/moderator/InternshipQueue";
import { ROUTES } from "./routes";

function renderRoute(route) {
  switch (route.kind) {
    case "home":
      return <Home />;
    case "auth":
      return <Auth portal={route.portal} mode={route.mode} />;
    case "dashboard":
      return (
        <PortalShell portal={route.portal}>
          <Overview portal={route.portal} section={route.section} title={route.title} />
        </PortalShell>
      );
    case "browse":
      return (
        <PortalShell portal={route.portal}>
          <Browse section={route.section} title={route.title} />
        </PortalShell>
      );
    case "profile":
      return (
        <PortalShell portal={route.portal}>
          <Profile section={route.section} title={route.title} />
        </PortalShell>
      );
    case "list":
      return (
        <PortalShell portal={route.portal}>
          <ListPage portal={route.portal} section={route.section} title={route.title} items={route.items} />
        </PortalShell>
      );
    case "companies":
      return (
        <PortalShell portal={route.portal}>
          <Companies section={route.section} title={route.title} />
        </PortalShell>
      );
    case "mod-queue":
      return (
        <PortalShell portal={route.portal}>
          <InternshipQueue section={route.section} title={route.title} />
        </PortalShell>
      );
    default:
      return (
        <PortalShell portal={route.portal}>
          <DetailStub portal={route.portal} section={route.section} title={route.title} />
        </PortalShell>
      );
  }
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {ROUTES.map((route) => (
          <Route key={route.path} path={route.path} element={renderRoute(route)} />
        ))}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
