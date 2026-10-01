import type { ReactNode } from 'react'
export default function SectionHeader({title, subtitle, action}: {title:string; subtitle?:string; action?:ReactNode}) {
  return <div className="panel-head"><div><b>{title}</b>{subtitle && <span>{subtitle}</span>}</div>{action}</div>
}
