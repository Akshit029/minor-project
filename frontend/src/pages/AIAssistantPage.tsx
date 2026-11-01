import React, { useState, useEffect, useRef } from 'react';
import { WeatherApi } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricValue } from '../components/common/MetricValue';
import type { DistrictName } from '../types/weather';
import {
  Sparkles,
  Send,
  Bot,
  User,
  Clock,
  CheckCircle,
  HelpCircle,
  Sliders,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Key,
  ShieldCheck,
  TrendingDown,
  Zap,
  Check,
  Copy,
  Compass
} from 'lucide-react';

interface ToolCallRecord {
  tool: string;
  input: Record<string, any>;
  output: Record<string, any>;
}

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  toolsCalled?: ToolCallRecord[];
  structuredData?: Record<string, any>;
  isError?: boolean;
  modelUsed?: string;
  geminiActive?: boolean;
}

const EXAMPLE_QUESTIONS = [
  {
    category: 'Reliability',
    label: 'Reliability of Srinagar (Day 2)',
    prompt: 'Explain the reliability of Srinagar on lead day 2.',
    icon: TrendingDown,
  },
  {
    category: 'Comparison',
    label: 'Compare Jammu & Srinagar (Day 3)',
    prompt: 'Compare the reliability of Jammu and Srinagar on lead day 3.',
    icon: Sliders,
  },
  {
    category: 'Theory',
    label: 'What does Reliability Index mean?',
    prompt: 'What does the reliability index mean?',
    icon: HelpCircle,
  },
  {
    category: 'Theory',
    label: 'Reliability vs. Bust Probability',
    prompt: 'What is the difference between reliability and bust probability?',
    icon: ShieldCheck,
  },
  {
    category: 'ML Bust Risk',
    label: 'Estimate Forecast-Bust Risk',
    prompt: 'Estimate forecast-bust risk for this forecast.',
    icon: Zap,
  },
  {
    category: 'Risk Analysis',
    label: 'Explain High Estimated Risk',
    prompt: 'Explain why this prediction has a high estimated risk.',
    icon: Bot,
  },
  {
    category: 'XAI (SHAP)',
    label: 'Global Feature Influence',
    prompt: 'Which features contributed most to predicted bust risk according to SHAP?',
    icon: Compass,
  },
  {
    category: 'XAI (SHAP)',
    label: 'Why Was Event 21 a Bust?',
    prompt: 'Why was the forecast in Baramulla (Event 21) classified as a bust?',
    icon: Zap,
  },
  {
    category: 'Meteorology',
    label: 'Humidity & Wind Influence',
    prompt: 'How do humidity and wind speed relate to forecast errors in the available data?',
    icon: HelpCircle,
  },
];

export const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        '### Welcome to the Weather Reliability AI Assistant\n\n' +
        'I am an agentic assistant orchestrating your **NOAA GFS vs. ECMWF ERA5** verification pipeline across Jammu & Kashmir.\n\n' +
        '**I have direct access to your scientific modules:**\n' +
        '- **Tool A (Reliability Lookup):** Retrieves Week 4 empirical reliability scores $R = R_{\\text{error}} \\times C$, sample confidence $C$, and historical MAE.\n' +
        '- **Tool B (Forecast-Bust Classifier):** Evaluates prospective forecast bust risk via the trained Week 5 ML model.\n' +
        '- **Tool C (Scientific Explanations):** Clarifies the distinction between retrospective reliability and prospective extreme bust risk.\n' +
        '- **Tool D (SHAP Feature Influence):** Explains feature contributions to predicted bust risk and high-error events (Week 7).\n' +
        '- **Tool E (Meteorological Audit):** Audits atmospheric humidity and wind speed availability without fabricating values.\n\n' +
        'Select an example question below or type your query to begin.',
      timestamp: 'Ready',
      modelUsed: 'Scientific-Engine (Agentic)',
      geminiActive: true,
    },
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendHealth, setBackendHealth] = useState<{
    status: string;
    gemini_api_key_configured: boolean;
    configured_model: string;
  } | null>(null);

  // Forecast bust feature assistant drawer state
  const [showBustForm, setShowBustForm] = useState(false);
  const [bustDistrict, setBustDistrict] = useState<DistrictName>('Srinagar');
  const [bustLeadDay, setBustLeadDay] = useState<number>(2);
  const [bustForecastValue, setBustForecastValue] = useState<number>(18.5);
  const [bustInitHour, setBustInitHour] = useState<number>(0);
  const [bustValidHour, setBustValidHour] = useState<number>(12);
  const [bustValidMonth, setBustValidMonth] = useState<number>(9);

  // Expanded tool calls tracker
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    WeatherApi.getHealth().then((health) => {
      setBackendHealth(health);
    });
  }, []);

  const toggleToolExpanded = (msgId: string) => {
    setExpandedTools((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleSendMessage = async (textToSend?: string, customFeatures?: any) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || loading) return;

    const userMsgId = `user-${Date.now()}`;
    const userMsg: MessageItem = {
      id: userMsgId,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    // Prepare history for agent context
    const historyPayload = messages.slice(-6).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const response = await WeatherApi.askAssistant({
        message: text,
        history: historyPayload,
        forecastFeatures: customFeatures,
      });

      const assistantMsgId = `assistant-${Date.now()}`;
      const assistantMsg: MessageItem = {
        id: assistantMsgId,
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        toolsCalled: response.tools_called,
        structuredData: response.structured_data,
        modelUsed: response.model,
        geminiActive: response.gemini_active,
        isError: !!response.error,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsgId = `error-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          id: errMsgId,
          role: 'assistant',
          content: `### Request Processing Error\n\nFailed to receive response from assistant: ${err.message || 'Unknown error'}. Please check if the backend service is running on port 8000.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleBustFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const prompt = `Estimate forecast-bust risk for ${bustDistrict} on lead day ${bustLeadDay} with forecast temperature ${bustForecastValue}°C.`;
    const features = {
      district: bustDistrict,
      lead_hours: bustLeadDay * 24,
      lead_day: bustLeadDay,
      forecast_value: bustForecastValue,
      init_hour: bustInitHour,
      valid_hour: bustValidHour,
      valid_month: bustValidMonth,
    };
    setShowBustForm(false);
    handleSendMessage(prompt, features);
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'reset',
        role: 'assistant',
        content: 'Conversation history reset. How can I assist with weather reliability verification today?',
        timestamp: 'Now',
        modelUsed: 'Scientific-Engine',
      },
    ]);
  };

  // Simple formatting helper for markdown text
  const renderFormattedMarkdown = (text: string) => {
    // Split into paragraphs / lines
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-sm font-bold text-slate-900 mt-3 mb-1.5 flex items-center gap-2">
            {line.replace('### ', '')}
          </h3>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h2 key={idx} className="text-base font-bold text-slate-900 mt-4 mb-2">
            {line.replace('## ', '')}
          </h2>
        );
      }
      if (line.startsWith('> ')) {
        return (
          <div key={idx} className="p-3 my-2 bg-slate-100/90 border-l-3 border-indigo-500 rounded-r-lg text-xs text-slate-700 italic">
            {line.replace('> ', '')}
          </div>
        );
      }
      if (line.startsWith('- ') || line.startsWith('• ')) {
        const itemText = line.substring(2);
        return (
          <li key={idx} className="text-xs text-slate-700 ml-4 list-disc my-0.5 leading-relaxed">
            <span dangerouslySetInnerHTML={{ __html: formatBoldAndCode(itemText) }} />
          </li>
        );
      }
      if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ')) {
        return (
          <div key={idx} className="text-xs text-slate-700 ml-2 my-1 leading-relaxed">
            <span dangerouslySetInnerHTML={{ __html: formatBoldAndCode(line) }} />
          </div>
        );
      }
      if (line.startsWith('|')) {
        // Simple table rendering representation
        return (
          <div key={idx} className="font-mono text-[11px] text-slate-700 bg-slate-50 px-2 py-0.5 rounded overflow-x-auto whitespace-pre">
            {line}
          </div>
        );
      }
      if (line.trim() === '') {
        return <div key={idx} className="h-1.5" />;
      }
      return (
        <p key={idx} className="text-xs text-slate-700 leading-relaxed my-1">
          <span dangerouslySetInnerHTML={{ __html: formatBoldAndCode(line) }} />
        </p>
      );
    });
  };

  const formatBoldAndCode = (str: string) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-slate-100 rounded text-slate-800 font-mono text-[11px]">$1</code>');
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Header Card */}
      <Card className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white p-5 sm:p-6 shadow-sm border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300">
                <Sparkles className="w-4 h-4 text-indigo-300" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                Week 6 Agentic AI Integration
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Weather Reliability AI Assistant
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              LangChain-orchestrated assistant integrating Week 4 empirical reliability scoring,
              Week 5 forecast-bust ML classifier inference, and meteorological uncertainty reasoning.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {backendHealth?.gemini_api_key_configured ? (
              <Badge variant="emerald" className="gap-1.5 py-1 px-2.5 text-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Gemini Active ({backendHealth.configured_model})
              </Badge>
            ) : (
              <Badge variant="amber" className="gap-1.5 py-1 px-2.5 text-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                Scientific Engine (Deterministic)
              </Badge>
            )}

            <button
              onClick={clearChat}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/15 text-slate-200 border border-white/10 text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
              title="Reset Chat"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Reset</span>
            </button>
          </div>
        </div>
      </Card>

      {/* Suggested Example Question Chips */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium px-1">
          <span>College Review Demonstration Prompts:</span>
          <span className="text-[11px] text-slate-400">Click any chip to run immediately</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {EXAMPLE_QUESTIONS.map((q, idx) => {
            const Icon = q.icon;
            return (
              <button
                key={idx}
                disabled={loading}
                onClick={() => {
                  if (q.prompt.includes('for this forecast')) {
                    setShowBustForm(true);
                  } else {
                    handleSendMessage(q.prompt);
                  }
                }}
                className="flex items-start gap-2.5 p-2.5 rounded-lg bg-white border border-slate-200/90 hover:border-indigo-300 hover:bg-indigo-50/40 text-left transition-all text-xs group cursor-pointer shadow-2xs disabled:opacity-50"
              >
                <div className="w-6 h-6 rounded-md bg-slate-100 group-hover:bg-indigo-100 text-slate-600 group-hover:text-indigo-700 flex items-center justify-center shrink-0 mt-0.5 transition-colors">
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0">
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 group-hover:text-indigo-600">
                    {q.category}
                  </div>
                  <div className="font-medium text-slate-800 text-xs truncate">
                    {q.label}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Collapsible Forecast-Bust Input Form Drawer */}
      <Card className="border border-slate-200 overflow-hidden">
        <div
          onClick={() => setShowBustForm(!showBustForm)}
          className="p-3.5 bg-slate-50 border-b border-slate-200/80 flex items-center justify-between cursor-pointer hover:bg-slate-100/70 transition-colors"
        >
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-800">
            <Sliders className="w-4 h-4 text-indigo-600" />
            <span>Interactive Forecast-Bust Input Feature Builder (Week 5 Schema)</span>
            <Badge variant="indigo" className="text-[10px] py-0 px-1.5">Exact 7 Features</Badge>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <span>{showBustForm ? 'Hide Form' : 'Configure Features'}</span>
            {showBustForm ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </div>

        {showBustForm && (
          <form onSubmit={handleBustFormSubmit} className="p-4 space-y-4 bg-white">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Target District
                </label>
                <select
                  value={bustDistrict}
                  onChange={(e) => setBustDistrict(e.target.value as DistrictName)}
                  className="w-full text-xs rounded-lg border border-slate-200 p-2 bg-white text-slate-800 focus:outline-hidden focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="Srinagar">Srinagar (Valley - High Elevation Offset)</option>
                  <option value="Jammu">Jammu (Plains - Baseline Low Error)</option>
                  <option value="Anantnag">Anantnag (South Valley)</option>
                  <option value="Baramulla">Baramulla (North Valley)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Lead Day &amp; Hours
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="1"
                    max="7"
                    value={bustLeadDay}
                    onChange={(e) => setBustLeadDay(Number(e.target.value))}
                    className="flex-1 accent-indigo-600"
                  />
                  <span className="text-xs font-mono font-semibold text-slate-800 w-16">
                    Day {bustLeadDay} ({bustLeadDay * 24}h)
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Forecast Temperature (°C)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={bustForecastValue}
                  onChange={(e) => setBustForecastValue(Number(e.target.value))}
                  className="w-full text-xs rounded-lg border border-slate-200 p-2 text-slate-800 font-mono focus:outline-hidden focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Init Cycle (UTC)
                </label>
                <select
                  value={bustInitHour}
                  onChange={(e) => setBustInitHour(Number(e.target.value))}
                  className="w-full text-xs rounded-lg border border-slate-200 p-2 bg-white text-slate-800 font-mono"
                >
                  <option value="0">00:00 UTC</option>
                  <option value="6">06:00 UTC</option>
                  <option value="12">12:00 UTC</option>
                  <option value="18">18:00 UTC</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Valid Target Hour (UTC)
                </label>
                <select
                  value={bustValidHour}
                  onChange={(e) => setBustValidHour(Number(e.target.value))}
                  className="w-full text-xs rounded-lg border border-slate-200 p-2 bg-white text-slate-800 font-mono"
                >
                  <option value="0">00:00 UTC</option>
                  <option value="6">06:00 UTC</option>
                  <option value="12">12:00 UTC (Diurnal Peak)</option>
                  <option value="18">18:00 UTC</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Forecast Month
                </label>
                <select
                  value={bustValidMonth}
                  onChange={(e) => setBustValidMonth(Number(e.target.value))}
                  className="w-full text-xs rounded-lg border border-slate-200 p-2 bg-white text-slate-800"
                >
                  <option value="1">January (Winter)</option>
                  <option value="5">May (Pre-Monsoon)</option>
                  <option value="9">September (Study Archive)</option>
                  <option value="10">October (Autumn)</option>
                </select>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-100">
              <p className="text-[11px] text-slate-500 italic">
                *Scientific Constraint: Features are strictly forecast issuance variables. Atmospheric moisture and wind speed are not features in the trained model.
              </p>
              <button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Estimate with Form Values</span>
              </button>
            </div>
          </form>
        )}
      </Card>

      {/* Main Chat Interface */}
      <Card className="flex flex-col h-[560px] border border-slate-200/90 shadow-xs overflow-hidden">
        {/* Messages Stream */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/40">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            const hasTools = msg.toolsCalled && msg.toolsCalled.length > 0;
            const isExpanded = !!expandedTools[msg.id];

            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {/* Assistant Avatar */}
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-2xs mt-0.5">
                    <Bot className="w-4 h-4 text-indigo-300" />
                  </div>
                )}

                {/* Message Body */}
                <div
                  className={`max-w-[85%] rounded-xl p-4 shadow-2xs text-xs space-y-2 ${
                    isUser
                      ? 'bg-slate-900 text-white ml-auto'
                      : msg.isError
                      ? 'bg-rose-50 border border-rose-200 text-slate-800'
                      : 'bg-white border border-slate-200/90 text-slate-800'
                  }`}
                >
                  {/* Message Meta Info Header */}
                  <div className="flex items-center justify-between gap-3 text-[10px] pb-1 border-b border-slate-100">
                    <span className={isUser ? 'text-slate-300 font-semibold' : 'text-slate-500 font-semibold'}>
                      {isUser ? 'Research Investigator' : 'Weather Reliability AI'}
                    </span>
                    <div className="flex items-center gap-2">
                      {!isUser && msg.modelUsed && (
                        <span className="font-mono text-[9px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600">
                          {msg.modelUsed}
                        </span>
                      )}
                      <span className={isUser ? 'text-slate-400' : 'text-slate-400'}>
                        {msg.timestamp}
                      </span>
                    </div>
                  </div>

                  {/* Rendered Text Content */}
                  <div className="space-y-1">
                    {isUser ? (
                      <p className="text-xs text-white leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      renderFormattedMarkdown(msg.content)
                    )}
                  </div>

                  {/* Embedded Structured Metric Summary (if present) */}
                  {!isUser && msg.structuredData?.bust_prediction?.success && (
                    <div className="p-2.5 rounded-lg bg-indigo-50/70 border border-indigo-200 mt-2 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between font-semibold text-indigo-900 text-[11px]">
                        <span>Model Output Summary</span>
                        <Badge
                          variant={
                            msg.structuredData.bust_prediction.risk_level === 'HIGH RISK'
                              ? 'rose'
                              : msg.structuredData.bust_prediction.risk_level === 'MEDIUM RISK'
                              ? 'amber'
                              : 'emerald'
                          }
                        >
                          {msg.structuredData.bust_prediction.risk_level}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-[11px]">
                        <div>
                          <span className="text-slate-500">Bust Probability: </span>
                          <span className="font-bold text-slate-800">{msg.structuredData.bust_prediction.bust_probability_percent}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Predicted Class: </span>
                          <span className="font-bold text-slate-800">{msg.structuredData.bust_prediction.predicted_class}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {!isUser && msg.structuredData?.reliability?.success && (
                    <div className="p-2.5 rounded-lg bg-slate-100/80 border border-slate-200 mt-2 space-y-1 text-xs">
                      <div className="flex items-center justify-between font-semibold text-slate-800 text-[11px]">
                        <span>Week 4 Empirical Reliability</span>
                        <Badge variant="indigo">
                          R = {msg.structuredData.reliability.reliability_score_R}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                        <div>
                          <span className="text-slate-500">Confidence (C): </span>
                          <span className="font-mono text-slate-700">{msg.structuredData.reliability.sample_confidence_C}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Observed MAE: </span>
                          <span className="font-mono text-slate-700">{msg.structuredData.reliability.training_MAE || msg.structuredData.reliability.test_MAE}°C</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Expandable Tools Invoked Section */}
                  {!isUser && hasTools && (
                    <div className="pt-1.5 border-t border-slate-100">
                      <button
                        onClick={() => toggleToolExpanded(msg.id)}
                        className="text-[10px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
                      >
                        <Sliders className="w-3 h-3" />
                        <span>
                          {msg.toolsCalled?.length} Scientific Tool{msg.toolsCalled?.length! > 1 ? 's' : ''} Invoked
                        </span>
                        {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                      </button>

                      {isExpanded && (
                        <div className="mt-2 space-y-2 text-[10px]">
                          {msg.toolsCalled?.map((tc, tIdx) => (
                            <div key={tIdx} className="p-2 rounded bg-slate-50 border border-slate-200/80 font-mono space-y-1">
                              <div className="font-semibold text-slate-800 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                {tc.tool}()
                              </div>
                              <div className="text-slate-500">
                                <strong>Args:</strong> {JSON.stringify(tc.input)}
                              </div>
                              <div className="text-slate-600 max-h-24 overflow-y-auto whitespace-pre-wrap bg-white p-1 rounded border border-slate-200">
                                {JSON.stringify(tc.output, null, 2)}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* User Avatar */}
                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-2xs mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-2xs animate-pulse">
                <Bot className="w-4 h-4 text-indigo-300" />
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-2xs flex items-center gap-2.5 text-xs text-slate-600">
                <div className="w-2 h-2 rounded-full bg-indigo-600 animate-ping" />
                <span>Consulting LangChain agent &amp; scientific models...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-white border-t border-slate-200/90 flex items-center gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask about reliability, compare districts, or forecast bust risk (e.g. 'Explain Srinagar lead day 2')..."
            className="flex-1 text-xs px-3.5 py-2.5 rounded-lg border border-slate-200 bg-white text-slate-800 placeholder-slate-400 focus:outline-hidden focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            disabled={loading}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={loading || !inputMessage.trim()}
            className="px-4 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
      </Card>

      {/* Scientific Framework & Limitations Note */}
      <div className="p-3.5 rounded-xl bg-slate-100/80 border border-slate-200 text-xs text-slate-600 space-y-1.5 leading-relaxed">
        <div className="flex items-center gap-2 font-semibold text-slate-800">
          <ShieldCheck className="w-4 h-4 text-slate-700" />
          <span>Week 6 Academic Context &amp; Verification Protocol</span>
        </div>
        <p>
          This assistant evaluates <strong>NOAA GFS (0.25°) operational forecasts</strong> verified against <strong>ECMWF ERA5 reanalysis</strong> over Jammu &amp; Kashmir.
          Reliability scores quantify historical verification accuracy and sample support. Forecast-bust predictions estimate prospective risk using the Week 5 ML pipeline.
          Direct observations from in-situ ground weather stations are not used in this prototype.
        </p>
      </div>
    </div>
  );
};

export default AIAssistantPage;
