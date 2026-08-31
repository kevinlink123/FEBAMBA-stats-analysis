// src/components/CategoriaPage.jsx
import { useState, useEffect } from 'preact/hooks';

// Interface para los datos
interface Jugador {
  nombre: string;
  partidos_jugados: number;
}

interface CategoriaData {
  categoria: string;
  jugadores: Jugador[];
}

interface CategoriaPageProps {
  categoria: string;
}

export default function CategoriaPage({ categoria }: CategoriaPageProps) {
  const [categoriaData, setCategoriaData] = useState<CategoriaData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const apiUrl = import.meta.env.DEV
          ? `http://localhost:5000/api/${categoria}`
          : `https://allboys-stats.vidalatech.dpdns.org/api/${categoria}`;
          
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setCategoriaData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar los datos');
        console.error('Error fetching category data:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [categoria]);

  // Renderizado del estado de carga
  if (loading) {
    return (
      <div class="text-center py-16">
        <div class="inline-block animate-pulse">
          <div class="w-12 h-12 border-4 border-[#e8e8e8] border-t-[#1e1e1e] rounded-full animate-spin"></div>
        </div>
        <p class="text-[#999] mt-4">Cargando datos...</p>
      </div>
    );
  }

  // Renderizado de error
  if (error) {
    return (
      <div class="bg-red-50 border border-red-200 rounded-2xl p-6 sm:p-8 text-center">
        <div class="text-4xl mb-4">⚠️</div>
        <h2 class="text-xl font-medium text-red-800 mb-2">Error al cargar los datos</h2>
        <p class="text-red-600 text-sm">{error}</p>
        <a 
          href="/categorias" 
          class="inline-block mt-4 text-sm text-[#666] hover:text-[#1e1e1e] transition-colors"
        >
          ← Volver a categorías
        </a>
      </div>
    );
  }

  // Renderizado principal cuando hay datos
  if (!categoriaData) {
    return null;
  }

  const totalPartidos = categoriaData.jugadores.reduce((sum, j) => sum + j.partidos_jugados, 0);
  const promedioPartidos = categoriaData.jugadores.length > 0 
    ? Math.round(totalPartidos / categoriaData.jugadores.length)
    : 0;
  const maxPartidos = categoriaData.jugadores.length > 0 
    ? Math.max(...categoriaData.jugadores.map(j => j.partidos_jugados))
    : 0;

  return (
    <>
      <section class="mb-8 sm:mb-10 pb-6 sm:pb-8 border-b border-[#e8e8e8]">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 class="text-3xl sm:text-4xl md:text-5xl font-light tracking-tight text-[#1e1e1e] leading-tight">
              <strong class="font-semibold">{categoriaData.categoria}</strong>
            </h1>
            <p class="text-base sm:text-lg text-[#777] font-light mt-2">
              {categoriaData.jugadores.length} jugadores registrados
            </p>
            <a
              href={`/stats/add`}
              class="inline-flex items-center gap-2 px-6 py-2.5 mt-4 bg-[#1e1e1e] text-white rounded-full text-sm font-medium hover:bg-[#333] transition-colors shadow-sm hover:shadow-md"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              Cargar nuevo archivo de partido
            </a>
          </div>
          
          <a
            href={`/categoria/${categoria}/stats`}
            class="inline-flex items-center gap-2 px-6 py-2.5 bg-[#1e1e1e] text-white rounded-full text-sm font-medium hover:bg-[#333] transition-colors shadow-sm hover:shadow-md"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
            </svg>
            Estadísticas Avanzadas
          </a>
        </div>
      </section>

      <section>
        <div class="bg-white rounded-2xl border border-[#e8e8e8] overflow-hidden">
          {categoriaData.jugadores.length > 0 ? (
            <div class="divide-y divide-[#e8e8e8]">
              {categoriaData.jugadores.map((jugador, index) => (
                <div 
                  key={jugador.nombre}
                  class="flex flex-wrap items-center justify-between p-4 sm:p-6 hover:bg-[#fafafa] transition-colors"
                >
                  <div class="flex items-center gap-3 sm:gap-4">
                    <span class="text-sm font-medium text-[#999] w-6">
                      #{index + 1}
                    </span>
                    <span class="text-base sm:text-lg font-medium text-[#1e1e1e]">
                      {jugador.nombre}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-2 sm:mt-0">
                    <span class="text-sm text-[#666]">Partidos:</span>
                    <span class="text-sm sm:text-base font-semibold text-[#1e1e1e] bg-[#f0f0f0] px-3 py-1 rounded-full">
                      {jugador.partidos_jugados}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div class="text-center py-12">
              <p class="text-[#999] text-lg">No hay jugadores en esta categoría</p>
            </div>
          )}
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mt-6">
          <div class="bg-white rounded-xl border border-[#e8e8e8] p-4 text-center">
            <div class="text-2xl font-light text-[#1e1e1e]">
              {categoriaData.jugadores.length}
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
              {promedioPartidos}
            </div>
            <div class="text-xs text-[#999] uppercase tracking-wider mt-0.5">
              Promedio Partidos
            </div>
          </div>
          <div class="bg-white rounded-xl border border-[#e8e8e8] p-4 text-center">
            <div class="text-2xl font-light text-[#1e1e1e]">
              {maxPartidos}
            </div>
            <div class="text-xs text-[#999] uppercase tracking-wider mt-0.5">
              Máximo Partidos
            </div>
          </div>
        </div>
      </section>
    </>
  );
}