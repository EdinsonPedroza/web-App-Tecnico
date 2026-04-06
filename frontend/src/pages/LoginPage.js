import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { GraduationCap, User, Eye, EyeOff, Loader2, Facebook, Users, BookOpen, Globe } from 'lucide-react';
import { getErrorMessage } from '@/utils/errorUtils';

const LOGO = process.env.PUBLIC_URL + '/logo.png';

/* ─── Floating glassmorphism stat cards ──────────────────────── */
const STATS = [
  { icon: Users,     value: '500+',   label: 'Estudiantes', anim: 'lp-fc1', delay: '0s'    },
  { icon: BookOpen,  value: '3',      label: 'Técnicos',    anim: 'lp-fc2', delay: '0.6s'  },
  { icon: Globe,     value: '100%',   label: 'Virtual',     anim: 'lp-fc3', delay: '1.2s'  },
];

export default function LoginPage() {
  const { login }    = useAuth();
  const navigate     = useNavigate();
  const [role, setRole]             = useState('estudiante');
  const [loading, setLoading]       = useState(false);
  const [showPass, setShowPass]     = useState(false);
  const [fieldKey, setFieldKey]     = useState(0);
  const [form, setForm]             = useState({ email: '', cedula: '', password: '' });

  const handleRoleChange = (r) => { setRole(r); setFieldKey(k => k + 1); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const creds = {
        role, password: form.password,
        ...(role === 'estudiante' ? { cedula: form.cedula } : { email: form.email }),
      };
      const user = await login(creds);
      toast.success(`¡Bienvenido, ${user.name}!`);
      if (user.role === 'editor')   navigate('/editor');
      else if (user.role === 'admin')    navigate('/admin');
      else if (user.role === 'profesor') navigate('/teacher');
      else navigate('/student');
    } catch (err) {
      toast.error(getErrorMessage(err, 'Error de autenticación'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* ─── Keyframes ─────────────────────────────────────────── */}
      <style>{`
        @keyframes lp-grad {
          0%,100% { background-position: 0% 60%; }
          50%      { background-position: 100% 40%; }
        }
        @keyframes lp-fc1 {
          0%,100% { transform: translateY(0px)   rotate(-2deg); }
          50%      { transform: translateY(-14px) rotate(-1deg); }
        }
        @keyframes lp-fc2 {
          0%,100% { transform: translateY(0px)  rotate(1.5deg); }
          50%      { transform: translateY(-10px) rotate(2.5deg); }
        }
        @keyframes lp-fc3 {
          0%,100% { transform: translateY(0px)  rotate(-1deg); }
          50%      { transform: translateY(-18px) rotate(0deg); }
        }
        @keyframes lp-spin  { to { transform: rotate(360deg);  } }
        @keyframes lp-rspin { to { transform: rotate(-360deg); } }
        @keyframes lp-pulse {
          0%,100% { opacity: .5; transform: scale(1);    }
          50%      { opacity: .9; transform: scale(1.12); }
        }
        @keyframes lp-twink {
          0%,100% { opacity: .15; }
          50%      { opacity: .9;  }
        }
        @keyframes lp-blob1 {
          0%,100% { transform: translate(0,0) scale(1);    }
          33%      { transform: translate(24px,-18px) scale(1.08); }
          66%      { transform: translate(-16px,12px) scale(.94); }
        }
        @keyframes lp-blob2 {
          0%,100% { transform: translate(0,0) scale(1);    }
          33%      { transform: translate(-20px,16px) scale(1.06); }
          66%      { transform: translate(18px,-14px) scale(.96); }
        }
        @keyframes lp-field {
          from { opacity:0; transform:translateY(-8px); }
          to   { opacity:1; transform:translateY(0);    }
        }
        @keyframes lp-shine {
          0%   { background-position: -200% center; }
          100% { background-position:  200% center; }
        }

        .lp-bg {
          background: linear-gradient(135deg,
            #071e3d 0%, #0d3b6e 20%, #1a5fa8 45%,
            #1e4d8c 65%, #0a2d5e 85%, #071e3d 100%);
          background-size: 400% 400%;
          animation: lp-grad 12s ease infinite;
        }
        .lp-grad-text {
          background: linear-gradient(135deg, #60a5fa, #93c5fd, #bfdbfe);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        /* Glassmorphism stat cards */
        .lp-card {
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(255,255,255,0.16);
          border-radius: 16px;
          will-change: transform;
        }
        .lp-card:hover {
          background: rgba(255,255,255,0.14);
          border-color: rgba(255,255,255,0.28);
          transition: background .25s, border-color .25s;
        }

        /* Orbit rings */
        .lp-spin  { animation: lp-spin  22s linear infinite; will-change: transform; }
        .lp-rspin { animation: lp-rspin 16s linear infinite; will-change: transform; }

        /* Logo glow */
        .lp-glow  { animation: lp-pulse 3.8s ease-in-out infinite; will-change: transform,opacity; }

        /* Blobs */
        .lp-blob1 { animation: lp-blob1 9s ease-in-out infinite; will-change: transform; }
        .lp-blob2 { animation: lp-blob2 7s ease-in-out infinite; will-change: transform; }

        /* Field swap */
        .lp-field { animation: lp-field .28s ease both; }

        /* Submit button */
        .lp-submit {
          background: linear-gradient(135deg, #1a5fa8, #2d7dd2, #1a5fa8);
          background-size: 200% 100%;
          border: none;
          transition: background-position .4s ease, transform .18s ease, box-shadow .18s ease;
          position: relative; overflow: hidden;
        }
        .lp-submit:not(:disabled):hover {
          background-position: 100% 0;
          transform: translateY(-2px);
          box-shadow: 0 8px 28px rgba(29,99,168,.45);
        }
        .lp-submit:not(:disabled):active { transform: translateY(0); }
        .lp-submit::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,.2) 50%, transparent 65%);
          background-size: 200% 100%; opacity: 0;
        }
        .lp-submit:not(:disabled):hover::after {
          opacity: 1;
          animation: lp-shine .55s linear;
        }

        /* FB button */
        .lp-fb {
          transition: transform .18s ease, box-shadow .18s ease, background .2s;
        }
        .lp-fb:hover {
          background: #145dbf !important;
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(24,119,242,.4);
        }

        /* Input focus */
        .lp-input:focus-within input {
          border-color: #2d7dd2;
          box-shadow: 0 0 0 3px rgba(45,125,210,.15);
          transition: border-color .2s, box-shadow .2s;
        }

        /* Gradient border card */
        .lp-form-card {
          background: white;
          border-radius: 20px;
          position: relative;
        }
        .lp-form-card::before {
          content: '';
          position: absolute;
          inset: -1.5px;
          border-radius: 21.5px;
          background: linear-gradient(135deg, rgba(45,125,210,.5) 0%, rgba(148,195,255,.25) 50%, rgba(45,125,210,.4) 100%);
          z-index: -1;
        }
      `}</style>

      <div className="min-h-screen flex">

        {/* ══════════════════════════════════════
            LEFT — Hero panel
        ══════════════════════════════════════ */}
        <div
          className="hidden lg:flex lg:w-[52%] relative lp-bg items-center justify-center overflow-hidden"
          style={{ clipPath: 'polygon(0 0, 94% 0, 100% 100%, 0 100%)' }}
        >

          {/* ── Background layers ── */}

          {/* Dot grid */}
          <div className="absolute inset-0 pointer-events-none" style={{
            backgroundImage: 'radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1px)',
            backgroundSize: '28px 28px',
          }} />

          {/* Mesh overlay — subtle horizontal lines */}
          <div className="absolute inset-0 pointer-events-none" style={{
            backgroundImage: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 40px)',
          }} />

          {/* Moving blobs (GPU-only) */}
          <div className="lp-blob1 absolute rounded-full blur-3xl pointer-events-none"
            style={{ width: 380, height: 380, top: -80, left: -80, background: 'rgba(45,125,210,0.25)' }} />
          <div className="lp-blob2 absolute rounded-full blur-3xl pointer-events-none"
            style={{ width: 320, height: 320, bottom: -60, right: -40, background: 'rgba(14,60,120,0.3)' }} />

          {/* Large decorative arc behind logo */}
          <div className="absolute pointer-events-none" style={{
            width: 480, height: 480,
            top: '50%', left: '50%',
            transform: 'translate(-50%, -58%)',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(45,125,210,0.22) 0%, transparent 70%)',
          }} />

          {/* Twinkling particles */}
          {[
            [9,14,0,3.1],[16,78,0.5,4],[28,6,1.1,3.6],[38,88,0.3,5],
            [51,48,1.8,3.3],[63,19,0.7,4.2],[72,65,2,3.8],[85,35,1.4,4.6],
            [91,82,0.9,2.9],[44,92,2.3,5.1],[5,55,1.6,3.7],
          ].map(([t,l,d,s],i) => (
            <div key={i} className="absolute rounded-full bg-white pointer-events-none"
              style={{ top:`${t}%`, left:`${l}%`, width:2.5, height:2.5,
                animation:`lp-twink ${s}s ease-in-out ${d}s infinite` }} />
          ))}

          {/* Rotating orbit rings — top-right */}
          <div className="lp-spin  absolute pointer-events-none" style={{ top: 28, right: 28, width: 100, height: 100 }}>
            <svg viewBox="0 0 100 100" fill="none">
              <circle cx="50" cy="50" r="48" stroke="rgba(255,255,255,0.25)" strokeWidth="1.2" strokeDasharray="10 5"/>
            </svg>
          </div>
          <div className="lp-rspin absolute pointer-events-none" style={{ top: 44, right: 44, width: 64, height: 64 }}>
            <svg viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="7 4"/>
            </svg>
          </div>

          {/* Rotating orbit rings — bottom-left */}
          <div className="lp-rspin absolute pointer-events-none" style={{ bottom: 28, left: 28, width: 120, height: 120 }}>
            <svg viewBox="0 0 120 120" fill="none">
              <circle cx="60" cy="60" r="58" stroke="rgba(255,255,255,0.2)" strokeWidth="1.2" strokeDasharray="12 6"/>
            </svg>
          </div>
          <div className="lp-spin  absolute pointer-events-none" style={{ bottom: 48, left: 48, width: 76, height: 76 }}>
            <svg viewBox="0 0 76 76" fill="none">
              <circle cx="38" cy="38" r="36" stroke="rgba(255,255,255,0.12)" strokeWidth="1" strokeDasharray="8 5"/>
            </svg>
          </div>

          {/* Bottom educational illustration */}
          <div className="absolute bottom-0 left-0 right-0 pointer-events-none" style={{ opacity: 0.11 }}>
            <svg viewBox="0 0 900 180" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax meet">
              {/* Open book */}
              <rect x="50" y="70" width="100" height="100" rx="5" fill="white"/>
              <line x1="100" y1="70" x2="100" y2="170" stroke="rgba(0,0,0,0.2)" strokeWidth="2"/>
              <rect x="58" y="88" width="32" height="5" rx="2.5" fill="rgba(255,255,255,0.5)"/>
              <rect x="58" y="100" width="26" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="58" y="112" width="30" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="108" y="88" width="32" height="5" rx="2.5" fill="rgba(255,255,255,0.5)"/>
              <rect x="108" y="100" width="26" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="108" y="112" width="30" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              {/* Books stack */}
              <rect x="290" y="130" width="140" height="22" rx="4" fill="white"/>
              <rect x="298" y="108" width="124" height="22" rx="4" fill="white"/>
              <rect x="286" y="86"  width="136" height="22" rx="4" fill="white"/>
              {/* Mortarboard */}
              <polygon points="600,52 672,76 600,100 528,76" fill="white"/>
              <rect x="596" y="76" width="8" height="48" rx="4" fill="white"/>
              <circle cx="600" cy="126" r="10" fill="white"/>
              <line x1="672" y1="76" x2="672" y2="108" stroke="white" strokeWidth="4" strokeLinecap="round"/>
              <circle cx="672" cy="114" r="7" fill="white"/>
              {/* Pencil */}
              <rect x="800" y="30" width="16" height="130" rx="4" transform="rotate(-12 800 30)" fill="white"/>
              <polygon points="796,158 816,158 806,180" transform="rotate(-12 806 158)" fill="white"/>
              <rect x="796" y="30" width="16" height="16" rx="3" transform="rotate(-12 800 30)" fill="rgba(255,255,255,0.6)"/>
            </svg>
          </div>

          {/* ── Branding content ── */}
          <div className="relative z-10 flex flex-col items-center text-center px-16 max-w-[440px]">

            {/* Logo with orbit + glow */}
            <div className="relative mb-9 flex items-center justify-center" style={{ width: 200, height: 200 }}>
              {/* Pulsing glow */}
              <div className="lp-glow absolute rounded-full blur-2xl"
                style={{ inset: -20, background: 'rgba(255,255,255,0.18)' }} />
              {/* Outer spinning ring */}
              <div className="lp-spin absolute" style={{ inset: -22 }}>
                <svg viewBox="0 0 244 244" fill="none" style={{width:'100%',height:'100%'}}>
                  <circle cx="122" cy="122" r="120" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" strokeDasharray="14 8"/>
                </svg>
              </div>
              {/* Inner counter-spin ring */}
              <div className="lp-rspin absolute" style={{ inset: -6 }}>
                <svg viewBox="0 0 212 212" fill="none" style={{width:'100%',height:'100%'}}>
                  <circle cx="106" cy="106" r="104" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="6 10"/>
                </svg>
              </div>
              {/* Logo */}
              <img src={LOGO} alt="Corporación Social Educando"
                className="relative rounded-full object-cover shadow-2xl z-10"
                style={{ width:160, height:160, border:'3px solid rgba(255,255,255,0.4)' }}
                onError={e => e.target.style.display='none'}
              />
            </div>

            {/* Title */}
            <h1 className="text-[1.85rem] font-extrabold font-heading text-white mb-2 leading-tight tracking-tight">
              Corporación Social<br/>
              <span className="lp-grad-text">Educando</span>
            </h1>
            <p className="text-white/65 text-sm leading-relaxed mb-12 max-w-xs">
              Llegamos a los rincones donde la educación no llega
            </p>

            {/* Floating glassmorphism stat cards */}
            <div className="flex gap-4 justify-center">
              {STATS.map(({ icon: Icon, value, label, anim, delay }) => (
                <div key={label} className="lp-card px-5 py-4 text-center cursor-default"
                  style={{ animation: `${anim} ${anim==='lp-fc2'?'5s':anim==='lp-fc1'?'4.2s':'6s'} ease-in-out ${delay} infinite` }}>
                  <Icon className="h-5 w-5 mx-auto mb-2" style={{ color: 'rgba(255,255,255,0.8)' }}/>
                  <div className="text-2xl font-extrabold text-white leading-none">{value}</div>
                  <div className="text-[11px] text-white/60 mt-1 font-medium">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ══════════════════════════════════════
            RIGHT — Login form
        ══════════════════════════════════════ */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-background">

          {/* Subtle background pattern */}
          <div className="absolute inset-0 pointer-events-none lg:left-[52%]" style={{
            backgroundImage: 'radial-gradient(rgba(45,125,210,0.04) 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }} />

          <div className="relative w-full max-w-[400px]">

            {/* Mobile logo */}
            <div className="lg:hidden flex flex-col items-center mb-8">
              <img src={LOGO} alt="Logo" className="h-20 w-20 rounded-full mb-3 object-cover"
                onError={e => e.target.style.display='none'} />
              <p className="text-base font-bold font-heading text-foreground">Educando</p>
            </div>

            {/* Form card with gradient border */}
            <div className="lp-form-card" style={{
              boxShadow: '0 32px 80px -16px rgba(0,0,0,0.12), 0 8px 24px -8px rgba(26,95,168,0.1)',
            }}>
              {/* Animated top bar */}
              <div className="lp-bg h-[3px] rounded-t-[20px]" />

              <div className="p-8">
                {/* Header */}
                <div className="text-center mb-7">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl mb-4"
                    style={{ background: 'linear-gradient(135deg, rgba(26,95,168,0.1), rgba(45,125,210,0.08))' }}>
                    <GraduationCap className="h-6 w-6" style={{ color: '#1a5fa8' }} />
                  </div>
                  <h2 className="text-2xl font-extrabold font-heading text-foreground tracking-tight">
                    Iniciar Sesión
                  </h2>
                  <p className="text-sm text-muted-foreground mt-1">
                    Accede a tu plataforma educativa
                  </p>
                </div>

                {/* Role tabs */}
                <Tabs value={role} onValueChange={handleRoleChange} className="mb-5">
                  <TabsList className="grid w-full grid-cols-2 rounded-xl h-11"
                    style={{ background: 'rgba(26,95,168,0.06)' }}>
                    <TabsTrigger value="estudiante" className="rounded-xl text-sm gap-1.5 font-medium">
                      <GraduationCap className="h-4 w-4" />Estudiante
                    </TabsTrigger>
                    <TabsTrigger value="profesor" className="rounded-xl text-sm gap-1.5 font-medium">
                      <User className="h-4 w-4" />Profesor
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                <form onSubmit={handleSubmit} className="space-y-4">

                  {/* Dynamic field */}
                  <div key={fieldKey} className="lp-field space-y-1.5">
                    {role === 'estudiante' ? (
                      <>
                        <Label htmlFor="cedula" className="text-sm font-semibold text-foreground/80">Cédula</Label>
                        <div className="lp-input">
                          <Input id="cedula" inputMode="numeric"
                            placeholder="Ej: 12345678 (solo números)"
                            value={form.cedula}
                            onChange={e => setForm({ ...form, cedula: e.target.value })}
                            className="h-11 rounded-xl text-sm"
                            required />
                        </div>
                      </>
                    ) : (
                      <>
                        <Label htmlFor="email" className="text-sm font-semibold text-foreground/80">Correo Electrónico</Label>
                        <div className="lp-input">
                          <Input id="email" type="email"
                            placeholder="correo@educando.com"
                            value={form.email}
                            onChange={e => setForm({ ...form, email: e.target.value })}
                            className="h-11 rounded-xl text-sm"
                            required />
                        </div>
                      </>
                    )}
                  </div>

                  {/* Password */}
                  <div className="space-y-1.5">
                    <Label htmlFor="password" className="text-sm font-semibold text-foreground/80">Contraseña</Label>
                    <div className="lp-input relative">
                      <Input id="password"
                        type={showPass ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={e => setForm({ ...form, password: e.target.value })}
                        className="h-11 rounded-xl text-sm pr-11"
                        required />
                      <button type="button" tabIndex={-1}
                        onClick={() => setShowPass(v => !v)}
                        className="absolute right-0 top-0 h-full w-11 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
                        {showPass ? <EyeOff className="h-4 w-4"/> : <Eye className="h-4 w-4"/>}
                      </button>
                    </div>
                  </div>

                  {/* Submit */}
                  <Button type="submit" disabled={loading}
                    className="lp-submit w-full h-11 rounded-xl font-bold text-sm text-white border-0 mt-1"
                    style={{ background: 'linear-gradient(135deg, #0f3460, #1a5fa8, #2d7dd2)' }}>
                    {loading
                      ? <><Loader2 className="h-4 w-4 animate-spin mr-2"/>Ingresando...</>
                      : 'Ingresar a la plataforma'
                    }
                  </Button>
                </form>

                {/* Divider */}
                <div className="flex items-center gap-3 my-5">
                  <div className="flex-1 h-px bg-border/40" />
                  <span className="text-xs text-muted-foreground/70 font-medium tracking-wide uppercase">Síguenos</span>
                  <div className="flex-1 h-px bg-border/40" />
                </div>

                {/* Facebook */}
                <a href="https://www.facebook.com/share/1HmbmUyj4p/?mibextid=wwXIfr"
                  target="_blank" rel="noopener noreferrer"
                  className="lp-fb flex items-center justify-center gap-2.5 w-full px-4 py-2.5 rounded-xl text-white font-semibold text-sm"
                  style={{ background: '#1877f2' }}>
                  <Facebook className="h-4 w-4"/>
                  Síguenos en Facebook
                </a>
              </div>
            </div>

            {/* Subtle copyright */}
            <p className="text-center text-xs text-muted-foreground/50 mt-5">
              © {new Date().getFullYear()} Corporación Social Educando
            </p>
          </div>
        </div>

      </div>
    </>
  );
}
