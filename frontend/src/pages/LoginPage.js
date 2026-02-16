import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { GraduationCap, User, Shield, Eye, EyeOff, Loader2 } from 'lucide-react';
import api from '@/lib/api';

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
      
      if (userData.role === 'admin') navigate('/admin');
      else if (userData.role === 'profesor') navigate('/teacher');
      else navigate('/student');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error de autenticación';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative gradient-primary items-center justify-center p-12">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}
        />
        <div className="relative z-10 text-center max-w-md">
          <div className="mb-8 flex justify-center">
            <img
              src="/logo.png"
              alt="Corporación Social Educando"
              className="h-44 w-44 rounded-full bg-card/10 p-2 shadow-lg"
            />
          </div>
          <h1 className="text-3xl font-bold font-heading text-primary-foreground mb-4">
            Corporación Social Educando
          </h1>
          <p className="text-primary-foreground/80 text-base leading-relaxed">
            Llegamos a los rincones donde la educación no llega
          </p>
          <div className="mt-10 grid grid-cols-3 gap-4">
            <div className="rounded-lg bg-card/10 backdrop-blur-sm p-4">
              <GraduationCap className="h-6 w-6 text-primary-foreground/90 mx-auto mb-2" />
              <p className="text-xs text-primary-foreground/70">3 Técnicos</p>
            </div>
            <div className="rounded-lg bg-card/10 backdrop-blur-sm p-4">
              <User className="h-6 w-6 text-primary-foreground/90 mx-auto mb-2" />
              <p className="text-xs text-primary-foreground/70">Virtual 100%</p>
            </div>
            <div className="rounded-lg bg-card/10 backdrop-blur-sm p-4">
              <Shield className="h-6 w-6 text-primary-foreground/90 mx-auto mb-2" />
              <p className="text-xs text-primary-foreground/70">Certificados</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex flex-col items-center mb-8">
            <img src="/logo.png" alt="Logo" className="h-20 w-20 rounded-full mb-3" />
            <h1 className="text-xl font-bold font-heading text-foreground">Educando</h1>
          </div>

          <Card className="shadow-elegant border-border/50">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-2xl font-heading">Iniciar Sesión</CardTitle>
              <CardDescription>Accede a tu plataforma educativa</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs value={role} onValueChange={setRole} className="mb-6">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="estudiante" className="text-xs sm:text-sm">
                    <GraduationCap className="h-3.5 w-3.5 mr-1" />
                    Estudiante
                  </TabsTrigger>
                  <TabsTrigger value="profesor" className="text-xs sm:text-sm">
                    <User className="h-3.5 w-3.5 mr-1" />
                    Profesor
                  </TabsTrigger>
                  <TabsTrigger value="admin" className="text-xs sm:text-sm">
                    <Shield className="h-3.5 w-3.5 mr-1" />
                    Admin
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              <form onSubmit={handleSubmit} className="space-y-4">
                {role === 'estudiante' ? (
                  <div className="space-y-2">
                    <Label htmlFor="cedula">Cédula</Label>
                    <Input
                      id="cedula"
                      placeholder="Ingresa tu número de cédula"
                      value={form.cedula}
                      onChange={(e) => setForm({ ...form, cedula: e.target.value })}
                      required
                    />
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Label htmlFor="email">Correo Electrónico</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="correo@educando.com"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      required
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="password">Contraseña</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <Button type="submit" className="w-full" size="lg" disabled={loading}>
                  {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                  Ingresar
                </Button>
              </form>

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
