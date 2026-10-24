import { Link } from "react-router-dom";
import Logo from "../components/Logo";

export default function NotFound() {
  return (
    <div className="not-found-page">
      <Logo size="lg" />
      <div className="not-found-code">404</div>
      <h1>Page not found</h1>
      <p>The page you're looking for doesn't exist in this demo, or the link is out of date.</p>
      <Link to="/" className="btn-primary not-found-home">
        <span>Back to home</span>
        <span>&rarr;</span>
      </Link>
    </div>
  );
}
