import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import Icon from '@/components/ui/icon';

interface User {
  id: number;
  email: string;
  full_name: string;
}

const API_URL = 'https://functions.poehali.dev/8f5ec37e-709a-4ca9-bfa0-616a89618a9e';

export default function Index() {
  const [view, setView] = useState<'login' | 'register' | 'home' | 'profile'>('login');
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    full_name: ''
  });

  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setView('home');
    }
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (registerData.password.length < 8) {
      toast.error('Ошибка', {
        description: 'Пароль должен содержать минимум 8 символов'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'register', ...registerData })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        toast.success('Успешно', {
          description: 'Регистрация завершена! Теперь войдите в систему'
        });
        setRegisterData({ email: '', password: '', full_name: '' });
        setView('login');
      } else {
        toast.error('Ошибка', {
          description: data.error || 'Не удалось зарегистрироваться'
        });
      }
    } catch {
      toast.error('Ошибка', {
        description: 'Проблема с подключением к серверу'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'login', ...loginData })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        toast.success('Успешно', {
          description: 'Добро пожаловать!'
        });
        setLoginData({ email: '', password: '' });
        setView('home');
      } else {
        toast.error('Ошибка', {
          description: data.error || 'Неверные данные для входа'
        });
      }
    } catch {
      toast.error('Ошибка', {
        description: 'Проблема с подключением к серверу'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    setView('login');
    toast.success('Вы вышли из системы');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl">
        {view === 'login' && (
          <Card className="max-w-md mx-auto animate-scale-in shadow-2xl border-0 bg-white/80 backdrop-blur">
            <CardHeader className="space-y-2 text-center">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mb-4 animate-fade-in">
                <Icon name="LogIn" className="text-white" size={32} />
              </div>
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Вход
              </CardTitle>
              <CardDescription className="text-base">Войдите в свой аккаунт</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2 animate-slide-in">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="you@example.com"
                    value={loginData.email}
                    onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                    required
                    className="border-2 focus:border-purple-500 transition-all"
                  />
                </div>
                <div className="space-y-2 animate-slide-in" style={{ animationDelay: '0.1s' }}>
                  <Label htmlFor="login-password">Пароль</Label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="••••••••"
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    required
                    className="border-2 focus:border-purple-500 transition-all"
                  />
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-6 text-lg transition-all hover:scale-105"
                >
                  {loading ? 'Загрузка...' : 'Войти'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setView('register')}
                  className="w-full hover:bg-purple-100 transition-colors"
                >
                  Нет аккаунта? Регистрация
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {view === 'register' && (
          <Card className="max-w-md mx-auto animate-scale-in shadow-2xl border-0 bg-white/80 backdrop-blur">
            <CardHeader className="space-y-2 text-center">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4 animate-fade-in">
                <Icon name="UserPlus" className="text-white" size={32} />
              </div>
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Регистрация
              </CardTitle>
              <CardDescription className="text-base">Создайте новый аккаунт</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="space-y-2 animate-slide-in">
                  <Label htmlFor="register-name">Полное имя</Label>
                  <Input
                    id="register-name"
                    type="text"
                    placeholder="Иван Иванов"
                    value={registerData.full_name}
                    onChange={(e) => setRegisterData({ ...registerData, full_name: e.target.value })}
                    required
                    className="border-2 focus:border-blue-500 transition-all"
                  />
                </div>
                <div className="space-y-2 animate-slide-in" style={{ animationDelay: '0.1s' }}>
                  <Label htmlFor="register-email">Email</Label>
                  <Input
                    id="register-email"
                    type="email"
                    placeholder="you@example.com"
                    value={registerData.email}
                    onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                    required
                    className="border-2 focus:border-blue-500 transition-all"
                  />
                </div>
                <div className="space-y-2 animate-slide-in" style={{ animationDelay: '0.2s' }}>
                  <Label htmlFor="register-password">Пароль (минимум 8 символов)</Label>
                  <Input
                    id="register-password"
                    type="password"
                    placeholder="••••••••"
                    value={registerData.password}
                    onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                    required
                    className="border-2 focus:border-blue-500 transition-all"
                  />
                  {registerData.password && registerData.password.length < 8 && (
                    <p className="text-sm text-red-500 flex items-center gap-1">
                      <Icon name="AlertCircle" size={16} />
                      Пароль должен содержать минимум 8 символов
                    </p>
                  )}
                </div>
                <Button
                  type="submit"
                  disabled={loading || registerData.password.length < 8}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-6 text-lg transition-all hover:scale-105"
                >
                  {loading ? 'Загрузка...' : 'Зарегистрироваться'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setView('login')}
                  className="w-full hover:bg-blue-100 transition-colors"
                >
                  Уже есть аккаунт? Войти
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {view === 'home' && user && (
          <div className="animate-fade-in">
            <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-3xl p-1 shadow-2xl">
              <div className="bg-white rounded-3xl p-8">
                <div className="text-center mb-8">
                  <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent animate-slide-in">
                    Добро пожаловать, {user.full_name}! 👋
                  </h1>
                  <p className="text-xl text-gray-600 animate-fade-in">Вы успешно вошли в систему</p>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mt-12">
                  <Card className="hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 animate-scale-in">
                    <CardHeader>
                      <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mb-3">
                        <Icon name="Home" className="text-white" size={24} />
                      </div>
                      <CardTitle className="text-2xl">Главная</CardTitle>
                      <CardDescription>Обзор вашего аккаунта</CardDescription>
                    </CardHeader>
                  </Card>

                  <Card
                    onClick={() => setView('profile')}
                    className="hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50 animate-scale-in"
                    style={{ animationDelay: '0.1s' }}
                  >
                    <CardHeader>
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-3">
                        <Icon name="User" className="text-white" size={24} />
                      </div>
                      <CardTitle className="text-2xl">Профиль</CardTitle>
                      <CardDescription>Просмотр и настройки</CardDescription>
                    </CardHeader>
                  </Card>

                  <Card
                    onClick={handleLogout}
                    className="hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-pink-200 bg-gradient-to-br from-pink-50 to-red-50 animate-scale-in"
                    style={{ animationDelay: '0.2s' }}
                  >
                    <CardHeader>
                      <div className="w-12 h-12 bg-gradient-to-r from-pink-600 to-red-600 rounded-full flex items-center justify-center mb-3">
                        <Icon name="LogOut" className="text-white" size={24} />
                      </div>
                      <CardTitle className="text-2xl">Выход</CardTitle>
                      <CardDescription>Завершить сеанс</CardDescription>
                    </CardHeader>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        )}

        {view === 'profile' && user && (
          <Card className="max-w-2xl mx-auto animate-scale-in shadow-2xl border-0 bg-white/80 backdrop-blur">
            <CardHeader className="space-y-4 text-center">
              <div className="mx-auto w-24 h-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4 animate-fade-in">
                <Icon name="UserCircle" className="text-white" size={48} />
              </div>
              <CardTitle className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Профиль пользователя
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4 animate-slide-in">
                <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-6 rounded-xl">
                  <Label className="text-sm text-gray-600 font-semibold">Полное имя</Label>
                  <p className="text-2xl font-bold text-gray-800 mt-1">{user.full_name}</p>
                </div>
                
                <div className="bg-gradient-to-r from-blue-100 to-purple-100 p-6 rounded-xl animate-slide-in" style={{ animationDelay: '0.1s' }}>
                  <Label className="text-sm text-gray-600 font-semibold">Email</Label>
                  <p className="text-2xl font-bold text-gray-800 mt-1">{user.email}</p>
                </div>
                
                <div className="bg-gradient-to-r from-pink-100 to-red-100 p-6 rounded-xl animate-slide-in" style={{ animationDelay: '0.2s' }}>
                  <Label className="text-sm text-gray-600 font-semibold">ID пользователя</Label>
                  <p className="text-2xl font-bold text-gray-800 mt-1">#{user.id}</p>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  onClick={() => setView('home')}
                  variant="outline"
                  className="flex-1 border-2 hover:bg-purple-100 transition-all"
                >
                  <Icon name="ArrowLeft" size={20} className="mr-2" />
                  Назад
                </Button>
                <Button
                  onClick={handleLogout}
                  className="flex-1 bg-gradient-to-r from-pink-600 to-red-600 hover:from-pink-700 hover:to-red-700 text-white transition-all hover:scale-105"
                >
                  <Icon name="LogOut" size={20} className="mr-2" />
                  Выйти
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
