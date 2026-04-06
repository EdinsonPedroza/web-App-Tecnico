import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { GraduationCap, User, Eye, EyeOff, Loader2, Facebook, BookOpen, Award, Wifi } from 'lucide-react';
import { getErrorMessage } from '@/utils/errorUtils';

// Pre-defined particles so they don't shift on re-render
const PARTICLES = [
  { id: 0,  top: '8%',  left: '12%', delay: '0s',    dur: '3.2s', size: 3 },
  { id: 1,  top: '15%', left: '75%', delay: '0.5s',  dur: '4s',   size: 2 },
  { id: 2,  top: '25%', left: '40%', delay: '1.1s',  dur: '3.5s', size: 2 },
  { id: 3,  top: '35%', left: '88%', delay: '0.3s',  dur: '5s',   size: 3 },
  { id: 4,  top: '48%', left: '6%',  delay: '1.8s',  dur: '3.8s', size: 2 },
  { id: 5,  top: '55%', left: '55%', delay: '0.7s',  dur: '4.2s', size: 2 },
  { id: 6,  top: '62%', left: '22%', delay: '2s',    dur: '3s',   size: 3 },
  { id: 7,  top: '70%', left: '80%', delay: '1.4s',  dur: '4.5s', size: 2 },
  { id: 8,  top: '80%', left: '35%', delay: '0.9s',  dur: '3.7s', size: 2 },
  { id: 9,  top: '88%', left: '65%', delay: '1.6s',  dur: '4.8s', size: 3 },
  { id: 10, top: '5%',  left: '50%', delay: '2.3s',  dur: '3.3s', size: 2 },
  { id: 11, top: '42%', left: '93%', delay: '0.4s',  dur: '5.2s', size: 2 },
  { id: 12, top: '92%', left: '10%', delay: '1.2s',  dur: '3.6s', size: 3 },
  { id: 13, top: '18%', left: '28%', delay: '2.8s',  dur: '4.1s', size: 2 },
  { id: 14, top: '73%', left: '48%', delay: '0.6s',  dur: '3.9s', size: 2 },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState('estudiante');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [fieldKey, setFieldKey] = useState(0); // triggers re-animation on tab change
  const [mounted, setMounted] = useState(false);

  const [form, setForm] = useState({ email: '', cedula: '', password: '' });

  useEffect(() => {
    // Slight delay to trigger entrance animations after mount
    const t = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(t);
  }, []);

  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setFieldKey(k => k + 1); // re-mount field with animation
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
      {/* ── Keyframe definitions ── */}
      <style>{`
        @keyframes lp-float {
          0%, 100% { transform: translateY(0px) scale(1); }
          50%       { transform: translateY(-18px) scale(1.04); }
        }
        @keyframes lp-float-rev {
          0%, 100% { transform: translateY(0px) scale(1); }
          50%       { transform: translateY(18px) scale(0.97); }
        }
        @keyframes lp-twinkle {
          0%, 100% { opacity: 0.25; transform: scale(1); }
          50%       { opacity: 1;    transform: scale(1.6); }
        }
        @keyframes lp-spin-slow {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes lp-spin-rev {
          from { transform: rotate(0deg); }
          to   { transform: rotate(-360deg); }
        }
        @keyframes lp-pulse-glow {
          0%, 100% { opacity: 0.45; transform: scale(1); }
          50%       { opacity: 0.85; transform: scale(1.15); }
        }
        @keyframes lp-gradient-shift {
          0%   { background-position: 0% 50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes lp-slide-in-right {
          from { opacity: 0; transform: translateX(32px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes lp-field-enter {
          from { opacity: 0; transform: translateX(-12px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes lp-btn-shimmer {
          0%   { background-position: -200% center; }
          100% { background-position:  200% center; }
        }
        @keyframes lp-stagger-1 {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes lp-wave {
          0%, 100% { d: path("M0,20 Q160,0 320,20 Q480,40 640,20 Q800,0 960,20 Q1120,40 1280,20 L1280,60 L0,60 Z"); }
          50%       { d: path("M0,20 Q160,40 320,20 Q480,0 640,20 Q800,40 960,20 Q1120,0 1280,20 L1280,60 L0,60 Z"); }
        }

        .lp-float-1 { animation: lp-float     3.8s ease-in-out infinite; }
        .lp-float-2 { animation: lp-float-rev 4.5s ease-in-out infinite; }
        .lp-float-3 { animation: lp-float     5.2s ease-in-out infinite; }
        .lp-float-4 { animation: lp-float-rev 3.5s ease-in-out infinite; }

        .lp-bg-anim {
          background: linear-gradient(135deg, #1e5fa8 0%, #2a7fd4 25%, #1a4e8c 50%, #3a8fd4 75%, #1e5fa8 100%);
          background-size: 300% 300%;
          animation: lp-gradient-shift 8s ease infinite;
        }

        .lp-logo-glow {
          animation: lp-pulse-glow 3s ease-in-out infinite;
        }
        .lp-ring-outer {
          animation: lp-spin-slow 18s linear infinite;
        }
        .lp-ring-inner {
          animation: lp-spin-rev 12s linear infinite;
        }

        .lp-form-enter {
          animation: lp-slide-in-right 0.55s cubic-bezier(0.16,1,0.3,1) both;
        }
        .lp-stagger-0 { animation: lp-stagger-1 0.4s ease both 0.05s; }
        .lp-stagger-1 { animation: lp-stagger-1 0.4s ease both 0.12s; }
        .lp-stagger-2 { animation: lp-stagger-1 0.4s ease both 0.19s; }
        .lp-stagger-3 { animation: lp-stagger-1 0.4s ease both 0.26s; }
        .lp-stagger-4 { animation: lp-stagger-1 0.4s ease both 0.33s; }
        .lp-stagger-5 { animation: lp-stagger-1 0.4s ease both 0.40s; }

        .lp-field-swap { animation: lp-field-enter 0.3s cubic-bezier(0.16,1,0.3,1) both; }

        .lp-stat-card {
          transition: transform 0.25s ease, background-color 0.25s ease, box-shadow 0.25s ease;
        }
        .lp-stat-card:hover {
          transform: translateY(-6px) scale(1.04);
          background-color: rgba(255,255,255,0.2);
          box-shadow: 0 12px 28px rgba(0,0,0,0.15);
        }

        .lp-input-wrap input:focus {
          box-shadow: 0 0 0 3px rgba(42,127,212,0.18);
          border-color: hsl(var(--primary));
        }

        .lp-btn-shine {
          position: relative;
          overflow: hidden;
        }
        .lp-btn-shine::after {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.25) 50%, transparent 60%);
          background-size: 200% 100%;
          opacity: 0;
          transition: opacity 0.2s;
        }
        .lp-btn-shine:hover::after {
          opacity: 1;
          animation: lp-btn-shimmer 0.65s linear;
        }
        .lp-btn-shine:not(:disabled):hover {
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(42,127,212,0.4);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .lp-btn-shine:not(:disabled):active {
          transform: translateY(0);
        }
      `}</style>

      <div className="min-h-screen flex">

        {/* ══════════════════════════════
            Left side — Branding
        ══════════════════════════════ */}
        <div className="hidden lg:flex lg:w-1/2 relative lp-bg-anim items-center justify-center p-12 overflow-hidden">

          {/* Twinkling particles */}
          {PARTICLES.map(p => (
            <div
              key={p.id}
              className="absolute rounded-full bg-white"
              style={{
                top: p.top, left: p.left,
                width: p.size, height: p.size,
                animation: `lp-twinkle ${p.dur} ease-in-out ${p.delay} infinite`,
              }}
            />
          ))}

          {/* Animated blobs */}
          <div
            className="lp-float-1 absolute -top-20 -left-20 w-80 h-80 rounded-full blur-3xl"
            style={{ background: 'rgba(255,255,255,0.12)' }}
          />
          <div
            className="lp-float-2 absolute -bottom-28 -right-16 w-96 h-96 rounded-full blur-3xl"
            style={{ background: 'rgba(255,255,255,0.10)' }}
          />
          <div
            className="lp-float-3 absolute top-1/3 left-1/3 w-56 h-56 rounded-full blur-2xl"
            style={{ background: 'rgba(255,255,255,0.06)' }}
          />
          <div
            className="lp-float-4 absolute top-10 right-1/4 w-40 h-40 rounded-full blur-2xl"
            style={{ background: 'rgba(255,255,255,0.08)' }}
          />

          {/* Rotating rings — top-right corner */}
          <div className="absolute top-10 right-10 lp-ring-outer" style={{ width: 100, height: 100 }}>
            <svg width="100" height="100" viewBox="0 0 100 100" fill="none">
              <circle cx="50" cy="50" r="48" stroke="rgba(255,255,255,0.22)" strokeWidth="1.5" strokeDasharray="8 5" />
            </svg>
          </div>
          <div className="absolute top-18 right-18 lp-ring-inner" style={{ top: 28, right: 28, width: 60, height: 60 }}>
            <svg width="60" height="60" viewBox="0 0 60 60" fill="none">
              <circle cx="30" cy="30" r="28" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="5 4" />
            </svg>
          </div>

          {/* Rotating rings — bottom-left corner */}
          <div className="absolute bottom-10 left-10 lp-ring-inner" style={{ width: 120, height: 120 }}>
            <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
              <circle cx="60" cy="60" r="58" stroke="rgba(255,255,255,0.18)" strokeWidth="1.5" strokeDasharray="10 6" />
            </svg>
          </div>
          <div className="absolute lp-ring-outer" style={{ bottom: 22, left: 22, width: 72, height: 72 }}>
            <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
              <circle cx="36" cy="36" r="34" stroke="rgba(255,255,255,0.12)" strokeWidth="1" strokeDasharray="6 4" />
            </svg>
          </div>

          {/* Diagonal stripe accent */}
          <div className="absolute top-0 right-0 h-full w-1/3 bg-white/5 skew-x-12 translate-x-16 pointer-events-none" />

          {/* Dot grid */}
          <div
            className="absolute inset-0 opacity-[0.06] pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)',
              backgroundSize: '30px 30px',
            }}
          />

          {/* ── Content ── */}
          <div className="relative z-10 text-center max-w-sm">

            {/* Logo */}
            <div className="mb-8 flex justify-center">
              <div className="relative">
                {/* Outer rotating dashed ring */}
                <div className="absolute inset-0 lp-ring-outer" style={{ margin: '-16px' }}>
                  <svg width="200" height="200" viewBox="0 0 200 200" fill="none">
                    <circle cx="100" cy="100" r="98" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" strokeDasharray="12 6" />
                  </svg>
                </div>
                {/* Glow */}
                <div className="lp-logo-glow absolute inset-0 rounded-full blur-xl" style={{ background: 'rgba(255,255,255,0.25)', margin: '-8px' }} />
                <img
                  src="/logo.png"
                  alt="Corporación Social Educando"
                  className="relative h-40 w-40 rounded-full object-cover shadow-2xl"
                  style={{ border: '3px solid rgba(255,255,255,0.4)' }}
                />
              </div>
            </div>

            <h1 className="text-3xl font-bold font-heading text-white mb-3 leading-tight drop-shadow-md">
              Corporación Social Educando
            </h1>
            <p className="text-white/75 text-base leading-relaxed mb-10">
              Llegamos a los rincones donde la educación no llega
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { icon: BookOpen, label: '3 Técnicos',  sub: 'Programas',   delay: '0s' },
                { icon: Wifi,     label: 'Virtual',      sub: '100% Online', delay: '0.1s' },
                { icon: Award,    label: 'Avalado',      sub: 'Certificados',delay: '0.2s' },
              ].map(({ icon: Icon, label, sub, delay }) => (
                <div
                  key={label}
                  className="lp-stat-card rounded-xl backdrop-blur-sm p-4 cursor-default"
                  style={{
                    background: 'rgba(255,255,255,0.12)',
                    border: '1px solid rgba(255,255,255,0.18)',
                    animationDelay: delay,
                  }}
                >
                  <Icon className="h-6 w-6 text-white/90 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-white leading-none">{label}</p>
                  <p className="text-[11px] text-white/60 mt-1">{sub}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ══════════════════════════════
            Right side — Login form
        ══════════════════════════════ */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-background relative overflow-hidden">

          {/* Subtle bg circles */}
          <div className="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl pointer-events-none" style={{ background: 'hsl(var(--primary)/0.06)' }} />
          <div className="absolute -bottom-32 -left-32 w-72 h-72 rounded-full blur-3xl pointer-events-none" style={{ background: 'hsl(var(--primary)/0.04)' }} />

          <div className={`w-full max-w-md ${mounted ? 'lp-form-enter' : 'opacity-0'}`}>

            {/* Mobile logo */}
            <div className="lg:hidden flex flex-col items-center mb-8">
              <img src="/logo.png" alt="Logo" className="h-20 w-20 rounded-full mb-3 object-cover" />
              <h1 className="text-xl font-bold font-heading text-foreground">Educando</h1>
            </div>

            <Card className="border border-border/60 rounded-2xl overflow-hidden" style={{ boxShadow: '0 20px 60px -15px rgba(0,0,0,0.12), 0 4px 16px -4px rgba(42,127,212,0.1)' }}>
              {/* Animated top bar */}
              <div className="h-1 w-full lp-bg-anim" style={{ backgroundSize: '300% 300%' }} />

              <CardContent className="p-8">

                {/* Header */}
                <div className="text-center mb-7 lp-stagger-0">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl mb-4" style={{ background: 'hsl(var(--primary)/0.1)' }}>
                    <GraduationCap className="h-6 w-6" style={{ color: 'hsl(var(--primary))' }} />
                  </div>
                  <h2 className="text-2xl font-bold font-heading text-foreground">Iniciar Sesión</h2>
                  <p className="text-sm text-muted-foreground mt-1">Accede a tu plataforma educativa</p>
                </div>

                {/* Role tabs */}
                <div className="lp-stagger-1">
                  <Tabs value={role} onValueChange={handleRoleChange} className="mb-6">
                    <TabsList className="grid w-full grid-cols-2 rounded-xl h-11">
                      <TabsTrigger value="estudiante" className="rounded-lg text-sm gap-1.5 transition-all duration-200">
                        <GraduationCap className="h-4 w-4" />
                        Estudiante
                      </TabsTrigger>
                      <TabsTrigger value="profesor" className="rounded-lg text-sm gap-1.5 transition-all duration-200">
                        <User className="h-4 w-4" />
                        Profesor
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">

                  {/* Dynamic field with re-animation */}
                  <div key={fieldKey} className="lp-field-swap lp-input-wrap space-y-1.5">
                    {role === 'estudiante' ? (
                      <>
                        <Label htmlFor="cedula" className="text-sm font-medium">Cédula</Label>
                        <Input
                          id="cedula"
                          inputMode="numeric"
                          placeholder="Ej: 12345678 (solo números)"
                          value={form.cedula}
                          onChange={(e) => setForm({ ...form, cedula: e.target.value })}
                          className="h-11 rounded-lg transition-all duration-200"
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
                          className="h-11 rounded-lg transition-all duration-200"
                          required
                        />
                      </>
                    )}
                  </div>

                  {/* Password */}
                  <div className="lp-stagger-3 lp-input-wrap space-y-1.5">
                    <Label htmlFor="password" className="text-sm font-medium">Contraseña</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={(e) => setForm({ ...form, password: e.target.value })}
                        className="h-11 rounded-lg pr-11 transition-all duration-200"
                        required
                      />
                      <button
                        type="button"
                        className="absolute right-0 top-0 h-full w-11 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors duration-150"
                        onClick={() => setShowPassword(!showPassword)}
                        tabIndex={-1}
                      >
                        {showPassword
                          ? <EyeOff className="h-4 w-4" />
                          : <Eye className="h-4 w-4" />
                        }
                      </button>
                    </div>
                  </div>

                  {/* Submit */}
                  <div className="lp-stagger-4">
                    <Button
                      type="submit"
                      className="w-full h-11 rounded-lg font-semibold text-sm lp-btn-shine"
                      disabled={loading}
                    >
                      {loading
                        ? <><Loader2 className="h-4 w-4 animate-spin mr-2" />Ingresando...</>
                        : 'Ingresar'
                      }
                    </Button>
                  </div>
                </form>

                {/* Divider */}
                <div className="lp-stagger-5 flex items-center gap-3 my-6">
                  <div className="flex-1 h-px bg-border/60" />
                  <span className="text-xs text-muted-foreground px-1">Síguenos</span>
                  <div className="flex-1 h-px bg-border/60" />
                </div>

                {/* Facebook */}
                <div className="lp-stagger-5">
                  <a
                    href="https://www.facebook.com/share/1HmbmUyj4p/?mibextid=wwXIfr"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="lp-btn-shine flex items-center justify-center gap-2.5 w-full px-4 py-2.5 rounded-lg text-white font-medium text-sm shadow-sm"
                    style={{ background: '#1877f2', transition: 'background 0.2s' }}
                    onMouseEnter={e => e.currentTarget.style.background = '#145dbf'}
                    onMouseLeave={e => e.currentTarget.style.background = '#1877f2'}
                  >
                    <Facebook className="h-4 w-4" />
                    Síguenos en Facebook
                  </a>
                </div>

              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
