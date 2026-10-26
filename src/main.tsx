import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { LanguageProvider } from './locales'
import './index.css'
import App from './App.tsx'
import { AuthGate } from './components/AuthGate'
import { LayoutMetricsSync } from './utils/layoutMetricsSync'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LanguageProvider>
      <AuthGate>
        <App />
      </AuthGate>
      {/* Attribution footer from the original Cheat Clip Pro, kept on every screen */}
      <div className="app-footer-shell">
        <LayoutMetricsSync />
      </div>
    </LanguageProvider>
  </StrictMode>,
)
