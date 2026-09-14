// src/components/CategoriaStatsPage.jsx
import { useState, useEffect } from 'preact/hooks';

// Interfaces para los datos
interface JugadorStats {
  id: number;
  nombre: string;
  efg: number;
  ast_prom: number;
  min_prom: number;
  partidos_jugados: number;
  pct2: number;
  pct3: number;
  pct_tl: number;
  per_prom: number;
  pts_prom: number;
  reb_prom: number;
  rec_prom: number;
  tap_prom: number;
  tov_percentage: number;
  usage_rate: number;
}

interface CategoriaStatsData {
  categoria: string;
  jugadores: JugadorStats[];
}

interface CategoriaStatsPageProps {
  categoria: string;
}

export default function CategoriaStatsPage({ categoria }: CategoriaStatsPageProps) {
  const [statsData, setStatsData] = useState<CategoriaStatsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const apiUrl = import.meta.env.DEV 
          ? `http://localhost:5000/api/${categoria}/stats`
          : `https://allboys-stats.vidalatech.dpdns.org/api/${categoria}/stats`;
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setStatsData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar los datos');
        console.error('Error fetching stats data:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [categoria]);

  // Renderizado del estado de carga
  if (loading) {
    return (
      <div class="text-center py-16">
        <div class="inline-block animate-pulse">
          <div class="w-12 h-12 border-4 border-[#e8e8e8] border-t-[#1e1e1e] rounded-full animate-spin"></div>
        </div>
        <p class="text-[#999] mt-4">Cargando estadísticas...</p>
      </div>
    );
  }

  // Renderizado de error
  if (error) {
    return (
      <div class="bg-red-50 border border-red-200 rounded-2xl p-6 sm:p-8 text-center">
        <div class="text-4xl mb-4">⚠️</div>
        <h2 class="text-xl font-medium text-red-800 mb-2">Error al cargar las estadísticas</h2>
        <p class="text-red-600 text-sm">{error}</p>
        <a 
          href={`/categoria/${categoria}`} 
          class="inline-block mt-4 text-sm text-[#666] hover:text-[#1e1e1e] transition-colors"
        >
          ← Volver a la categoría
        </a>
      </div>
    );
  }

  // Renderizado principal cuando hay datos
  if (!statsData) {
    return null;
  }

  const totalPartidos = statsData.jugadores.reduce((sum, j) => sum + j.partidos_jugados, 0);
  const promedioPuntos = statsData.jugadores.length > 0 
    ? (statsData.jugadores.reduce((sum, j) => sum + (j.pts_prom || 0), 0) / statsData.jugadores.length)
    : 0;
  const maxPuntosProm = statsData.jugadores.length > 0 
    ? Math.max(...statsData.jugadores.map(j => j.pts_prom || 0))
    : 0;

  return (
    <>
      <div class="mb-6 pb-4 border-b border-[#e8e8e8]">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-light tracking-tight text-[#1e1e1e]">
              Estadísticas de Jugadores — <span class="font-semibold">{statsData.categoria}</span>
            </h1>
            <p class="text-sm text-[#777] font-light mt-1">
              {statsData.jugadores.length} jugadores registrados
            </p>
          </div>
          <a 
            href={`/categoria/${categoria}`}
            class="inline-flex items-center gap-2 text-sm text-[#666] hover:text-[#1e1e1e] transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a la categoría
          </a>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-[#e8e8e8] p-4 sm:p-6 shadow-sm overflow-hidden">
        <div class="overflow-x-auto -webkit-overflow-scrolling-touch">
          <table class="w-full border-collapse text-[13px] min-w-[900px]">
            <thead class="border-b border-[#d0d0d0]">
              <tr>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Jugador</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">PJ</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Min</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Pts</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Reb</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Asis</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Rec</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Tap</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">Per</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">2PT%</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">3PT%</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">TL%</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">EFG%</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">TOV%</th>
                <th class="text-left py-3 px-0 pr-4 font-medium text-[11px] uppercase tracking-[0.04em] text-[#666] bg-[#fafafa] sticky top-0 z-10 border-b border-[#e0e0e0] whitespace-nowrap">USAGE%</th>
              </tr>
            </thead>
            <tbody>
              {statsData.jugadores.length > 0 ? (
                statsData.jugadores.map((jugador, index) => (
                  <tr key={index} class="hover:bg-[#f8f8f8] transition-colors duration-150 border-b border-[#f0f0f0] last:border-b-0">
                    <td class="py-2.5 px-0 pr-4 text-[#1a1a1a] font-medium whitespace-nowrap"><a href={`/categoria/${categoria}/stats/${jugador.id}`}>{jugador.nombre}</a></td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.partidos_jugados}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.min_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.pts_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.reb_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.ast_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.rec_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.tap_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] whitespace-nowrap">{jugador.per_prom?.toFixed(1) ?? '-'}</td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] text-[#4a4a4a] whitespace-nowrap">
                      {jugador.pct2 != null ? `${(jugador.pct2).toFixed(1)}%` : '-'}
                    </td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] text-[#4a4a4a] whitespace-nowrap">
                      {jugador.pct3 != null ? `${(jugador.pct3).toFixed(1)}%` : '-'}
                    </td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] text-[#4a4a4a] whitespace-nowrap">
                      {jugador.pct_tl != null ? `${(jugador.pct_tl).toFixed(1)}%` : '-'}
                    </td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] text-[#4a4a4a] whitespace-nowrap">
                      {jugador.efg != null ? `${(jugador.efg).toFixed(1)}%` : '-'}
                    </td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] text-[#4a4a4a] whitespace-nowrap">
                      {jugador.tov_percentage != null ? `${(jugador.tov_percentage).toFixed(1)}%` : '-'}
                    </td>
                    <td class="py-2.5 px-0 pr-4 font-semibold tabular-nums tracking-[-0.01em] text-[#4a4a4a] whitespace-nowrap">
                      {jugador.usage_rate != null ? `${(jugador.usage_rate).toFixed(1)}%` : '-'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={15} class="text-center py-8 text-[#999]">
                    No hay datos estadísticos disponibles para esta categoría
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {statsData.jugadores.length > 0 && (
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mt-6">
          <div class="bg-white rounded-xl border border-[#e8e8e8] p-4 text-center">
            <div class="text-2xl font-light text-[#1e1e1e]">
              {statsData.jugadores.length}
            </div>
            <div class="text-xs text-[#999] uppercase tracking-wider mt-0.5">
              Total Jugadores
            </div>
          </div>
          <div class="bg-white rounded-xl border border-[#e8e8e8] p-4 text-center">
            <div class="text-2xl font-light text-[#1e1e1e]">
              {totalPartidos}
            </div>
            <div class="text-xs text-[#999] uppercase tracking-wider mt-0.5">
              Total Partidos
            </div>
          </div>
          <div class="bg-white rounded-xl border border-[#e8e8e8] p-4 text-center">
            <div class="text-2xl font-light text-[#1e1e1e]">
              {promedioPuntos.toFixed(1)}
            </div>
            <div class="text-xs text-[#999] uppercase tracking-wider mt-0.5">
              Prom. Puntos
            </div>
          </div>
          <div class="bg-white rounded-xl border border-[#e8e8e8] p-4 text-center">
            <div class="text-2xl font-light text-[#1e1e1e]">
              {maxPuntosProm.toFixed(1)}
            </div>
            <div class="text-xs text-[#999] uppercase tracking-wider mt-0.5">
              Máx. Puntos Prom.
            </div>
          </div>
        </div>
      )}
    </>
  );
}