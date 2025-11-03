/**
 * Página de Nova Denúncia Pública (e-Denúncia)
 * Módulo PoC - Fase P (ELIMINATÓRIA)
 * 
 * Fluxo:
 * 1. Chatbot FSM para triagem
 * 2. Formulário de localização + descrição
 * 3. Upload de foto (opcional)
 * 4. Captura GPS automática
 * 5. Envio + fallback offline
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Camera, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import ChatbotFSM from '@/modules/eDenuncia/ChatbotFSM';
import type { 
  DenunciaCreate,
  ChatbotResposta, 
  DenunciaPrioridade,
  CoordenadasGPS 
} from '@/types/denuncia';
import { enqueueDenuncia, syncQueue } from '@/lib/offlineQueue'

type Step = 'chatbot' | 'formulario' | 'enviando' | 'sucesso';

// Lista simplificada de municípios MT (os 10 maiores)
const MUNICIPIOS_MT = [
  { codigo: '5103403', nome: 'Cuiabá' },
  { codigo: '5107909', nome: 'Várzea Grande' },
  { codigo: '5103809', nome: 'Rondonópolis' },
  { codigo: '5106224', nome: 'Sinop' },
  { codigo: '5106455', nome: 'Tangará da Serra' },
  { codigo: '5100201', nome: 'Alta Floresta' },
  { codigo: '5100250', nome: 'Alto Araguaia' },
  { codigo: '5101001', nome: 'Barra do Garças' },
  { codigo: '5101209', nome: 'Cáceres' },
  { codigo: '5105507', nome: 'Pontes e Lacerda' }
];

const NovaDenunciaPage: React.FC = () => {
  const navigate = useNavigate();
  
  // States do fluxo
  const [step, setStep] = useState<Step>('chatbot');
  const [chatbotRespostas, setChatbotRespostas] = useState<ChatbotResposta[]>([]);
  const [classificacao, setClassificacao] = useState<DenunciaPrioridade>('MEDIO');
  const [duracaoChatbot, setDuracaoChatbot] = useState<number>(0);
  
  // States do formulário
  const [endereco, setEndereco] = useState('');
  const [bairro, setBairro] = useState('');
  const [municipioCodigo, setMunicipioCodigo] = useState('5103403'); // Cuiabá default
  const [descricao, setDescricao] = useState('');
  const [fotoFile, setFotoFile] = useState<File | null>(null);
  const [fotoPreview, setFotoPreview] = useState<string | null>(null);
  
  // Contato (opcional)
  const [contatoNome, setContatoNome] = useState('');
  const [contatoTelefone, setContatoTelefone] = useState('');
  const [contatoAnonimo, setContatoAnonimo] = useState(false);
  
  // GPS
  const [coordenadas, setCoordenadas] = useState<CoordenadasGPS | null>(null);
  const [gpsError, setGpsError] = useState<string | null>(null);
  const [capturandoGPS, setCapturandoGPS] = useState(false);
  
  // Resposta da API
  const [numeroProtocolo, setNumeroProtocolo] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [offlineEnfileirada, setOfflineEnfileirada] = useState(false);
  const [copiado, setCopiado] = useState(false);

  // Capturar GPS ao carregar formulário
  useEffect(() => {
    if (step === 'formulario' && !coordenadas) {
      capturarGPS();
    }
  }, [step, coordenadas]);

  useEffect(() => {
    syncQueue();
    const onOnline = () => { syncQueue(); };
    window.addEventListener('online', onOnline);
    return () => window.removeEventListener('online', onOnline);
  }, []);

  const capturarGPS = () => {
    if (!navigator.geolocation) {
      setGpsError('Seu navegador não suporta geolocalização');
      return;
    }

    setCapturandoGPS(true);
    setGpsError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoordenadas({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          precisao: position.coords.accuracy
        });
        setCapturandoGPS(false);
      },
      (error) => {
        console.error('Erro ao capturar GPS:', error);
        setGpsError('Não foi possível obter sua localização. Por favor, autorize o acesso.');
        setCapturandoGPS(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  const handleChatbotComplete = (
    respostas: ChatbotResposta[],
    classe: DenunciaPrioridade,
    duracao: number
  ) => {
    setChatbotRespostas(respostas);
    setClassificacao(classe);
    setDuracaoChatbot(duracao);
    setStep('formulario');
  };

  const handleFotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        alert('Foto muito grande. Máximo 5MB.');
        return;
      }
      setFotoFile(file);
      setFotoPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validações
    if (!coordenadas) {
      alert('Aguarde a captura do GPS ou tente novamente');
      capturarGPS();
      return;
    }

    if (!endereco || !bairro || !descricao) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }

    setStep('enviando');
    setErro(null);

    let foto_url: string | undefined;
    try {
      // 1. Upload foto (se houver)
      if (fotoFile) {
        const formData = new FormData();
        formData.append('file', fotoFile);
        
        const uploadRes = await fetch('/api/upload/foto', {
          method: 'POST',
          body: formData,
        });
        
        if (!uploadRes.ok) {
          const uploadErr = await uploadRes.json();
          throw new Error(uploadErr.detail || 'Erro ao fazer upload da foto');
        }
        
        const uploadData = await uploadRes.json();
        foto_url = uploadData.url; // Caminho relativo para salvar no DB
      }

      // 2. Montar payload
      const payload: DenunciaCreate = {
        endereco,
        bairro,
        municipio_codigo: municipioCodigo,
        coordenadas,
        descricao,
        foto_url,
        chatbot_classificacao: classificacao,
        chatbot_respostas: chatbotRespostas,
        chatbot_duracao_segundos: duracaoChatbot,
        contato_nome: contatoAnonimo ? undefined : contatoNome,
        contato_telefone: contatoAnonimo ? undefined : contatoTelefone,
        contato_anonimo: contatoAnonimo,
        origem: 'WEB',
        user_agent: navigator.userAgent
      };

      if (!navigator.onLine) {
        await enqueueDenuncia(payload);
        setOfflineEnfileirada(true);
        setNumeroProtocolo(null);
        setStep('sucesso');
        return;
      }

      // 3. Enviar para API
      const response = await fetch('/api/denuncias', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao enviar denúncia');
      }

      const result = await response.json();
      setNumeroProtocolo(result.numero_protocolo);
      setStep('sucesso');

    } catch (error) {
      console.error('Erro ao enviar denúncia:', error);
      if (!navigator.onLine) {
        await enqueueDenuncia({
          endereco,
          bairro,
          municipio_codigo: municipioCodigo,
          coordenadas,
          descricao,
          foto_url,
          chatbot_classificacao: classificacao,
          chatbot_respostas: chatbotRespostas,
          chatbot_duracao_segundos: duracaoChatbot,
          contato_nome: contatoAnonimo ? undefined : contatoNome,
          contato_telefone: contatoAnonimo ? undefined : contatoTelefone,
          contato_anonimo: contatoAnonimo,
          origem: 'WEB',
          user_agent: navigator.userAgent
        });
        setOfflineEnfileirada(true);
        setNumeroProtocolo(null);
        setStep('sucesso');
      } else {
        setErro(error instanceof Error ? error.message : 'Erro ao enviar denúncia');
        setStep('formulario');
      }
    }
  };

  // Render por etapa
  if (step === 'chatbot') {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              e-Denúncia - Reporte Focos de Dengue
            </h1>
            <p className="text-gray-600">
              Ajude a combater o mosquito Aedes aegypti em sua região
            </p>
          </div>

          <ChatbotFSM onComplete={handleChatbotComplete} />
        </div>
      </div>
    );
  }

  if (step === 'formulario') {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Dados da Denúncia
            </h2>

            {erro && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-800">Erro ao enviar</p>
                  <p className="text-sm text-red-700">{erro}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* GPS Status */}
              <div className={`p-4 rounded-lg border-2 ${
                coordenadas 
                  ? 'bg-green-50 border-green-200' 
                  : 'bg-yellow-50 border-yellow-200'
              }`}>
                <div className="flex items-center gap-3">
                  <MapPin className={`w-5 h-5 ${
                    coordenadas ? 'text-green-600' : 'text-yellow-600'
                  }`} />
                  <div className="flex-1">
                    {capturandoGPS && (
                      <p className="text-sm text-gray-700">
                        <Loader2 className="w-4 h-4 inline animate-spin mr-2" />
                        Capturando localização GPS...
                      </p>
                    )}
                    {coordenadas && !capturandoGPS && (
                      <p className="text-sm text-green-800">
                        ✓ Localização capturada (precisão: {coordenadas.precisao?.toFixed(0)}m)
                      </p>
                    )}
                    {gpsError && (
                      <p className="text-sm text-red-800">{gpsError}</p>
                    )}
                  </div>
                  {gpsError && (
                    <button
                      type="button"
                      onClick={capturarGPS}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Tentar novamente
                    </button>
                  )}
                </div>
              </div>

              {/* Município */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Município *
                </label>
                <select
                  value={municipioCodigo}
                  onChange={(e) => setMunicipioCodigo(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {MUNICIPIOS_MT.map((mun) => (
                    <option key={mun.codigo} value={mun.codigo}>
                      {mun.nome}
                    </option>
                  ))}
                </select>
              </div>

              {/* Endereço */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Endereço completo *
                </label>
                <input
                  type="text"
                  value={endereco}
                  onChange={(e) => setEndereco(e.target.value)}
                  placeholder="Rua, número, complemento"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                  minLength={5}
                  maxLength={500}
                />
              </div>

              {/* Bairro */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bairro *
                </label>
                <input
                  type="text"
                  value={bairro}
                  onChange={(e) => setBairro(e.target.value)}
                  placeholder="Nome do bairro"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                  minLength={2}
                  maxLength={200}
                />
              </div>

              {/* Descrição */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descrição do problema *
                </label>
                <textarea
                  value={descricao}
                  onChange={(e) => setDescricao(e.target.value)}
                  placeholder="Descreva o que você viu (máximo 500 caracteres)"
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  required
                  minLength={10}
                  maxLength={500}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {descricao.length}/500 caracteres
                </p>
              </div>

              {/* Foto */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Foto (opcional)
                </label>
                <div className="flex items-center gap-4">
                  <label className="cursor-pointer flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg border border-gray-300 transition-colors">
                    <Camera className="w-5 h-5 text-gray-600" />
                    <span className="text-sm text-gray-700">
                      {fotoFile ? 'Alterar foto' : 'Adicionar foto'}
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFotoChange}
                      className="hidden"
                    />
                  </label>
                  {fotoPreview && (
                    <img
                      src={fotoPreview}
                      alt="Preview"
                      className="w-20 h-20 object-cover rounded-lg border border-gray-300"
                    />
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Máximo 5MB. Formatos: JPG, PNG
                </p>
              </div>

              {/* Contato */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Dados para Contato (opcional)
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="anonimo"
                      checked={contatoAnonimo}
                      onChange={(e) => setContatoAnonimo(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <label htmlFor="anonimo" className="text-sm text-gray-700">
                      Prefiro manter anonimato
                    </label>
                  </div>

                  {!contatoAnonimo && (
                    <>
                      <input
                        type="text"
                        value={contatoNome}
                        onChange={(e) => setContatoNome(e.target.value)}
                        placeholder="Seu nome"
                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        maxLength={200}
                      />
                      <input
                        type="tel"
                        value={contatoTelefone}
                        onChange={(e) => setContatoTelefone(e.target.value)}
                        placeholder="Telefone com DDD"
                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        maxLength={20}
                      />
                    </>
                  )}
                </div>
              </div>

              {/* Botões */}
              <div className="flex gap-4 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => setStep('chatbot')}
                  className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
                >
                  Voltar
                </button>
                <button
                  type="submit"
                  disabled={!coordenadas || capturandoGPS}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Enviar Denúncia
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'enviando') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-700">Enviando denúncia...</p>
        </div>
      </div>
    );
  }

  if (step === 'sucesso') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Denúncia Registrada!
          </h2>
          <p className="text-gray-600 mb-6">
            Sua denúncia foi recebida e será analisada em breve.
          </p>
          {offlineEnfileirada && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
              Você está offline. Sua denúncia foi salva e será enviada automaticamente quando a conexão voltar.
            </div>
          )}
          
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-600 mb-1">Número do Protocolo</p>
            <p className="text-2xl font-mono font-bold text-blue-600">
              {numeroProtocolo ?? 'Pendente de sincronização'}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Guarde este número para acompanhar sua denúncia
            </p>
          </div>

          <div className="space-y-3">
            {numeroProtocolo && (
              <div className="flex gap-3">
                <button
                  onClick={async () => { if (numeroProtocolo) { await navigator.clipboard.writeText(numeroProtocolo); setCopiado(true); setTimeout(() => setCopiado(false), 2000); } }}
                  className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
                >
                  {copiado ? 'Copiado!' : 'Copiar Protocolo'}
                </button>
                <a
                  href={`/denuncia/consultar/${numeroProtocolo}`}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-medium text-center hover:bg-green-700 transition-colors"
                >
                  Acompanhar Denúncia
                </a>
              </div>
            )}
            <button
              onClick={() => navigate('/')}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Voltar para Home
            </button>
            <button
              onClick={() => window.location.reload()}
              className="w-full px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Fazer Nova Denúncia
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default NovaDenunciaPage;
