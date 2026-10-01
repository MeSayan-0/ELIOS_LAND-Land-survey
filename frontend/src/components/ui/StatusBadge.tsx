export default function StatusBadge({ label, tone='pending' }: {label:string; tone?:'ok'|'pending'|'danger'}) {
  return <span className={`status-${tone}`}>{label}</span>
}
