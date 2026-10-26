import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { Eye, EyeOff, Lock } from 'lucide-react';
import { useLanguage } from '../locales';

type Status = 'checking' | 'locked' | 'open';

/**
 * Shows a password screen when the server has APP_PASSWORD set.
 * Any later 401 from /api (expired session) brings the screen back.
 */
export function AuthGate({ children }: { children: ReactNode }) {
  const { language } = useLanguage();
  const [status, setStatus] = useState<Status>('checking');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const id = language === 'id';

  useEffect(() => {
    fetch('/api/auth/status', { credentials: 'same-origin' })
      .then(res => (res.ok ? res.json() : { required: false, authenticated: true }))
      .then(data => setStatus(data.required && !data.authenticated ? 'locked' : 'open'))
      .catch(() => setStatus('open'));

    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const res = await originalFetch(...args);
      const url = typeof args[0] === 'string' ? args[0] : args[0] instanceof URL ? args[0].href : args[0].url;
      if (res.status === 401 && url.includes('/api/') && !url.includes('/api/auth/')) {
        setStatus('locked');
      }
      return res;
    };
    return () => { window.fetch = originalFetch; };
  }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ password }),
      });
      if (res.ok) {
        setPassword('');
        setStatus('open');
        return;
      }
      if (res.status === 429) setError(id ? 'Terlalu banyak percobaan. Coba lagi beberapa menit lagi.' : 'Too many attempts. Try again in a few minutes.');
      else setError(id ? 'Password salah.' : 'Wrong password.');
    } catch {
      setError(id ? 'Tidak bisa terhubung ke server.' : 'Cannot reach the server.');
    } finally {
      setSubmitting(false);
    }
  };

  if (status === 'checking') return <div className="auth-screen" aria-busy="true" />;
  if (status === 'open') return <>{children}</>;

  return (
    <div className="auth-screen">
      <form className="auth-card" onSubmit={submit}>
        <svg width="44" height="44" viewBox="0 0 64 64" aria-hidden="true" className="logo-mark">
          <defs>
            <linearGradient id="auth-logo-grad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#a9c7ff" />
              <stop offset=".55" stopColor="#3d7bff" />
              <stop offset="1" stopColor="#1b3fb8" />
            </linearGradient>
          </defs>
          <path d="M20 15.5c0-2.3 2.5-3.7 4.5-2.5l26 15.8c1.9 1.1 1.9 3.9 0 5L24.5 51c-2 1.2-4.5-.2-4.5-2.5z" fill="url(#auth-logo-grad)" />
          <path d="M12 38.5 52 23.5" stroke="#04060d" strokeWidth="5" strokeLinecap="round" />
        </svg>
        <h1 className="auth-title">Clipper Hub <span className="logo-accent">Cheat Pro</span></h1>
        <p className="auth-sub">{id ? 'Masukkan password untuk melanjutkan.' : 'Enter the password to continue.'}</p>
        <label className="auth-field">
          <Lock size={16} />
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Password"
            autoComplete="current-password"
            autoFocus
            required
          />
          <button type="button" onClick={() => setShowPassword(v => !v)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </label>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button type="submit" className="glowing-btn auth-submit" disabled={submitting || !password}>
          {submitting ? (id ? 'Memeriksa...' : 'Checking...') : (id ? 'Masuk' : 'Sign in')}
        </button>
      </form>
    </div>
  );
}
