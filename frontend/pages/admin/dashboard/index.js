import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import axios from 'axios';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [stats, setStats] = useState({ total: 0, validadas: 0, pendentes: 0 });
  const [triagens, setTriagens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [validatingTriagem, setValidatingTriagem] = useState(null);
  const [feedback, setFeedback] = useState('');
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const loggedInUser = localStorage.getItem('user');
    if (!loggedInUser) {
      router.push('/admin');
      return;
    }
    
    setUser(loggedInUser);
    
    // Load initial data
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const statsResponse = await axios.get('http://localhost:8000/api/estatisticas');
      setStats(statsResponse.data);
      
      // Load triagens based on active menu
      if (activeMenu === 'dashboard' || activeMenu === 'pendentes') {
        const triagensResponse = await axios.get('http://localhost:8000/api/triagens?filtro=pendentes');
        setTriagens(triagensResponse.data.triagens);
      } else if (activeMenu === 'todas') {
        const triagensResponse = await axios.get('http://localhost:8000/api/triagens?filtro=todas');
        setTriagens(triagensResponse.data.triagens);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Erro ao carregar dados. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuClick = async (menu) => {
    setActiveMenu(menu);
    setLoading(true);
    
    try {
      if (menu === 'pendentes') {
        const response = await axios.get('http://localhost:8000/api/triagens?filtro=pendentes');
        setTriagens(response.data.triagens);
      } else if (menu === 'todas') {
        const response = await axios.get('http://localhost:8000/api/triagens?filtro=todas');
        setTriagens(response.data.triagens);
      } else if (menu === 'dashboard') {
        await fetchDashboardData();
      }
    } catch (err) {
      console.error('Error changing menu:', err);
      setError('Erro ao carregar dados. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (triagem) => {
    if (!triagem || !triagem.id) return;
    setValidatingTriagem(triagem);
    setFeedback('');
  };

  const submitValidation = async () => {
    if (!feedback.trim()) {
      alert('Por favor, digite um feedback.');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await axios.post('http://localhost:8000/api/validar', {
        triagem_id: validatingTriagem.id,
        validado_por: user,
        feedback
      });
      
      if (response.data.success) {
        alert('Triagem validada com sucesso!');
        setValidatingTriagem(null);
        setFeedback('');
        fetchDashboardData(); // Refresh data
      } else {
        alert('Erro ao validar triagem. Por favor, tente novamente.');
      }
    } catch (err) {
      console.error('Error validating triage:', err);
      alert('Erro ao validar triagem. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const cancelValidation = () => {
    setValidatingTriagem(null);
    setFeedback('');
  };

  const getClassificationColor = (classification) => {
    const classLower = classification?.toLowerCase();
    if (classLower === 'vermelho') return 'classification-red';
    if (classLower === 'laranja') return 'classification-orange';
    if (classLower === 'amarelo') return 'classification-yellow';
    if (classLower === 'verde') return 'classification-green';
    if (classLower === 'azul') return 'classification-blue';
    return '';
  };

  const getClassificationText = (classification) => {
    const classLower = classification?.toLowerCase();
    if (classLower === 'vermelho') return 'EMERGÊNCIA (VERMELHO)';
    if (classLower === 'laranja') return 'MUITO URGENTE (LARANJA)';
    if (classLower === 'amarelo') return 'URGENTE (AMARELO)';
    if (classLower === 'verde') return 'POUCO URGENTE (VERDE)';
    if (classLower === 'azul') return 'NÃO URGENTE (AZUL)';
    return classification?.toUpperCase();
  };

  // Render validation page
  const renderValidationPage = () => {
    const triagem = validatingTriagem;
    
    return (
      <div>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '2rem' 
        }}>
          <h2 style={{ color: '#003B71', margin: 0 }}>
            Validação de Triagem
          </h2>
          <button 
            className="button"
            onClick={cancelValidation}
            style={{ 
              background: '#6c757d',
              marginBottom: 0 
            }}
          >
            ← Voltar
          </button>
        </div>

        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h3 style={{ color: '#003B71', marginBottom: '1rem' }}>
            Informações da Triagem
          </h3>
          
          <div style={{ marginBottom: '1rem' }}>
            <strong>ID:</strong> {triagem.id}
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <strong>Data/Hora:</strong> {triagem.data_hora}
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <strong>Sintomas do Paciente:</strong>
            <div style={{ 
              background: '#f8f9fa', 
              padding: '1rem', 
              borderRadius: '5px', 
              marginTop: '0.5rem',
              border: '1px solid #dee2e6'
            }}>
              {triagem.sintomas}
            </div>
          </div>

          {triagem.classificacao && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Classificação IA:</strong>
              <div className={`classification ${getClassificationColor(triagem.classificacao)}`} 
                   style={{ marginTop: '0.5rem', padding: '0.5rem', borderRadius: '5px' }}>
                {getClassificationText(triagem.classificacao)}
              </div>
            </div>
          )}

          {triagem.justificativa && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Análise Clínica da IA:</strong>
              <div style={{ 
                background: '#f8f9fa', 
                padding: '1rem', 
                borderRadius: '5px', 
                marginTop: '0.5rem',
                border: '1px solid #dee2e6'
              }}>
                {triagem.justificativa}
              </div>
            </div>
          )}

          {triagem.condutas && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Condutas Recomendadas pela IA:</strong>
              <div style={{ 
                background: '#f8f9fa', 
                padding: '1rem', 
                borderRadius: '5px', 
                marginTop: '0.5rem',
                border: '1px solid #dee2e6'
              }}>
                {triagem.condutas}
              </div>
            </div>
          )}
        </div>

        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ color: '#003B71', marginBottom: '1rem' }}>
            Validação do Especialista
          </h3>
          
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 'bold',
              color: '#003B71'
            }}>
              Feedback de Validação:
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Digite seu feedback sobre esta triagem. Inclua se concorda com a classificação, se há algo a corrigir, observações clínicas, etc."
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '1rem',
                border: '2px solid #dee2e6',
                borderRadius: '8px',
                fontSize: '14px',
                fontFamily: 'inherit',
                resize: 'vertical',
                marginBottom: '1rem'
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem', fontSize: '14px', color: '#6c757d' }}>
            <strong>Validado por:</strong> {user}
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              className="button"
              onClick={submitValidation}
              disabled={loading || !feedback.trim()}
              style={{ marginBottom: 0 }}
            >
              {loading ? 'Validando...' : 'Confirmar Validação'}
            </button>
            <button 
              className="button"
              onClick={cancelValidation}
              style={{ 
                background: '#6c757d',
                marginBottom: 0
              }}
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    );
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    router.push('/admin');
  };

  const renderContent = () => {
    // If validating a triagem, show validation page
    if (validatingTriagem) {
      return renderValidationPage();
    }

    if (activeMenu === 'dashboard') {
      return (
        <>
          <div className="dashboard-header">
            <h2 style={{ color: '#003B71', margin: 0 }}>Dashboard - Estatísticas do Sistema</h2>
          </div>
          
          <div className="stats-container">
            <div className="stat-card stat-total">
              <h3 style={{ color: '#003B71' }}>Total de Triagens</h3>
              <h1 style={{ color: '#003B71' }}>{stats.total}</h1>
            </div>
            
            <div className="stat-card stat-validated">
              <h3 style={{ color: '#009B3A' }}>Validadas</h3>
              <h1 style={{ color: '#009B3A' }}>{stats.validadas}</h1>
            </div>
            
            <div className="stat-card stat-pending">
              <h3 style={{ color: '#FF7F00' }}>Pendentes</h3>
              <h1 style={{ color: '#FF7F00' }}>{stats.pendentes}</h1>
            </div>
          </div>
          
          {stats.pendentes > 0 && (
            <div className="section">
              <h3 className="section-title">Triagens Pendentes Recentes</h3>
              {renderTriagensList(triagens.slice(0, 5))}
            </div>
          )}
        </>
      );
    } else if (activeMenu === 'pendentes' || activeMenu === 'todas') {
      const title = activeMenu === 'pendentes' ? 'Triagens Pendentes' : 'Todas as Triagens';
      
      return (
        <>
          <div className="dashboard-header">
            <h2 style={{ color: '#003B71', margin: 0 }}>{title}</h2>
          </div>
          
          {triagens.length > 0 ? (
            renderTriagensList(triagens)
          ) : (
            <p>Nenhuma triagem encontrada.</p>
          )}
        </>
      );
    } else if (activeMenu === 'conhecimento') {
      return (
        <>
          <div className="dashboard-header">
            <h2 style={{ color: '#003B71', margin: 0 }}>Banco de Conhecimento</h2>
          </div>
          
          <div className="card">
            <p>🚧 Funcionalidade em desenvolvimento - Visualização de casos validados e padrões identificados.</p>
          </div>
        </>
      );
    } else if (activeMenu === 'exportar') {
      return (
        <>
          <div className="dashboard-header">
            <h2 style={{ color: '#003B71', margin: 0 }}>📤 Exportar Dados</h2>
          </div>
          
          <button 
            className="button"
            style={{ marginBottom: '1rem' }}
            onClick={() => alert('Funcionalidade em desenvolvimento')}
          >
            Gerar CSV
          </button>
        </>
      );
    }
  };

  const renderTriagensList = (triagens) => {
    return triagens.map((triagem) => {
      const borderColor = triagem.validado === 1 ? '#009B3A' : '#FF7F00';
      const statusText = triagem.validado === 1 ? 'Validada' : 'Pendente';
      
      return (
        <div 
          key={triagem.id}
          style={{
            background: 'white',
            padding: '1.5rem',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            borderLeft: `4px solid ${borderColor}`,
            marginBottom: '1rem'
          }}
        >
          <h4 style={{ color: '#003B71', marginBottom: '0.5rem' }}>
            ID: {triagem.id.substring(0, 8)}... | {statusText}
          </h4>
          <p style={{ margin: '0.25rem 0', color: '#58595B' }}>
            <strong>Data:</strong> {triagem.data_hora}
          </p>
          <p style={{ margin: '0.25rem 0', color: '#58595B' }}>
            <strong>Sintomas:</strong> {triagem.sintomas.substring(0, 100)}...
          </p>
          
          {triagem.validado === 0 && (
            <button 
              className="button"
              style={{ marginTop: '0.5rem' }}
              onClick={() => handleValidate(triagem)}
            >
              Validar triagem
            </button>
          )}
        </div>
      );
    });
  };

  if (!user) {
    return <div>Redirecionando...</div>;
  }

  return (
    <div>
      <Head>
        <title>Página inicial administrador</title>
        <meta name="description" content="Dashboard do Sistema de Triagem" />
        <link rel="icon" href="https://hci.org.br/wp-content/uploads/2023/07/cropped-fav-150x150.png" />
      </Head>

      <div style={{ minHeight: '100vh' }}>
        {/* Header Navigation */}
        <header style={{
          background: 'var(--hci-azul)',
          color: 'white',
          padding: '1rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            <div>
              <h3 style={{ color: 'white', margin: 0 }}>Bem-vindo, {user.charAt(0).toUpperCase() + user.slice(1)}!</h3>
            </div>
            
            <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <button 
                className={`button ${activeMenu === 'dashboard' ? 'button-active' : ''}`}
                style={{ 
                  background: activeMenu === 'dashboard' ? 'var(--hci-verde)' : 'var(--hci-azul)',
                  marginBottom: 0 
                }}
                onClick={() => handleMenuClick('dashboard')}
              >
                Dashboard
              </button>
              <button 
                className={`button ${activeMenu === 'pendentes' ? 'button-active' : ''}`}
                style={{ 
                  background: activeMenu === 'pendentes' ? 'var(--hci-verde)' : 'var(--hci-azul)',
                  marginBottom: 0 
                }}
                onClick={() => handleMenuClick('pendentes')}
              >
                Pendentes
              </button>
              <button 
                className={`button ${activeMenu === 'todas' ? 'button-active' : ''}`}
                style={{ 
                  background: activeMenu === 'todas' ? 'var(--hci-verde)' : 'var(--hci-azul)',
                  marginBottom: 0 
                }}
                onClick={() => handleMenuClick('todas')}
              >
                Todas
              </button>
              <button 
                className={`button ${activeMenu === 'conhecimento' ? 'button-active' : ''}`}
                style={{ 
                  background: activeMenu === 'conhecimento' ? 'var(--hci-verde)' : 'var(--hci-azul)',
                  marginBottom: 0 
                }}
                onClick={() => handleMenuClick('conhecimento')}
              >
                Conhecimento
              </button>
              <button 
                className={`button ${activeMenu === 'exportar' ? 'button-active' : ''}`}
                style={{ 
                  background: activeMenu === 'exportar' ? 'var(--hci-verde)' : 'var(--hci-azul)',
                  marginBottom: 0 
                }}
                onClick={() => handleMenuClick('exportar')}
              >
                Exportar
              </button>
              
              <button 
                className="button"
                style={{ 
                  background: '#dc3545',
                  marginBottom: 0,
                  marginLeft: '1rem' 
                }}
                onClick={handleLogout}
              >
                Logout
              </button>
            </nav>
          </div>
        </header>
        
        {/* Main content */}
        <main style={{ 
          padding: '2rem', 
          maxWidth: '1200px', 
          margin: '0 auto' 
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <p>Carregando...</p>
            </div>
          ) : error ? (
            <div style={{ color: 'red', padding: '1rem' }}>
              <p>{error}</p>
              <button 
                className="button"
                onClick={fetchDashboardData}
              >
                Tentar novamente
              </button>
            </div>
          ) : (
            renderContent()
          )}
        </main>
      </div>
    </div>
  );
}