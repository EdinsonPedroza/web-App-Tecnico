import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { GraduationCap, User, Eye, EyeOff, Loader2, Facebook, Users, BookOpen, Clock, Globe } from 'lucide-react';
import { getErrorMessage } from '@/utils/errorUtils';

const LOGO = process.env.PUBLIC_URL + '/logo.png';

const STATS = [
  { icon: Users,    value: '500+',  label: 'Estudiantes'       },
  { icon: BookOpen, value: '+10',   label: 'Técnicos'          },
  { icon: Clock,    value: '6',     label: 'Meses · Bachiller' },
  { icon: Globe,    value: '100%',  label: 'Virtual'           },
];

export default function LoginPage() {
  const { login }   = useAuth();
  const navigate    = useNavigate();
  const [role, setRole]         = useState('estudiante');
  const [loading, setLoading]   = useState(false);
  const [showPass, setShowPass] = useState(false);
  const [fieldKey, setFieldKey] = useState(0);
  const [form, setForm]         = useState({ email: '', cedula: '', password: '' });

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
      if      (user.role === 'editor')   navigate('/editor');
      else if (user.role === 'admin')    navigate('/admin');
      else if (user.role === 'profesor') navigate('/teacher');
      else                               navigate('/student');
    } catch (err) {
      toast.error(getErrorMessage(err, 'Error de autenticación'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        /* ── gradient background ── */
        @keyframes lp-grad {
          0%,100% { background-position: 0% 60%; }
          50%      { background-position: 100% 40%; }
        }
        .lp-bg {
          background: linear-gradient(145deg,
            #071e3d 0%, #0c2d5c 22%, #14488a 48%,
            #0d3468 72%, #071e3d 100%);
          background-size: 300% 300%;
          animation: lp-grad 14s ease infinite;
        }

        /* ── logo glow (very subtle) ── */
        @keyframes lp-glow {
          0%,100% { opacity: .4; }
          50%      { opacity: .7; }
        }
        .lp-glow { animation: lp-glow 5s ease-in-out infinite; }

        /* ── stat cards ── only opacity drift, no movement ── */
        @keyframes lp-card-in {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0);   }
        }
        .lp-stat { animation: lp-card-in .5s ease both; }
        .lp-stat:nth-child(1) { animation-delay: .05s; }
        .lp-stat:nth-child(2) { animation-delay: .12s; }
        .lp-stat:nth-child(3) { animation-delay: .19s; }
        .lp-stat:nth-child(4) { animation-delay: .26s; }
        .lp-stat {
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          background: rgba(255,255,255,0.07);
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 14px;
          transition: background .2s, border-color .2s, transform .2s;
        }
        .lp-stat:hover {
          background: rgba(255,255,255,0.12);
          border-color: rgba(255,255,255,0.22);
          transform: translateY(-3px);
        }

        /* ── twinkling particles ── */
        @keyframes lp-twink {
          0%,100% { opacity: .1; }
          50%      { opacity: .6; }
        }

        /* ── gradient text ── */
        .lp-grad-text {
          background: linear-gradient(120deg, #93c5fd, #bfdbfe, #e0f2fe);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        /* ── field swap ── */
        @keyframes lp-field {
          from { opacity:0; transform:translateY(-6px); }
          to   { opacity:1; transform:translateY(0);    }
        }
        .lp-field { animation: lp-field .25s ease both; }

        /* ── submit button ── */
        .lp-submit {
          background: linear-gradient(135deg, #0f3460 0%, #1a5fa8 50%, #2176c7 100%);
          background-size: 200% 100%;
          border: none; color: white; font-weight: 700;
          transition: background-position .35s ease, transform .16s ease, box-shadow .16s ease;
          position: relative; overflow: hidden;
        }
        .lp-submit:not(:disabled):hover {
          background-position: 100% 0;
          transform: translateY(-2px);
          box-shadow: 0 8px 28px rgba(26,95,168,.42);
        }
        .lp-submit:not(:disabled):active { transform: translateY(0); }

        /* ── gradient border on form card ── */
        .lp-form-card {
          background: hsl(var(--card));
          border-radius: 20px;
          position: relative;
          isolation: isolate;
        }
        .lp-form-card::before {
          content: '';
          position: absolute;
          inset: -1.5px;
          border-radius: 21.5px;
          background: linear-gradient(135deg,
            rgba(45,125,210,.45) 0%,
            rgba(147,197,253,.2) 50%,
            rgba(45,125,210,.35) 100%);
          z-index: -1;
        }

        /* ── input focus glow ── */
        .lp-input-wrap input:focus {
          border-color: #2176c7;
          box-shadow: 0 0 0 3px rgba(33,118,199,.14);
          transition: border-color .18s, box-shadow .18s;
        }

        /* ── fb hover ── */
        .lp-fb {
          transition: background .2s, transform .16s, box-shadow .16s;
        }
        .lp-fb:hover {
          background: #145dbf !important;
          transform: translateY(-2px);
          box-shadow: 0 6px 18px rgba(24,119,242,.38);
        }
      `}</style>

      <div className="min-h-screen flex">

        {/* ════════════════════════════════
            LEFT — Hero panel
        ════════════════════════════════ */}
        <div
          className="hidden lg:flex lg:w-[52%] relative lp-bg items-center justify-center overflow-hidden"
          style={{ clipPath: 'polygon(0 0, 94% 0, 100% 100%, 0 100%)' }}
        >

          {/* Dot grid */}
          <div className="absolute inset-0 pointer-events-none" style={{
            backgroundImage: 'radial-gradient(rgba(255,255,255,0.055) 1px, transparent 1px)',
            backgroundSize: '30px 30px',
          }}/>

          {/* Horizontal mesh lines */}
          <div className="absolute inset-0 pointer-events-none" style={{
            backgroundImage: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 44px)',
          }}/>

          {/* Static blobs — no animation, just depth layers */}
          <div className="absolute rounded-full blur-3xl pointer-events-none"
            style={{ width:420, height:420, top:-100, left:-100, background:'rgba(21,74,142,0.4)' }}/>
          <div className="absolute rounded-full blur-3xl pointer-events-none"
            style={{ width:340, height:340, bottom:-80, right:-60, background:'rgba(10,42,90,0.5)' }}/>
          <div className="absolute rounded-full blur-2xl pointer-events-none"
            style={{ width:240, height:240, top:'40%', left:'60%', transform:'translate(-50%,-50%)', background:'rgba(33,118,199,0.15)' }}/>

          {/* Radial center glow */}
          <div className="absolute pointer-events-none" style={{
            width:500, height:500,
            top:'50%', left:'50%',
            transform:'translate(-50%,-56%)',
            borderRadius:'50%',
            background:'radial-gradient(circle, rgba(33,118,199,0.18) 0%, transparent 68%)',
          }}/>

          {/* Sparse twinkling particles */}
          {[
            [8,13,0,3.4],[17,76,0.7,4.2],[34,6,1.3,3.8],[42,90,0.2,5.1],
            [59,52,1.9,3.5],[71,22,0.5,4.6],[82,68,2.2,3.2],[90,40,1.1,4.9],
          ].map(([t,l,d,s],i) => (
            <div key={i} className="absolute rounded-full bg-white pointer-events-none"
              style={{ top:`${t}%`, left:`${l}%`, width:2.5, height:2.5,
                animation:`lp-twink ${s}s ease-in-out ${d}s infinite` }}/>
          ))}

          {/* Bottom illustration */}
          <div className="absolute bottom-0 left-0 right-0 pointer-events-none" style={{ opacity:.1 }}>
            <svg viewBox="0 0 900 180" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax meet">
              <rect x="50" y="70" width="100" height="100" rx="5" fill="white"/>
              <line x1="100" y1="70" x2="100" y2="170" stroke="rgba(0,0,0,0.2)" strokeWidth="2"/>
              <rect x="58" y="88" width="32" height="5" rx="2.5" fill="rgba(255,255,255,0.5)"/>
              <rect x="58" y="100" width="24" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="58" y="112" width="28" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="108" y="88" width="32" height="5" rx="2.5" fill="rgba(255,255,255,0.5)"/>
              <rect x="108" y="100" width="24" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="108" y="112" width="28" height="5" rx="2.5" fill="rgba(255,255,255,0.4)"/>
              <rect x="295" y="128" width="130" height="22" rx="4" fill="white"/>
              <rect x="303" y="106" width="114" height="22" rx="4" fill="white"/>
              <rect x="291" y="84"  width="128" height="22" rx="4" fill="white"/>
              <polygon points="600,50 672,76 600,102 528,76" fill="white"/>
              <rect x="596" y="76" width="8" height="46" rx="4" fill="white"/>
              <circle cx="600" cy="126" r="9" fill="white"/>
              <line x1="672" y1="76" x2="672" y2="106" stroke="white" strokeWidth="4" strokeLinecap="round"/>
              <circle cx="672" cy="113" r="7" fill="white"/>
              <rect x="800" y="28" width="14" height="128" rx="4" transform="rotate(-12 800 28)" fill="white"/>
              <polygon points="797,154 813,154 805,176" transform="rotate(-12 805 154)" fill="white"/>
            </svg>
          </div>

          {/* ── Content ── */}
          <div className="relative z-10 flex flex-col items-center text-center px-14 max-w-[440px]">

            {/* Logo — glow only, no spinning rings */}
            <div className="relative mb-8 flex items-center justify-center" style={{ width:164, height:164 }}>
              <div className="lp-glow absolute rounded-full blur-2xl"
                style={{ inset:-16, background:'rgba(255,255,255,0.16)' }}/>
              <img src={LOGO} alt="Corporación Social Educando"
                className="relative rounded-full object-cover shadow-2xl z-10"
                style={{ width:160, height:160, border:'3px solid rgba(255,255,255,0.35)' }}
                onError={e => { e.target.style.display='none'; }}
              />
            </div>

            {/* Title */}
            <h1 className="text-[1.75rem] font-extrabold font-heading text-white mb-2 leading-snug tracking-tight">
              Corporación Social<br/>
              <span className="lp-grad-text">Educando</span>
            </h1>
            <p className="text-white/60 text-sm leading-relaxed mb-10 max-w-[280px]">
              Llegamos a los rincones donde la educación no llega
            </p>

            {/* Stat cards — 2×2 grid, entrada suave, hover lift */}
            <div className="grid grid-cols-2 gap-3 w-full max-w-[320px]">
              {STATS.map(({ icon: Icon, value, label }) => (
                <div key={label} className="lp-stat flex items-center gap-3 px-4 py-3.5">
                  <div className="shrink-0 flex items-center justify-center w-9 h-9 rounded-xl"
                    style={{ background:'rgba(255,255,255,0.1)' }}>
                    <Icon className="h-4 w-4 text-white/80"/>
                  </div>
                  <div className="text-left min-w-0">
                    <div className="text-lg font-extrabold text-white leading-none">{value}</div>
                    <div className="text-[11px] text-white/55 mt-0.5 leading-tight">{label}</div>
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>

        {/* ════════════════════════════════
            RIGHT — Login form
        ════════════════════════════════ */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-background">

          {/* Very subtle dot texture — right side only */}
          <div className="absolute inset-0 pointer-events-none" style={{
            backgroundImage:'radial-gradient(rgba(33,118,199,0.035) 1px, transparent 1px)',
            backgroundSize:'22px 22px',
          }}/>

          <div className="relative w-full max-w-[390px]">

            {/* Mobile logo */}
            <div className="lg:hidden flex flex-col items-center mb-8">
              <img src={LOGO} alt="Logo" className="h-20 w-20 rounded-full mb-3 object-cover"
                onError={e => { e.target.style.display='none'; }}/>
              <p className="text-base font-bold font-heading text-foreground">Educando</p>
            </div>

            <div className="lp-form-card"
              style={{ boxShadow:'0 24px 64px -12px rgba(0,0,0,0.1), 0 6px 20px -6px rgba(14,68,138,0.09)' }}>

              {/* Top accent bar */}
              <div className="lp-bg h-[3px] rounded-t-[20px]"/>

              <div className="p-8">
                {/* Header */}
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl mb-4"
                    style={{ background:'linear-gradient(135deg,rgba(14,52,96,0.08),rgba(33,118,199,0.07))' }}>
                    <GraduationCap className="h-5 w-5" style={{ color:'#1a5fa8' }}/>
                  </div>
                  <h2 className="text-[1.35rem] font-extrabold font-heading text-foreground tracking-tight">
                    Iniciar Sesión
                  </h2>
                  <p className="text-sm text-muted-foreground mt-1">
                    Accede a tu plataforma educativa
                  </p>
                </div>

                {/* Role tabs */}
                <Tabs value={role} onValueChange={handleRoleChange} className="mb-5">
                  <TabsList className="grid w-full grid-cols-2 rounded-xl h-11"
                    style={{ background:'rgba(14,52,96,0.05)' }}>
                    <TabsTrigger value="estudiante" className="rounded-xl text-sm gap-1.5 font-semibold">
                      <GraduationCap className="h-3.5 w-3.5"/>Estudiante
                    </TabsTrigger>
                    <TabsTrigger value="profesor" className="rounded-xl text-sm gap-1.5 font-semibold">
                      <User className="h-3.5 w-3.5"/>Profesor
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                <form onSubmit={handleSubmit} className="space-y-4">

                  {/* Dynamic field */}
                  <div key={fieldKey} className="lp-field space-y-1.5">
                    {role === 'estudiante' ? (
                      <>
                        <Label htmlFor="cedula" className="text-sm font-semibold text-foreground/75">Cédula</Label>
                        <div className="lp-input-wrap">
                          <Input id="cedula" inputMode="numeric"
                            placeholder="Ej: 12345678 (solo números)"
                            value={form.cedula}
                            onChange={e => setForm({ ...form, cedula: e.target.value })}
                            className="h-11 rounded-xl text-sm" required/>
                        </div>
                      </>
                    ) : (
                      <>
                        <Label htmlFor="email" className="text-sm font-semibold text-foreground/75">Correo Electrónico</Label>
                        <div className="lp-input-wrap">
                          <Input id="email" type="email"
                            placeholder="correo@educando.com"
                            value={form.email}
                            onChange={e => setForm({ ...form, email: e.target.value })}
                            className="h-11 rounded-xl text-sm" required/>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Password */}
                  <div className="space-y-1.5">
                    <Label htmlFor="password" className="text-sm font-semibold text-foreground/75">Contraseña</Label>
                    <div className="lp-input-wrap relative">
                      <Input id="password"
                        type={showPass ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={e => setForm({ ...form, password: e.target.value })}
                        className="h-11 rounded-xl text-sm pr-11" required/>
                      <button type="button" tabIndex={-1}
                        onClick={() => setShowPass(v => !v)}
                        className="absolute right-0 top-0 h-full w-11 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
                        {showPass ? <EyeOff className="h-4 w-4"/> : <Eye className="h-4 w-4"/>}
                      </button>
                    </div>
                  </div>

                  <Button type="submit" disabled={loading}
                    className="lp-submit w-full h-11 rounded-xl text-sm mt-1">
                    {loading
                      ? <><Loader2 className="h-4 w-4 animate-spin mr-2"/>Ingresando...</>
                      : 'Ingresar a la plataforma'
                    }
                  </Button>
                </form>

                {/* Divider */}
                <div className="flex items-center gap-3 my-5">
                  <div className="flex-1 h-px bg-border/40"/>
                  <span className="text-[11px] text-muted-foreground/60 font-medium tracking-widest uppercase">Síguenos</span>
                  <div className="flex-1 h-px bg-border/40"/>
                </div>

                {/* Facebook */}
                <a href="https://www.facebook.com/share/1HmbmUyj4p/?mibextid=wwXIfr"
                  target="_blank" rel="noopener noreferrer"
                  className="lp-fb flex items-center justify-center gap-2.5 w-full px-4 py-2.5 rounded-xl text-white font-semibold text-sm"
                  style={{ background:'#1877f2' }}>
                  <Facebook className="h-4 w-4"/>Síguenos en Facebook
                </a>
              </div>
            </div>

            <p className="text-center text-[11px] text-muted-foreground/40 mt-5 tracking-wide">
              © {new Date().getFullYear()} Corporación Social Educando
            </p>
          </div>
        </div>

      </div>
    </>
  );
}
