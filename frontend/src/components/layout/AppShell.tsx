import type { ReactNode } from 'react'
export default function AppShell({children}:{children:ReactNode}) {
  return <div className="app-shell">{children}</div>
}
