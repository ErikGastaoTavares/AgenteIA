import { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import axios from 'axios';
import Link from 'next/link';

export default function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      setError('Por favor, preencha todos os campos.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/login', {
        username,
        password
      });
      
      if (response.data.success) {
        // Store user in localStorage or context
        localStorage.setItem('user', response.data.user);
        router.push('/admin/dashboard');
      } else {
        setError('Usuário ou senha inválidos.');
      }
    } catch (err) {
      console.error('Error logging in:', err);
      setError('Erro ao realizar login. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Head>
        <title>Login - Sistema de Triagem</title>
        <meta name="description" content="Login para o Sistema de Triagem" />
        <link rel="icon" href="https://hci.org.br/wp-content/uploads/2023/07/cropped-fav-150x150.png" />
      </Head>

      <div className="container" style={{ position: 'relative' }}>
        <Link href="/">
          <button 
            style={{
              position: 'absolute',
              top: '20px',
              left: '20px',
              background: 'var(--hci-azul)',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold'
            }}
          >
            ← VOLTAR PARA TRIAGEM
          </button>
        </Link>

        <div style={{ textAlign: 'center', marginBottom: '2rem', marginTop: '2rem' }}>
          <img 
            src="https://hci.org.br/wp-content/uploads/2024/09/logo.png" 
            alt="Logo HCI" 
            style={{ maxWidth: '300px', marginBottom: '1rem' }}
          />
          <h2 className='admin-title' style={{fontSize: '1.5rem', marginTop: '0.5rem' }}>
            Painel de Validação de Triagens
          </h2>
        </div>

        <div className="login-container">
          <h2 className="login-title">Login do Sistema</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username" className="form-label">
                Usuário
              </label>
              <input
                id="username"
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Senha
              </label>
              <input
                id="password"
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite sua senha"
              />
            </div>
            
            {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}
            
            <button 
              type="submit" 
              className="button login-button"
              disabled={loading}
            >
              {loading ? 'ENTRANDO...' : 'ENTRAR'}
            </button>
          </form>
        </div>

        <div style={{
          background: 'var(--hci-azul)',
          color: 'white',
          padding: '1.5rem',
          borderRadius: '10px',
          marginTop: '2rem',
          textAlign: 'center',
          maxWidth: '600px',
          margin: '2rem auto 0 auto'
        }}>
          <h3 style={{ color: 'white', marginBottom: '1rem' }}>Credenciais para Demonstração</h3>
          <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap' }}>
            <div style={{ margin: '0.5rem' }}>
              <strong>Admin:</strong><br />
              admin / admin
            </div>
            <div style={{ margin: '0.5rem' }}>
              <strong>Médico:</strong><br />
              medico / medico
            </div>
            <div style={{ margin: '0.5rem' }}>
              <strong>Enfermeiro:</strong><br />
              enfermeiro / enfermeiro
            </div>
          </div>
        </div>

        <footer className="footer">
          <p style={{ margin: '0.5rem 0', fontWeight: 'bold' }}>Sistema de Validação de Triagens Clínicas</p>
          <p style={{ margin: '0.5rem 0' }}>Hospital de Clínicas de Ijuí</p>
          <p style={{ margin: '0.5rem 0' }}>© 2025 - Todos os direitos reservados</p>
        </footer>
      </div>
    </div>
  );
}