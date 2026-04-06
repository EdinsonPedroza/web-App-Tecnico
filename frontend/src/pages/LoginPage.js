import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { GraduationCap, User, Eye, EyeOff, Loader2, Facebook } from 'lucide-react';
import { getErrorMessage } from '@/utils/errorUtils';

const LOGO = process.env.PUBLIC_URL + '/logo.png';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState('estudiante');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [fieldKey, setFieldKey] = useState(0);
  const [form, setForm] = useState({ email: '', cedula: '', password: '' });

  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setFieldKey(k => k + 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const credentials = {
        role,
        password: form.password,
        ...(role === 'estudiante' ? { cedula: form.cedula } : { email: form.email })
      };
      const userData = await login(credentials);
      toast.success(`¡Bienvenido, ${userData.name}!`);
      if (userData.role === 'editor') navigate('/editor');
      else if (userData.role === 'admin') navigate('/admin');
      else if (userData.role === 'profesor') navigate('/teacher');
      else navigate('/student');
    } catch (err) {
      toast.error(getErrorMessage(err, 'Error de autenticación'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @keyframes lp-gradient {
          0%   { background-position: 0% 50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes lp-float {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(-14px); }
        }
        @keyframes lp-float-slow {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(10px); }
        }
        @keyframes lp-glow {
          0%, 100% { opacity: 0.5; transform: scale(1); }
          50%       { opacity: 0.85; transform: scale(1.1); }
        }
        @keyframes lp-spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes lp-spin-rev {
          from { transform: rotate(0deg); }
          to   { transform: rotate(-360deg); }
        }
        @keyframes lp-twinkle {
          0%, 100% { opacity: 0.2; }
          50%       { opacity: 0.8; }
        }
        @keyframes lp-shimmer {
          0%   { background-position: -200% center; }
          100% { background-position:  200% center; }
        }
        @keyframes lp-field {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .lp-bg {
          background: linear-gradient(135deg, #0f3460 0%, #1a5fa8 30%, #2176c7 55%, #1a4e8c 80%, #0f3460 100%);
          background-size: 300% 300%;
          animation: lp-gradient 10s ease infinite;
        }
        .lp-glow-ring { animation: lp-glow 3.5s ease-in-out infinite; }
        .lp-float     { animation: lp-float 4s ease-in-out infinite; }
        .lp-float-slow{ animation: lp-float-slow 5.5s ease-in-out infinite; }
        .lp-spin       { animation: lp-spin 20s linear infinite; }
        .lp-spin-rev   { animation: lp-spin-rev 14s linear infinite; }

        .lp-field-enter { animation: lp-field 0.28s ease both; }

        .lp-btn {
          position: relative; overflow: hidden;
          transition: transform 0.18s ease, box-shadow 0.18s ease;
        }
        .lp-btn::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.22) 50%, transparent 65%);
          background-size: 200% 100%;
          opacity: 0;
        }
        .lp-btn:not(:disabled):hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(26,95,168,0.4); }
        .lp-btn:not(:disabled):hover::after { opacity: 1; animation: lp-shimmer 0.6s linear; }
        .lp-btn:not(:disabled):active { transform: translateY(0); }

        .lp-fb {
          transition: background 0.2s, transform 0.18s, box-shadow 0.18s;
          position: relative; overflow: hidden;
        }
        .lp-fb:hover { background: #145dbf !important; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(24,119,242,0.4); }

        .lp-input { transition: border-color 0.2s, box-shadow 0.2s; }
        .lp-input:focus { box-shadow: 0 0 0 3px rgba(33,118,199,0.15); }
      `}</style>

      <div className="min-h-screen flex">

        {/* ══════════ LEFT — Branding ══════════ */}
        <div className="hidden lg:flex lg:w-1/2 relative lp-bg items-center justify-center overflow-hidden">

          {/* Dot grid */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px)',
              backgroundSize: '32px 32px',
            }}
          />

          {/* Scattered star particles */}
          {[
            { t: '7%',  l: '11%', d: '0s',   s: '2.8s' },
            { t: '14%', l: '72%', d: '0.6s',  s: '3.5s' },
            { t: '31%', l: '87%', d: '1.2s',  s: '4s'   },
            { t: '52%', l: '5%',  d: '1.9s',  s: '3.2s' },
            { t: '66%', l: '58%', d: '0.4s',  s: '4.5s' },
            { t: '78%', l: '25%', d: '2.1s',  s: '3.8s' },
            { t: '88%', l: '78%', d: '0.9s',  s: '2.6s' },
            { t: '44%', l: '42%', d: '1.5s',  s: '5s'   },
          ].map((p, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-white"
              style={{ top: p.t, left: p.l, width: 3, height: 3, animation: `lp-twinkle ${p.s} ease-in-out ${p.d} infinite` }}
            />
          ))}

          {/* Floating blobs */}
          <div className="lp-float absolute -top-16 -left-16 w-72 h-72 rounded-full blur-3xl bg-white/10" />
          <div className="lp-float-slow absolute -bottom-20 -right-12 w-80 h-80 rounded-full blur-3xl bg-white/8" />

          {/* Rotating rings — corners */}
          <div className="absolute top-8 right-8 lp-spin" style={{ width: 90, height: 90 }}>
            <svg viewBox="0 0 90 90" fill="none"><circle cx="45" cy="45" r="43" stroke="rgba(255,255,255,0.22)" strokeWidth="1.2" strokeDasharray="9 5"/></svg>
          </div>
          <div className="absolute bottom-8 left-8 lp-spin-rev" style={{ width: 110, height: 110 }}>
            <svg viewBox="0 0 110 110" fill="none"><circle cx="55" cy="55" r="53" stroke="rgba(255,255,255,0.18)" strokeWidth="1.2" strokeDasharray="11 6"/></svg>
          </div>

          {/* Inline educational illustration — books + graduation cap */}
          <div className="absolute bottom-0 left-0 right-0 pointer-events-none" style={{ opacity: 0.13 }}>
            <svg viewBox="0 0 800 220" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax meet">
              {/* Open book left */}
              <rect x="40" y="100" width="90" height="110" rx="4" fill="white"/>
              <rect x="40" y="100" width="45" height="110" rx="4" fill="white"/>
              <line x1="85" y1="100" x2="85" y2="210" stroke="rgba(255,255,255,0.6)" strokeWidth="2"/>
              <rect x="50" y="116" width="26" height="4" rx="2" fill="rgba(255,255,255,0.5)"/>
              <rect x="50" y="126" width="20" height="4" rx="2" fill="rgba(255,255,255,0.4)"/>
              <rect x="50" y="136" width="24" height="4" rx="2" fill="rgba(255,255,255,0.4)"/>
              <rect x="95" y="116" width="26" height="4" rx="2" fill="rgba(255,255,255,0.5)"/>
              <rect x="95" y="126" width="20" height="4" rx="2" fill="rgba(255,255,255,0.4)"/>
              <rect x="95" y="136" width="24" height="4" rx="2" fill="rgba(255,255,255,0.4)"/>
              {/* Stack of books middle */}
              <rect x="260" y="155" width="120" height="18" rx="3" fill="white"/>
              <rect x="268" y="137" width="104" height="18" rx="3" fill="white"/>
              <rect x="256" y="119" width="116" height="18" rx="3" fill="white"/>
              {/* Graduation cap */}
              <polygon points="580,80 640,100 580,120 520,100" fill="white"/>
              <rect x="576" y="100" width="8" height="40" rx="2" fill="white"/>
              <circle cx="580" cy="142" r="8" fill="white"/>
              <line x1="640" y1="100" x2="640" y2="128" stroke="white" strokeWidth="3"/>
              <circle cx="640" cy="132" r="5" fill="white"/>
              {/* Pencil right */}
              <rect x="700" y="60" width="14" height="120" rx="3" transform="rotate(-15 700 60)" fill="white"/>
              <polygon points="698,180 712,180 705,200" transform="rotate(-15 705 180)" fill="white"/>
            </svg>
          </div>

          {/* ── Branding content ── */}
          <div className="relative z-10 text-center px-12 max-w-sm">
            {/* Logo */}
            <div className="mb-7 flex justify-center">
              <div className="relative">
                <div className="lp-glow-ring absolute rounded-full blur-2xl bg-white/25" style={{ inset: '-10px' }} />
                <div className="lp-spin absolute rounded-full" style={{ inset: '-18px' }}>
                  <svg viewBox="0 0 176 176" fill="none" style={{ width: '100%', height: '100%' }}>
                    <circle cx="88" cy="88" r="86" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" strokeDasharray="12 7"/>
                  </svg>
                </div>
                <img
                  src={LOGO}
                  alt="Corporación Social Educando"
                  className="relative rounded-full object-cover shadow-2xl"
                  style={{ width: 140, height: 140, border: '3px solid rgba(255,255,255,0.35)' }}
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              </div>
            </div>

            <h1 className="text-2xl font-bold font-heading text-white mb-2 leading-snug">
              Corporación Social Educando
            </h1>
            <p className="text-white/70 text-sm leading-relaxed">
              Llegamos a los rincones donde la educación no llega
            </p>
          </div>
        </div>

        {/* ══════════ RIGHT — Login ══════════ */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-background">
          <div className="w-full max-w-md">

            {/* Mobile logo */}
            <div className="lg:hidden flex flex-col items-center mb-8">
              <img src={LOGO} alt="Logo" className="h-20 w-20 rounded-full mb-3 object-cover" onError={(e) => { e.target.style.display = 'none'; }} />
              <p className="text-base font-bold font-heading text-foreground">Educando</p>
            </div>

            <Card
              className="border border-border/50 rounded-2xl overflow-hidden"
              style={{ boxShadow: '0 24px 64px -12px rgba(0,0,0,0.10), 0 4px 16px -4px rgba(26,95,168,0.08)' }}
            >
              {/* Top accent */}
              <div className="h-[3px] lp-bg" />

              <CardContent className="p-8">
                {/* Header */}
                <div className="text-center mb-6">
                  <div
                    className="inline-flex items-center justify-center w-11 h-11 rounded-xl mb-4"
                    style={{ background: 'hsl(var(--primary)/0.08)' }}
                  >
                    <GraduationCap className="h-5 w-5" style={{ color: 'hsl(var(--primary))' }} />
                  </div>
                  <h2 className="text-xl font-bold font-heading text-foreground">Iniciar Sesión</h2>
                  <p className="text-sm text-muted-foreground mt-1">Accede a tu plataforma educativa</p>
                </div>

                {/* Tabs */}
                <Tabs value={role} onValueChange={handleRoleChange} className="mb-5">
                  <TabsList className="grid w-full grid-cols-2 rounded-xl h-10">
                    <TabsTrigger value="estudiante" className="rounded-lg text-sm gap-1.5">
                      <GraduationCap className="h-3.5 w-3.5" />
                      Estudiante
                    </TabsTrigger>
                    <TabsTrigger value="profesor" className="rounded-lg text-sm gap-1.5">
                      <User className="h-3.5 w-3.5" />
                      Profesor
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Dynamic field */}
                  <div key={fieldKey} className="lp-field-enter space-y-1.5">
                    {role === 'estudiante' ? (
                      <>
                        <Label htmlFor="cedula" className="text-sm font-medium">Cédula</Label>
                        <Input
                          id="cedula"
                          inputMode="numeric"
                          placeholder="Ej: 12345678 (solo números)"
                          value={form.cedula}
                          onChange={(e) => setForm({ ...form, cedula: e.target.value })}
                          className="lp-input h-10 rounded-lg"
                          required
                        />
                      </>
                    ) : (
                      <>
                        <Label htmlFor="email" className="text-sm font-medium">Correo Electrónico</Label>
                        <Input
                          id="email"
                          type="email"
                          placeholder="correo@educando.com"
                          value={form.email}
                          onChange={(e) => setForm({ ...form, email: e.target.value })}
                          className="lp-input h-10 rounded-lg"
                          required
                        />
                      </>
                    )}
                  </div>

                  {/* Password */}
                  <div className="space-y-1.5">
                    <Label htmlFor="password" className="text-sm font-medium">Contraseña</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={(e) => setForm({ ...form, password: e.target.value })}
                        className="lp-input h-10 rounded-lg pr-10"
                        required
                      />
                      <button
                        type="button"
                        tabIndex={-1}
                        onClick={() => setShowPassword(v => !v)}
                        className="absolute right-0 top-0 h-full w-10 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="lp-btn w-full h-10 rounded-lg font-semibold text-sm"
                    disabled={loading}
                  >
                    {loading
                      ? <><Loader2 className="h-4 w-4 animate-spin mr-2" />Ingresando...</>
                      : 'Ingresar'
                    }
                  </Button>
                </form>

                {/* Divider */}
                <div className="flex items-center gap-3 my-5">
                  <div className="flex-1 h-px bg-border/50" />
                  <span className="text-xs text-muted-foreground">Síguenos</span>
                  <div className="flex-1 h-px bg-border/50" />
                </div>

                {/* Facebook */}
                <a
                  href="https://www.facebook.com/share/1HmbmUyj4p/?mibextid=wwXIfr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="lp-fb flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-lg text-white font-medium text-sm"
                  style={{ background: '#1877f2' }}
                >
                  <Facebook className="h-4 w-4" />
                  Síguenos en Facebook
                </a>
              </CardContent>
            </Card>
          </div>
        </div>

      </div>
    </>
  );
}
