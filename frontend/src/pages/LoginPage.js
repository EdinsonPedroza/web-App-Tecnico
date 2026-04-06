import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { GraduationCap, User, Eye, EyeOff, Loader2, Facebook, BookOpen, Award, Wifi } from 'lucide-react';
import api from '@/lib/api';
import { getErrorMessage } from '@/utils/errorUtils';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState('estudiante');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [form, setForm] = useState({
    email: '',
    cedula: '',
    password: ''
  });

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
      const msg = getErrorMessage(err, 'Error de autenticación');
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* ── Left side – Branding ── */}
      <div className="hidden lg:flex lg:w-1/2 relative gradient-primary items-center justify-center p-12 overflow-hidden">

        {/* Decorative blobs */}
        <div className="absolute -top-24 -left-24 w-72 h-72 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-32 -right-20 w-96 h-96 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute top-1/2 left-1/4 w-48 h-48 rounded-full bg-white/5 blur-2xl" />

        {/* Floating rings */}
        <div className="absolute top-16 right-16 w-32 h-32 rounded-full border border-white/20" />
        <div className="absolute top-20 right-20 w-20 h-20 rounded-full border border-white/15" />
        <div className="absolute bottom-24 left-12 w-40 h-40 rounded-full border border-white/15" />
        <div className="absolute bottom-28 left-16 w-24 h-24 rounded-full border border-white/10" />

        {/* Dot grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage: `radial-gradient(circle, #ffffff 1px, transparent 1px)`,
            backgroundSize: '28px 28px'
          }}
        />

        {/* Diagonal accent stripe */}
        <div className="absolute top-0 right-0 w-1/3 h-full bg-white/5 skew-x-12 translate-x-12" />

        {/* Content */}
        <div className="relative z-10 text-center max-w-md">
          {/* Logo with glow ring */}
          <div className="mb-8 flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 rounded-full bg-white/20 blur-xl scale-110" />
              <img
                src="/logo.png"
                alt="Corporación Social Educando"
                className="relative h-40 w-40 rounded-full object-cover shadow-2xl ring-4 ring-white/30"
              />
            </div>
          </div>

          <h1 className="text-3xl font-bold font-heading text-white mb-3 leading-tight">
            Corporación Social Educando
          </h1>
          <p className="text-white/75 text-base leading-relaxed mb-10">
            Llegamos a los rincones donde la educación no llega
          </p>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: BookOpen, label: '3 Técnicos', sub: 'Programas' },
              { icon: Wifi,       label: 'Virtual',    sub: '100% Online' },
              { icon: Award,      label: 'Avalado',    sub: 'Certificados' },
            ].map(({ icon: Icon, label, sub }) => (
              <div
                key={label}
                className="rounded-xl bg-white/10 backdrop-blur-sm border border-white/15 p-4 hover:bg-white/15 transition-colors"
              >
                <Icon className="h-6 w-6 text-white/90 mx-auto mb-2" />
                <p className="text-sm font-semibold text-white/95 leading-none">{label}</p>
                <p className="text-[11px] text-white/60 mt-1">{sub}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right side – Login form ── */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-background">
        <div className="w-full max-w-md animate-slide-up">

          {/* Mobile logo */}
          <div className="lg:hidden flex flex-col items-center mb-8">
            <img src="/logo.png" alt="Logo" className="h-20 w-20 rounded-full mb-3 object-cover" />
            <h1 className="text-xl font-bold font-heading text-foreground">Educando</h1>
          </div>

          <Card className="shadow-elegant border border-border/60 rounded-2xl overflow-hidden">
            {/* Card top accent bar */}
            <div className="h-1 w-full gradient-primary" />

            <CardContent className="p-8">
              {/* Header */}
              <div className="text-center mb-7">
                <h2 className="text-2xl font-bold font-heading text-foreground">Iniciar Sesión</h2>
                <p className="text-sm text-muted-foreground mt-1">Accede a tu plataforma educativa</p>
              </div>

              {/* Role tabs */}
              <Tabs value={role} onValueChange={setRole} className="mb-6">
                <TabsList className="grid w-full grid-cols-2 rounded-xl h-11">
                  <TabsTrigger value="estudiante" className="rounded-lg text-sm gap-1.5">
                    <GraduationCap className="h-4 w-4" />
                    Estudiante
                  </TabsTrigger>
                  <TabsTrigger value="profesor" className="rounded-lg text-sm gap-1.5">
                    <User className="h-4 w-4" />
                    Profesor
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              <form onSubmit={handleSubmit} className="space-y-5">
                {role === 'estudiante' ? (
                  <div className="space-y-1.5">
                    <Label htmlFor="cedula" className="text-sm font-medium">Cédula</Label>
                    <Input
                      id="cedula"
                      inputMode="numeric"
                      placeholder="Ej: 12345678 (solo números)"
                      value={form.cedula}
                      onChange={(e) => setForm({ ...form, cedula: e.target.value })}
                      className="h-11 rounded-lg"
                      required
                    />
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    <Label htmlFor="email" className="text-sm font-medium">Correo Electrónico</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="correo@educando.com"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="h-11 rounded-lg"
                      required
                    />
                  </div>
                )}

                <div className="space-y-1.5">
                  <Label htmlFor="password" className="text-sm font-medium">Contraseña</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                      className="h-11 rounded-lg pr-11"
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full w-11 hover:bg-transparent text-muted-foreground hover:text-foreground"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full h-11 rounded-lg font-semibold text-sm mt-1"
                  disabled={loading}
                >
                  {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                  {loading ? 'Ingresando...' : 'Ingresar'}
                </Button>
              </form>

              {/* Divider */}
              <div className="flex items-center gap-3 my-6">
                <div className="flex-1 h-px bg-border/60" />
                <span className="text-xs text-muted-foreground">Síguenos</span>
                <div className="flex-1 h-px bg-border/60" />
              </div>

              {/* Facebook */}
              <a
                href="https://www.facebook.com/share/1HmbmUyj4p/?mibextid=wwXIfr"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2.5 w-full px-4 py-2.5 rounded-lg bg-[#1877f2] hover:bg-[#145dbf] text-white font-medium text-sm transition-all duration-200 shadow-sm hover:shadow-md hover:scale-[1.02]"
              >
                <Facebook className="h-4 w-4" />
                Síguenos en Facebook
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
