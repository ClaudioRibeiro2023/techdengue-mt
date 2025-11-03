/**
 * Chatbot FSM (Finite State Machine) para Triagem de Denúncias
 * Classifica denúncias em 3 níveis: ALTO, MEDIO, BAIXO
 */
import React, { useState, useEffect } from 'react';
import { MessageCircle, Send } from 'lucide-react';
import type { ChatbotResposta, DenunciaPrioridade } from '@/types/denuncia';

// Estados da máquina de estados
type ChatbotState = 
  | 'inicio'
  | 'agua_parada'
  | 'larvas'
  | 'lixo'
  | 'classificacao'
  | 'fim';

interface ChatbotOption {
  texto: string;
  proximo?: ChatbotState;
  classificacao?: DenunciaPrioridade;
}

interface ChatbotStep {
  pergunta?: string;
  mensagem?: string;
  opcoes?: ChatbotOption[];
}

// Definição do fluxo do chatbot
const chatbotFlow: Record<ChatbotState, ChatbotStep> = {
  inicio: {
    pergunta: '🚨 Vamos identificar a gravidade da situação. Você viu água parada no local?',
    opcoes: [
      { texto: 'Sim', proximo: 'larvas' },
      { texto: 'Não', proximo: 'lixo' }
    ]
  },
  agua_parada: {
    pergunta: 'A água está parada há quanto tempo?',
    opcoes: [
      { texto: 'Mais de 1 semana', proximo: 'larvas' },
      { texto: 'Menos de 1 semana', proximo: 'larvas' }
    ]
  },
  larvas: {
    pergunta: '🔍 Há larvas visíveis na água (pequenos "vermes" se movendo)?',
    opcoes: [
      { texto: 'Sim, vejo larvas', classificacao: 'ALTO', proximo: 'classificacao' },
      { texto: 'Não vejo larvas', classificacao: 'MEDIO', proximo: 'classificacao' },
      { texto: 'Não sei identificar', classificacao: 'MEDIO', proximo: 'classificacao' }
    ]
  },
  lixo: {
    pergunta: '🗑️ Há lixo, entulho ou objetos que podem acumular água no local?',
    opcoes: [
      { texto: 'Sim, há lixo acumulado', classificacao: 'MEDIO', proximo: 'classificacao' },
      { texto: 'Não há lixo', classificacao: 'BAIXO', proximo: 'classificacao' }
    ]
  },
  classificacao: {
    mensagem: 'Entendi. Vou registrar sua denúncia.',
    opcoes: []
  },
  fim: {
    mensagem: '✅ Denúncia classificada com sucesso!',
    opcoes: []
  }
};

// Descrição de cada prioridade
const prioridadeInfo: Record<DenunciaPrioridade, { emoji: string; label: string; descricao: string; cor: string }> = {
  ALTO: {
    emoji: '🔴',
    label: 'Prioridade ALTA',
    descricao: 'Larvas visíveis indicam risco iminente. Equipe será acionada rapidamente.',
    cor: 'bg-red-50 border-red-200 text-red-800'
  },
  MEDIO: {
    emoji: '🟡',
    label: 'Prioridade MÉDIA',
    descricao: 'Situação requer atenção. Vistoria será agendada em breve.',
    cor: 'bg-yellow-50 border-yellow-200 text-yellow-800'
  },
  BAIXO: {
    emoji: '🟢',
    label: 'Prioridade BAIXA',
    descricao: 'Denúncia registrada. Será analisada junto com outras do bairro.',
    cor: 'bg-green-50 border-green-200 text-green-800'
  }
};

interface ChatbotFSMProps {
  onComplete: (respostas: ChatbotResposta[], classificacao: DenunciaPrioridade, duracao: number) => void;
}

interface Message {
  tipo: 'bot' | 'usuario';
  texto: string;
  timestamp: Date;
}

const ChatbotFSM: React.FC<ChatbotFSMProps> = ({ onComplete }) => {
  const [currentState, setCurrentState] = useState<ChatbotState>('inicio');
  const [messages, setMessages] = useState<Message[]>([]);
  const [respostas, setRespostas] = useState<ChatbotResposta[]>([]);
  const [classificacao, setClassificacao] = useState<DenunciaPrioridade | null>(null);
  const [inicioTimestamp] = useState<number>(Date.now());
  const [isTyping, setIsTyping] = useState(false);

  // Inicializar com primeira pergunta
  useEffect(() => {
    const step = chatbotFlow[currentState];
    if (step.pergunta) {
      addBotMessage(step.pergunta);
    }
  }, []);

  const addBotMessage = (texto: string) => {
    setIsTyping(true);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { tipo: 'bot', texto, timestamp: new Date() }
      ]);
      setIsTyping(false);
    }, 500); // Simula "digitando"
  };

  const handleOptionClick = (option: ChatbotOption) => {
    const currentStep = chatbotFlow[currentState];
    
    // Adicionar resposta do usuário
    setMessages((prev) => [
      ...prev,
      { tipo: 'usuario', texto: option.texto, timestamp: new Date() }
    ]);

    // Salvar resposta
    const novaResposta: ChatbotResposta = {
      pergunta: currentStep.pergunta || '',
      resposta: option.texto,
      timestamp: new Date().toISOString()
    };
    
    const novasRespostas = [...respostas, novaResposta];
    setRespostas(novasRespostas);

    // Se tem classificação, salvar
    if (option.classificacao) {
      setClassificacao(option.classificacao);
    }

    // Próximo estado
    if (option.proximo) {
      const nextState = option.proximo;
      setCurrentState(nextState);
      
      const nextStep = chatbotFlow[nextState];
      
      if (nextStep.pergunta) {
        addBotMessage(nextStep.pergunta);
      } else if (nextStep.mensagem && option.classificacao) {
        // Mostrar resultado da classificação
        const info = prioridadeInfo[option.classificacao];
        const mensagemFinal = `${info.emoji} ${info.label}\n\n${info.descricao}`;
        addBotMessage(mensagemFinal);
        
        // Completar após 2 segundos
        setTimeout(() => {
          const duracaoSegundos = Math.floor((Date.now() - inicioTimestamp) / 1000);
          onComplete(novasRespostas, option.classificacao!, duracaoSegundos);
        }, 2000);
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b">
        <div className="bg-blue-100 p-3 rounded-full">
          <MessageCircle className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Assistente de Triagem</h2>
          <p className="text-sm text-gray-600">Vou ajudar a classificar sua denúncia</p>
        </div>
      </div>

      {/* Messages */}
      <div className="space-y-4 mb-6 min-h-[300px] max-h-[400px] overflow-y-auto">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.tipo === 'usuario' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.tipo === 'usuario'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.texto}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {msg.timestamp.toLocaleTimeString('pt-BR', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Options */}
      {!isTyping && chatbotFlow[currentState].opcoes && chatbotFlow[currentState].opcoes!.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-gray-600 mb-3">Selecione uma opção:</p>
          {chatbotFlow[currentState].opcoes!.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleOptionClick(option)}
              className="w-full flex items-center justify-between px-4 py-3 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <span className="text-gray-900">{option.texto}</span>
              <Send className="w-4 h-4 text-gray-400" />
            </button>
          ))}
        </div>
      )}

      {/* Progress indicator */}
      {classificacao && (
        <div className={`mt-4 p-4 rounded-lg border-2 ${prioridadeInfo[classificacao].cor}`}>
          <div className="flex items-center gap-2">
            <span className="text-2xl">{prioridadeInfo[classificacao].emoji}</span>
            <div>
              <p className="font-semibold">{prioridadeInfo[classificacao].label}</p>
              <p className="text-sm">{prioridadeInfo[classificacao].descricao}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatbotFSM;
