import React, { useState, useRef } from 'react';
import { BatchResponse, predictBatchCsv, PredictionResponse } from '../services/api';
import {
  UploadCloud,
  FileText,
  AlertTriangle,
  CheckCircle,
  Download,
  Search,
  Filter,
  RefreshCw,
  Sparkles,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';

interface BatchAnalyzerProps {
  onInspectMessage?: (text: string) => void;
}

const SAMPLE_CSV_CONTENT = `text
"Hola papá, llegué bien a casa. Te llamo luego."
"URGENTE: Banco alerta de bloqueo preventivo. Verifique su cuenta en http://banco-seguridad.es de inmediato."
"¿Vas a ir a la reunión de las 5 de la tarde?"
"AVISO: Su paquete con código ES-99321 requiere confirmar entrega. Ingrese a http://envios-track.com o llame al 900881122"
"Te paso la lista del supermercado: leche, huevos y pan."
"FELICIDADES! Su número ha sido seleccionado para reclamar un bono de $2,000. Llame urgente al 800-449911"
"Nos vemos en la entrada del teatro a las ocho."
"ALERTA FRAUDE: Se ha detectado un cargo de $850. Ingrese a http://banco-soporte.org para cancelar"
"El reporte de ventas ya fue enviado por correo electrónico."
"URGENTE: Su clave de banca online expira hoy. Actualícela en http://actualiza-clave.net"`;

export const BatchAnalyzer: React.FC<BatchAnalyzerProps> = ({ onInspectMessage }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [batchResult, setBatchResult] = useState<BatchResponse | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterType, setFilterType] = useState<'all' | 'spam' | 'ham' | 'critical'>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 10;
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0];
      if (!selected.name.endsWith('.csv')) {
        setError('El archivo seleccionado debe tener extensión .csv');
        setFile(null);
        return;
      }
      setFile(selected);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const dropped = e.dataTransfer.files[0];
      if (!dropped.name.endsWith('.csv')) {
        setError('El archivo arrastrado debe tener extensión .csv');
        return;
      }
      setFile(dropped);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleLoadSampleCSV = () => {
    const blob = new Blob([SAMPLE_CSV_CONTENT], { type: 'text/csv' });
    const sampleFile = new File([blob], 'sms_amenazas_muestra.csv', { type: 'text/csv' });
    setFile(sampleFile);
    setError(null);
  };

  const handleProcessBatch = async () => {
    if (!file) {
      setError('Por favor seleccione o arrastre un archivo .csv para procesar.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await predictBatchCsv(file);
      setBatchResult(result);
      setCurrentPage(1);
    } catch (err: unknown) {
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axErr = err as { response?: { data?: { detail?: string } } };
        setError(axErr.response?.data?.detail || 'Error al procesar el archivo CSV (HTTP 422).');
      } else {
        setError('No se pudo conectar con el microservicio API (puerto 8090).');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!batchResult) return;
    const headers = ['id', 'texto', 'clasificacion', 'probabilidad_spam', 'probabilidad_ham', 'nivel_riesgo', 'tokens_detectados', 'latencia_ms'];
    const rows = batchResult.predictions.map((p, idx) => [
      idx + 1,
      `"${(p.text || '').replace(/"/g, '""')}"`,
      p.label,
      p.spam_probability,
      p.ham_probability,
      p.risk_level,
      `"${p.detected_tokens.join(';')}"`,
      p.latency_ms,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `auditoria_sms_lote_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportJSON = () => {
    if (!batchResult) return;
    const blob = new Blob([JSON.stringify(batchResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `auditoria_sms_lote_${Date.now()}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filtrado de predicciones
  const filteredPredictions = (batchResult?.predictions || []).filter((item: PredictionResponse) => {
    const textMatch = (item.text || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.detected_tokens.some((t) => t.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!textMatch) return false;

    if (filterType === 'spam') return item.label === 'spam';
    if (filterType === 'ham') return item.label === 'ham';
    if (filterType === 'critical') return item.risk_level === 'CRÍTICO';
    return true;
  });

  const totalPages = Math.ceil(filteredPredictions.length / pageSize) || 1;
  const paginatedPredictions = filteredPredictions.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <div className="space-y-6">
      {/* Zona de Carga de Archivos */}
      <div className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b app-border pb-3">
          <div>
            <h3 className="text-base font-bold app-text-primary flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-[#4361ee]" />
              Ingesta Masiva de Datasets y Archivos CSV
            </h3>
            <p className="text-xs app-text-secondary mt-0.5">
              Procesamiento paralelo de lotes de mensajes con auditoría inmutable en PostgreSQL.
            </p>
          </div>
          <button
            type="button"
            onClick={handleLoadSampleCSV}
            className="text-xs bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-3 py-1.5 rounded-md hover:bg-[#393c59] flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#4361ee]" />
            Cargar Lote de Muestra (10 SMS)
          </button>
        </div>

        {/* Dropzone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed app-border-solid rounded-lg p-6 text-center app-card-subtle flex flex-col items-center justify-center gap-3 cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv"
            className="hidden"
          />
          <FileText className="w-10 h-10 text-[#8d99ae]" />
          <div>
            <p className="text-xs font-semibold app-text-primary">
              {file ? `Archivo seleccionado: ${file.name} (${(file.size / 1024).toFixed(1)} KB)` : 'Arrastre aquí un archivo .CSV o haga clic para explorar'}
            </p>
            <p className="text-xs app-text-secondary mt-1">
              Admite columnas: <code className="text-[#4361ee]">text</code>, <code className="text-[#4361ee]">text_es</code>, <code className="text-[#4361ee]">mensaje</code> o <code className="text-[#4361ee]">sms</code> (hasta 1.000 filas por lote)
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-[#3a1017] border border-[#ef233c] text-[#ef233c] text-xs p-3 rounded font-mono flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-end gap-3 pt-2">
          {file && (
            <button
              type="button"
              onClick={() => {
                setFile(null);
                setBatchResult(null);
                setError(null);
              }}
              className="text-xs px-3 py-2 text-[#8d99ae] hover:text-[#edf2f4]"
            >
              Cancelar
            </button>
          )}
          <button
            type="button"
            disabled={!file || loading}
            onClick={handleProcessBatch}
            className="btn-cta text-xs px-5 py-2.5 rounded-md font-medium flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Analizando Dataset por Lote...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Ejecutar Clasificación de Lote</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Resumen Ejecutivo del Lote (KPIs) */}
      {batchResult && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="app-card border rounded-lg p-4">
              <span className="text-xs font-mono text-[#8d99ae] block">Total Evaluados</span>
              <span className="text-2xl font-bold font-mono text-[#edf2f4]">
                {batchResult.summary.total}
              </span>
              <span className="text-xs text-[#8d99ae] mt-1 block">mensajes procesados</span>
            </div>

            <div className="app-card border rounded-lg p-4 border-[#ef233c]/40 bg-[#ef233c]/5">
              <span className="text-xs font-mono text-[#ef233c] block flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5" />
                Amenazas Phishing / Spam
              </span>
              <span className="text-2xl font-bold font-mono text-[#ef233c]">
                {batchResult.summary.spam_count} ({batchResult.summary.spam_percentage}%)
              </span>
              <span className="text-xs text-[#8d99ae] mt-1 block">vector malicioso</span>
            </div>

            <div className="app-card border rounded-lg p-4 border-[#2b9348]/40 bg-[#2b9348]/5">
              <span className="text-xs font-mono text-green-400 block flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" />
                Comunicaciones Legítimas
              </span>
              <span className="text-2xl font-bold font-mono text-green-400">
                {batchResult.summary.ham_count}
              </span>
              <span className="text-xs text-[#8d99ae] mt-1 block">mensajes benignos</span>
            </div>

            <div className="app-card border rounded-lg p-4">
              <span className="text-xs font-mono text-[#8d99ae] block">Latencia Promedio</span>
              <span className="text-2xl font-bold font-mono text-[#4361ee]">
                {batchResult.summary.avg_latency_ms.toFixed(2)} ms
              </span>
              <span className="text-xs text-[#8d99ae] mt-1 block">
                Total: {batchResult.total_latency_ms.toFixed(1)} ms
              </span>
            </div>
          </div>

          {/* Tabla de Resultados y Filtros */}
          <div className="app-card border rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b app-border pb-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-mono text-[#8d99ae] flex items-center gap-1">
                  <Filter className="w-3.5 h-3.5" />
                  Filtrar:
                </span>
                <button
                  type="button"
                  onClick={() => { setFilterType('all'); setCurrentPage(1); }}
                  className={`text-xs px-2.5 py-1 rounded font-mono ${
                    filterType === 'all'
                      ? 'bg-[#4361ee] text-white font-bold'
                      : 'bg-[#2b2d42] text-[#edf2f4] hover:bg-[#393c59]'
                  }`}
                >
                  Todos ({batchResult.predictions.length})
                </button>
                <button
                  type="button"
                  onClick={() => { setFilterType('spam'); setCurrentPage(1); }}
                  className={`text-xs px-2.5 py-1 rounded font-mono ${
                    filterType === 'spam'
                      ? 'bg-[#ef233c] text-white font-bold'
                      : 'bg-[#2b2d42] text-[#ef233c] hover:bg-[#393c59]'
                  }`}
                >
                  Spam ({batchResult.summary.spam_count})
                </button>
                <button
                  type="button"
                  onClick={() => { setFilterType('ham'); setCurrentPage(1); }}
                  className={`text-xs px-2.5 py-1 rounded font-mono ${
                    filterType === 'ham'
                      ? 'bg-[#2b9348] text-white font-bold'
                      : 'bg-[#2b2d42] text-green-400 hover:bg-[#393c59]'
                  }`}
                >
                  Ham ({batchResult.summary.ham_count})
                </button>
                <button
                  type="button"
                  onClick={() => { setFilterType('critical'); setCurrentPage(1); }}
                  className={`text-xs px-2.5 py-1 rounded font-mono ${
                    filterType === 'critical'
                      ? 'bg-[#ef233c] text-white font-bold'
                      : 'bg-[#2b2d42] text-[#edf2f4] hover:bg-[#393c59]'
                  }`}
                >
                  Riesgo Crítico
                </button>
              </div>

              {/* Búsqueda y Exportación */}
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-[#8d99ae]" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                    placeholder="Buscar en el lote..."
                    className="app-card-subtle border app-border-solid rounded text-xs pl-8 pr-3 py-1.5 app-text-primary focus:outline-none focus:ring-1 focus:ring-[#4361ee]"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleExportCSV}
                  title="Descargar reporte en formato CSV"
                  className="text-xs bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1.5 rounded hover:bg-[#393c59] flex items-center gap-1"
                >
                  <Download className="w-3.5 h-3.5 text-[#4361ee]" />
                  CSV
                </button>
                <button
                  type="button"
                  onClick={handleExportJSON}
                  title="Descargar reporte en formato JSON"
                  className="text-xs bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1.5 rounded hover:bg-[#393c59] flex items-center gap-1"
                >
                  <Download className="w-3.5 h-3.5 text-[#4361ee]" />
                  JSON
                </button>
              </div>
            </div>

            {/* Tabla */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b app-border text-[#8d99ae]">
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Mensaje SMS</th>
                    <th className="py-2.5 px-3 text-center">Clasificación</th>
                    <th className="py-2.5 px-3 text-center">Riesgo</th>
                    <th className="py-2.5 px-3 text-right">P(Spam)</th>
                    <th className="py-2.5 px-3">Tokens Detectados</th>
                    <th className="py-2.5 px-3 text-center">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y app-border">
                  {paginatedPredictions.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-6 text-center text-[#8d99ae]">
                        No se encontraron registros que coincidan con el filtro.
                      </td>
                    </tr>
                  ) : (
                    paginatedPredictions.map((row: PredictionResponse, idx: number) => {
                      const isSpam = row.label === 'spam';
                      return (
                        <tr key={idx} className="hover:bg-[#232537]">
                          <td className="py-2.5 px-3 text-[#8d99ae]">
                            {(currentPage - 1) * pageSize + idx + 1}
                          </td>
                          <td className="py-2.5 px-3 font-sans max-w-md truncate app-text-primary" title={row.text}>
                            {row.text || '(Texto procesado)'}
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                isSpam
                                  ? 'bg-[#ef233c]/20 text-[#ef233c] border border-[#ef233c]/40'
                                  : 'bg-green-500/20 text-green-400 border border-green-500/40'
                              }`}
                            >
                              {row.label.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                row.risk_level === 'CRÍTICO'
                                  ? 'text-[#ef233c]'
                                  : row.risk_level === 'MEDIO'
                                  ? 'text-yellow-400'
                                  : 'text-green-400'
                              }`}
                            >
                              {row.risk_level}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono">
                            {(row.spam_probability * 100).toFixed(1)}%
                          </td>
                          <td className="py-2.5 px-3">
                            <div className="flex flex-wrap gap-1">
                              {row.detected_tokens.length > 0 ? (
                                row.detected_tokens.map((tok: string, tIdx: number) => (
                                  <span
                                    key={tIdx}
                                    className="bg-[#2b2d42] border border-[#8d99ae] text-[#4361ee] text-[9px] px-1.5 py-0.2 rounded"
                                  >
                                    {tok}
                                  </span>
                                ))
                              ) : (
                                <span className="text-[#8d99ae] text-[10px]">—</span>
                              )}
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            {onInspectMessage && row.text && (
                              <button
                                type="button"
                                onClick={() => onInspectMessage(row.text || '')}
                                className="text-[11px] text-[#4361ee] hover:underline flex items-center justify-center gap-1 mx-auto"
                                title="Abrir en Visor Forense de NLP"
                              >
                                <span>Forense</span>
                                <ArrowRight className="w-3 h-3" />
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Paginación */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t app-border pt-3 text-xs font-mono">
                <span className="text-[#8d99ae]">
                  Mostrando página {currentPage} de {totalPages} ({filteredPredictions.length} registros)
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    className="bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1 rounded disabled:opacity-40"
                  >
                    Anterior
                  </button>
                  <button
                    type="button"
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    className="bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1 rounded disabled:opacity-40"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
