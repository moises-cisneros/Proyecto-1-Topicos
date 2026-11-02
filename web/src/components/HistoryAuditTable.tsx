import React, { useEffect, useState } from 'react';
import { HistoryResponse, MessageAuditRecord, getHistory } from '../services/api';
import { ChevronLeft, ChevronRight, Clock, Database, Eye, RefreshCw } from 'lucide-react';

interface HistoryAuditTableProps {
  onSelectMessage?: (text: string) => void;
}

export const HistoryAuditTable: React.FC<HistoryAuditTableProps> = ({ onSelectMessage }) => {
  const [historyData, setHistoryData] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(0);
  const limit = 10;

  const loadHistory = async (pageIndex: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory(limit, pageIndex * limit);
      setHistoryData(data);
    } catch {
      setError(
        'No se pudo conectar con la base de datos PostgreSQL (puerto 5439) o el endpoint /history.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(page);
  }, [page]);

  const totalRecords = historyData?.total || 0;
  const totalPages = Math.ceil(totalRecords / limit) || 1;

  const formatDate = (isoStr: string) => {
    try {
      const date = new Date(isoStr);
      return date.toLocaleString('es-ES', {
        dateStyle: 'short',
        timeStyle: 'medium',
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-b app-border pb-2 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold app-text-primary">
              Registro de Auditoría Persistente (PostgreSQL)
            </h2>
            <span className="bg-[#232537] border border-[#8d99ae] text-xs font-mono px-2 py-0.5 rounded text-[#a8dadc] flex items-center gap-1">
              <Database className="w-3.5 h-3.5 text-[#4361ee]" />
              Puerto 5439
            </span>
          </div>
          <p className="text-xs app-text-secondary mt-1">
            Historial inmutable de clasificaciones realizadas y tiempos de inferencia.
          </p>
        </div>

        <button
          type="button"
          onClick={() => loadHistory(page)}
          className="text-xs font-mono bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-3 py-1.5 rounded hover:bg-[#393c59] flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refrescar Historial
        </button>
      </div>

      <div className="app-card border rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs font-mono app-text-muted flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Consultando registros en base de datos...
          </div>
        ) : error ? (
          <div className="p-6 text-xs font-mono text-[#ef233c] bg-[#3a1017] border-b border-[#ef233c] flex items-center justify-between">
            <span>{error}</span>
            <button
              type="button"
              onClick={() => loadHistory(page)}
              className="bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-3 py-1 rounded"
            >
              Reintentar
            </button>
          </div>
        ) : historyData && historyData.records.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-[#232537] border-b app-border text-[#edf2f4]">
                <tr>
                  <th className="p-3 w-12">ID</th>
                  <th className="p-3 w-36">Fecha / Hora</th>
                  <th className="p-3">Texto del Mensaje</th>
                  <th className="p-3 w-32">Predicción</th>
                  <th className="p-3 w-28">Prob. Spam</th>
                  <th className="p-3 w-36">Vectores</th>
                  <th className="p-3 w-24">Latencia</th>
                  <th className="p-3 w-20 text-center">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y app-border">
                {historyData.records.map((rec: MessageAuditRecord) => {
                  const isSpam = rec.prediction.toLowerCase() === 'spam';
                  return (
                    <tr key={rec.id} className="hover:bg-[#232537] app-text-secondary">
                      <td className="p-3 font-bold text-[#edf2f4]">#{rec.id}</td>
                      <td className="p-3 text-[11px] app-text-muted flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDate(rec.created_at)}
                      </td>
                      <td className="p-3 max-w-md truncate" title={rec.message_text}>
                        {rec.message_text}
                      </td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            isSpam ? 'badge-phishing' : 'badge-legit'
                          }`}
                        >
                          {isSpam ? 'SPAM / FRAUDE' : 'LEGÍTIMO'}
                        </span>
                      </td>
                      <td
                        className={`p-3 font-bold ${
                          isSpam ? 'text-[#ef233c]' : 'text-[#8d99ae]'
                        }`}
                      >
                        {(rec.probability_spam * 100).toFixed(1)}%
                      </td>
                      <td className="p-3">
                        <div className="flex flex-wrap gap-1">
                          {rec.detected_tokens && rec.detected_tokens.length > 0 ? (
                            rec.detected_tokens.map((tok, i) => (
                              <span
                                key={i}
                                className="bg-[#2b2d42] border border-[#8d99ae] text-[#edf2f4] px-1.5 py-0.5 rounded text-[10px]"
                              >
                                {tok}
                              </span>
                            ))
                          ) : (
                            <span className="text-[10px] app-text-muted">-</span>
                          )}
                        </div>
                      </td>
                      <td className="p-3 text-[11px] text-[#4361ee] font-bold">
                        {rec.latency_ms} ms
                      </td>
                      <td className="p-3 text-center">
                        {onSelectMessage && (
                          <button
                            type="button"
                            onClick={() => onSelectMessage(rec.message_text)}
                            title="Inspeccionar en analizador"
                            className="bg-[#2b2d42] text-[#edf2f4] hover:bg-[#4361ee] border border-[#8d99ae] p-1.5 rounded inline-flex items-center"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-xs font-mono app-text-muted">
            No se han registrado auditorías de inferencia aún. Clasifique mensajes en el analizador
            para comenzar el registro.
          </div>
        )}

        {/* Paginación */}
        {totalRecords > limit && (
          <div className="p-3 border-t app-border bg-[#232537] flex items-center justify-between text-xs font-mono">
            <span className="app-text-secondary">
              Mostrando {page * limit + 1} - {Math.min((page + 1) * limit, totalRecords)} de{' '}
              {totalRecords} auditorías
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1 rounded disabled:opacity-40 flex items-center gap-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                Anterior
              </button>
              <span className="app-text-primary font-bold">
                Pág. {page + 1} de {totalPages}
              </span>
              <button
                type="button"
                disabled={page + 1 >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1 rounded disabled:opacity-40 flex items-center gap-1"
              >
                Siguiente
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
