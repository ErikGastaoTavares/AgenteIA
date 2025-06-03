import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import axios from 'axios';

export default function Home() {
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [validationSent, setValidationSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!symptoms.trim()) {
      setError('Por favor, insira os sintomas do paciente.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Usar endpoint que apenas processa, sem salvar no banco
      const response = await axios.post('http://localhost:8000/api/processar-triagem', {
        sintomas: symptoms
      });
      
      setResult(response.data);
      setValidationSent(false); // Reset validation status
    } catch (err) {
      console.error('Error processing triage:', err);
      setError('Erro ao processar a triagem. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const sendForValidation = async () => {
    if (!result) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Agora sim, salvar no banco para validação
      const response = await axios.post('http://localhost:8000/api/triagem', {
        sintomas: symptoms,
        classificacao: result.classificacao,
        justificativa: result.justificativa,
        condutas: result.condutas
      });
      
      if (response.data.success || response.data.id) {
        setValidationSent(true);
        // Atualizar o result com o ID retornado do banco
        setResult({
          ...result,
          id: response.data.id || response.data.triagem_id
        });
      } else {
        setError('Erro ao enviar para validação. Por favor, tente novamente.');
      }
    } catch (err) {
      console.error('Error sending for validation:', err);
      setError('Erro ao enviar para validação. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const getClassificationColor = (classification) => {
    const classLower = classification.toLowerCase();
    if (classLower === 'vermelho') return 'classification-red';
    if (classLower === 'laranja') return 'classification-orange';
    if (classLower === 'amarelo') return 'classification-yellow';
    if (classLower === 'verde') return 'classification-green';
    if (classLower === 'azul') return 'classification-blue';
    return '';
  };

  const getClassificationEmoji = (classification) => {
    const classLower = classification.toLowerCase();
    if (classLower === 'vermelho') return '🔴';
    if (classLower === 'laranja') return '🟠';
    if (classLower === 'amarelo') return '🟡';
    if (classLower === 'verde') return '🟢';
    if (classLower === 'azul') return '🔵';
    return '';
  };

  const getClassificationText = (classification) => {
    const classLower = classification.toLowerCase();
    if (classLower === 'vermelho') return 'EMERGÊNCIA (VERMELHO)';
    if (classLower === 'laranja') return 'MUITO URGENTE (LARANJA)';
    if (classLower === 'amarelo') return 'URGENTE (AMARELO)';
    if (classLower === 'verde') return 'POUCO URGENTE (VERDE)';
    if (classLower === 'azul') return 'NÃO URGENTE (AZUL)';
    return classification.toUpperCase();
  };

  return (
    <div>
      <Head>
        <title>Sistema de Triagem</title>
        <meta name="description" content="Sistema de Triagem baseado no Protocolo de Manchester" />
        <link rel="icon" type="image/png" href="https://hci.org.br/wp-content/uploads/2023/07/cropped-fav-150x150.png" />
        <link rel="shortcut icon" type="image/png" href="https://hci.org.br/wp-content/uploads/2024/09/logo-300x67.png" />
      </Head>

      <div className="container">
        <header className="header">
          <div className="logo-container">
            <img 
              src="https://hci.org.br/wp-content/uploads/2024/09/logo-300x67.png"
              alt="Logo HCI" 
              className="logo" 
            />
            <h2 className="title" style={{ marginTop: '50px' }}>Sistema de Triagem</h2>
          </div>
          <Link href="/admin">
            <button className="admin-button">
              ÁREA ADMINISTRATIVA
            </button>
          </Link>
        </header>

        <main>
          <div className="form-container">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="symptoms" className="form-label">
                  Descreva os sintomas do paciente
                </label>
                <textarea
                  id="symptoms"
                  className="form-textarea"
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="Exemplo: Paciente masculino apresenta febre alta, tosse seca e dificuldade para respirar."
                  rows={5}
                />
              </div>
              {error && <p style={{ color: 'red' }}>{error}</p>}
              <button 
                type="submit" 
                className="button"
                disabled={loading}
              >
                {loading ? 'Classificando...' : 'Classificar e gerar conduta'}
              </button>
            </form>
          </div>

          {result && (
            <div className="result-container">
              <h2>Resultado da Triagem</h2>
              
              <div className={`classification ${getClassificationColor(result.classificacao)}`}>
                <h3>
                  {getClassificationEmoji(result.classificacao)} Classificação: {getClassificationText(result.classificacao)}
                </h3>
              </div>
              
              <div className="section">
                <h3 className="section-title">Análise Clínica</h3>
                <p>{result.justificativa}</p>
              </div>
              
              <div className="section">
                <h3 className="section-title">Condutas Recomendadas</h3>
                <p>{result.condutas}</p>
              </div>
              
              {!validationSent ? (
                <button 
                  onClick={sendForValidation} 
                  className="button"
                  disabled={loading}
                  style={{ marginTop: '1rem' }}
                >
                  {loading ? 'Enviando...' : 'Enviar para validação por especialistas'}
                </button>
              ) : (
                <div className="card card-success" style={{ marginTop: '1rem' }}>
                  <p>✅Triagem enviada para validação com sucesso!</p>
                  <p>ID de Rastreamento: {result.id}</p>
                  <p>A triagem será revisada por especialistas clínicos para garantir a precisão da classificação e das condutas sugeridas.</p>
                </div>
              )}
            </div>
          )}
        </main>

        <footer className="footer">
          <p>Sistema desenvolvido conforme o Protocolo de Manchester</p>
        </footer>
      </div>
    </div>
  );
}