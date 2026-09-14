// src/components/PlayerStatsPage.jsx
import { useState, useEffect, useRef } from 'preact/hooks';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  LineController,
  Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Registrar componentes de Chart.js
ChartJS.register(
  LineController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
);

const PlayerStatsPage = ({ jugadorId, categoria }) => {
  const [nombreJugador, setNombreJugador] = useState("");
  const [datosEvolucion, setDatosEvolucion] = useState(null);
  const [estadisticaSeleccionada, setEstadisticaSeleccionada] = useState('pts');
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    const fetchDatos = async () => {
      setCargando(true);
      setError(null);
      try {
        const apiUrl = import.meta.env.DEV
          ? `http://localhost:5000/api/${categoria}/stats/${jugadorId}`
          : `https://allboys-stats.vidalatech.dpdns.org/api/${categoria}/stats/${jugadorId}`;
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setDatosEvolucion(data.datos_jugador);
        setNombreJugador(data.nombre)
      } catch (error) {
        console.error('Error cargando datos:', error);
        setError('No se pudieron cargar los datos de evolución');
      } finally {
        setCargando(false);
      }
    };
    
    if (jugadorId && categoria) {
      fetchDatos();
    }
  }, [jugadorId, categoria]);

  useEffect(() => {
    if (!datosEvolucion || datosEvolucion.length === 0 || !chartRef.current) return;

    // Destruir gráfico anterior si existe
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    
    const estadisticas = {
      pts: { label: 'Puntos', color: '#FF6B6B' },
      pct2: { label: '% Dobles', color: '#4ECDC4' },
      pct3: { label: '% Triples', color: '#45B7D1' },
      pct_tl: { label: '% Tiros Libres', color: '#96CEB4' },
    };

    const estadistica = estadisticas[estadisticaSeleccionada];
    const esPorcentaje = estadisticaSeleccionada.startsWith('pct');

    const fechas = datosEvolucion.map(d => new Date(d.fecha));
    const valores = datosEvolucion.map(d => d[estadisticaSeleccionada]);

    chartInstanceRef.current = new ChartJS(ctx, {
      type: 'line',
      data: {
        labels: fechas,
        datasets: [{
          label: estadistica.label,
          data: valores,
          borderColor: estadistica.color,
          backgroundColor: estadistica.color + '33',
          tension: 0.1,
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                let value = context.parsed.y;
                if (esPorcentaje) {
                  value = value.toFixed(1) + '%';
                } else if (label === 'Puntos') {
                  value = Math.round(value);
                }
                return label + ': ' + value;
              }
            }
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                day: 'dd/MM/yy'
              }
            },
            title: {
              display: true,
              text: 'Fecha del Partido'
            }
          },
          y: {
            title: {
              display: true,
              text: esPorcentaje ? 'Porcentaje (%)' : 'Valor'
            },
            min: esPorcentaje ? 0 : undefined
          }
        }
      }
    });

    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, [datosEvolucion, estadisticaSeleccionada]);

  const estadisticasDisponibles = [
    { key: 'pts', label: 'Puntos', color: '#FF6B6B' },
    { key: 'pct2', label: '% Dobles', color: '#4ECDC4' },
    { key: 'pct3', label: '% Triples', color: '#45B7D1' },
    { key: 'pct_tl', label: '% Tiros Libres', color: '#96CEB4' },
  ];

  // Renderizado condicional
  if (cargando) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600">Cargando datos...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
      </div>
    );
  }

  if (!datosEvolucion || datosEvolucion.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
        <p>No hay datos de partidos disponibles para este jugador en esta categoría</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <div class="mb-6 pb-4 border-b border-[#e8e8e8]">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-light tracking-tight text-[#1e1e1e]">
              Evolucion Estadistica del Jugador — <span class="font-semibold">{nombreJugador}</span>
            </h1>
            <p class="text-sm text-[#777] font-light mt-1">
              Estadisticas partido a partido
            </p>
          </div>
          <a 
            href={`/categoria/${categoria}/stats`}
            class="inline-flex items-center gap-2 text-sm text-[#666] hover:text-[#1e1e1e] transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a Estadisticas Avanzadas
          </a>
        </div>
      </div>
      <h3 className="text-lg font-semibold mb-4">
        Evolución de {nombreJugador}
      </h3>
      
      <div className="mb-4 flex flex-wrap gap-2">
        {estadisticasDisponibles.map(est => (
          <button
            key={est.key}
            onClick={() => setEstadisticaSeleccionada(est.key)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors
              ${estadisticaSeleccionada === est.key 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            {est.label}
          </button>
        ))}
      </div>

      <div className="h-64">
        <canvas ref={chartRef}></canvas>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left">Fecha</th>
              <th className="px-3 py-2 text-right">Pts</th>
              <th className="px-3 py-2 text-right">%2P</th>
              <th className="px-3 py-2 text-right">%3P</th>
              <th className="px-3 py-2 text-right">%TL</th>
              <th className="px-3 py-2 text-right">Min</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {datosEvolucion.map((d, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-3 py-2">{new Date(d.fecha).toLocaleDateString()}</td>
                <td className="px-3 py-2 text-right font-medium">{d.pts}</td>
                <td className="px-3 py-2 text-right">{d.pct2.toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{d.pct3.toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{d.pct_tl.toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{d.minutos.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlayerStatsPage;