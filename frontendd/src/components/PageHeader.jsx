export default function PageHeader({ step, title, status = "SYSTEM READY" }) {
  return (
    <div className="breadcrumb breadcrumb-page">
      <span className="path">
        {step} / {title}
      </span>
      <span className="status">● {status}</span>
    </div>
  );
}
