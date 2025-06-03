"""
Módulo para fornecer respostas simuladas quando o Ollama não estiver disponível
"""

def get_mock_response(sintomas):
    """
    Retorna uma resposta simulada baseada nos sintomas
    
    Args:
        sintomas: String com os sintomas do paciente
        
    Returns:
        String com a resposta simulada
    """
    sintomas_lower = sintomas.lower()
    
    # Caso de emergência (vermelho)
    if any(termo in sintomas_lower for termo in ["parada", "inconsciente", "choque", "não responde", "sangramento intenso"]):
        return """Classificação
vermelho

Justificativa
Paciente apresenta sinais de comprometimento crítico das funções vitais com necessidade de intervenção imediata. A alteração do nível de consciência associada à instabilidade hemodinâmica indica risco iminente de morte se não houver intervenção rápida.

Condutas
- Acesso venoso calibroso imediato
- Monitorização contínua de sinais vitais
- Avaliação médica imediata (tempo zero)
- Preparo para suporte avançado de vida
- Exames laboratoriais de emergência (gasometria, eletrólitos, hemograma)"""

    # Caso muito urgente (laranja)
    elif any(termo in sintomas_lower for termo in ["dor torácica", "dispneia grave", "confusão", "convulsão"]):
        return """Classificação
laranja

Justificativa
Paciente apresenta sintomas sugestivos de condição potencialmente ameaçadora à vida. A dor torácica associada a outros sintomas pode indicar síndrome coronariana aguda que requer avaliação e intervenção rápidas para prevenir complicações graves.

Condutas
- Monitorização cardíaca
- Acesso venoso periférico
- ECG de 12 derivações em até 10 minutos
- Avaliação médica em até 10 minutos
- Coleta de enzimas cardíacas
- Administração de AAS conforme protocolo"""

    # Caso urgente (amarelo)
    elif any(termo in sintomas_lower for termo in ["febre alta", "vômitos", "desidratação", "dor moderada"]):
        return """Classificação
amarelo

Justificativa
Paciente apresenta sintomas compatíveis com processo infeccioso agudo. A febre elevada associada à taquicardia sugere necessidade de avaliação médica em prazo reduzido para investigação etiológica e início de tratamento apropriado.

Condutas
- Verificar sinais vitais completos
- Solicitar hemograma completo e PCR
- Administrar antitérmico se necessário
- Reavaliação médica em até 60 minutos"""

    # Caso pouco urgente (verde)
    elif any(termo in sintomas_lower for termo in ["dor leve", "tosse", "resfriado", "mal estar"]):
        return """Classificação
verde

Justificativa
Paciente apresenta quadro clínico estável com sintomas de início recente, sem sinais de alerta. Os sinais vitais encontram-se dentro dos parâmetros normais e não há indicativos de deterioração iminente.

Condutas
- Verificar sinais vitais
- Avaliação médica em até 120 minutos
- Orientações sobre sintomáticos
- Retorno se piora ou persistência dos sintomas"""

    # Caso não urgente (azul)
    elif any(termo in sintomas_lower for termo in ["renovação", "atestado", "crônico", "consulta de rotina"]):
        return """Classificação
azul

Justificativa
Paciente em condição crônica estável, sem alterações agudas. Apresenta-se para atendimento eletivo sem caracterização de urgência ou emergência. Sinais vitais estáveis e sem queixas de dor ou desconforto significativo.

Condutas
- Verificar sinais vitais
- Encaminhar para atendimento ambulatorial
- Orientar sobre agendamento de consulta eletiva
- Avaliação médica conforme disponibilidade do serviço"""

    # Caso padrão (amarelo)
    else:
        return """Classificação
amarelo

Justificativa
Paciente apresenta quadro clínico que requer avaliação médica em tempo oportuno. Os sintomas descritos sugerem condição que, embora não represente risco imediato à vida, necessita de investigação para prevenir complicações.

Condutas
- Verificar sinais vitais a cada 60 minutos
- Avaliação médica em até 60 minutos
- Exames laboratoriais conforme avaliação médica
- Medicação sintomática conforme prescrição
- Orientar retorno imediato se piora dos sintomas"""