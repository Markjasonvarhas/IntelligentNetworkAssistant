<template>
  <div class="charts-grid">
    <!-- Latency & Predictive Horizon Waveform -->
    <div class="cyber-card chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <span class="chart-tag">AI PREDICTIVE TELEMETRY</span>
          <h3 class="chart-title">LATENCY & PREDICTIVE HORIZON (+30s FORECAST)</h3>
        </div>
        <div class="forecast-status-pill" :class="isBufferbloatWarning ? 'status-warn' : 'status-ok'">
          <span class="pulse-dot" :class="isBufferbloatWarning ? 'dot-warn' : 'dot-ok'"></span>
          {{ isBufferbloatWarning ? 'BUFFERBLOAT RISING (+25ms)' : 'AI FORECAST: STABLE NOMINAL' }}
        </div>
      </div>
      
      <div class="chart-wrapper">
        <canvas ref="latencyChartRef"></canvas>
      </div>

      <div class="chart-footer-legend">
        <span class="legend-item"><span class="legend-dot cyan"></span> Live Latency (ms)</span>
        <span class="legend-item"><span class="legend-dot purple"></span> Jitter (ms)</span>
        <span class="legend-item"><span class="legend-dot amber"></span> AI Predictive Horizon (+30s)</span>
      </div>
    </div>

    <!-- Packet Loss & Throughput Chart -->
    <div class="cyber-card chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <span class="chart-tag">BANDWIDTH DYNAMICS</span>
          <h3 class="chart-title">PACKET LOSS (%) & THROUGHPUT (Mbps)</h3>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><span class="legend-dot green"></span> Throughput (Mbps)</span>
          <span class="legend-item"><span class="legend-dot crimson"></span> Packet Loss (%)</span>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas ref="throughputChartRef"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const props = defineProps({
  telemetryData: {
    type: Array,
    default: () => []
  }
});

const latencyChartRef = ref(null);
const throughputChartRef = ref(null);
const isBufferbloatWarning = ref(false);

let latencyChart = null;
let throughputChart = null;

const commonChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 500,
    easing: 'easeOutQuart'
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(6, 9, 19, 0.95)',
      titleFont: { family: 'Orbitron', size: 11 },
      bodyFont: { family: 'Fira Code', size: 11 },
      borderColor: 'rgba(0, 240, 255, 0.4)',
      borderWidth: 1,
      padding: 10,
      displayColors: true
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: {
        color: '#8b949e',
        font: { family: 'Fira Code', size: 9 },
        maxTicksLimit: 10
      }
    },
    y: {
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: {
        color: '#8b949e',
        font: { family: 'Fira Code', size: 10 }
      }
    }
  }
};

function calculateForecast(latencies) {
  if (!latencies || latencies.length < 5) return [];
  
  // Linear regression on the last 8 points
  const recent = latencies.slice(-8);
  const n = recent.length;
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
  
  for (let i = 0; i < n; i++) {
    sumX += i;
    sumY += recent[i];
    sumXY += i * recent[i];
    sumX2 += i * i;
  }
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX || 1);
  const intercept = (sumY - slope * sumX) / n;
  
  isBufferbloatWarning.value = slope > 0.6;
  
  // Project 3 future horizon points
  const lastVal = recent[recent.length - 1];
  return [
    lastVal,
    Math.max(5, Math.round((lastVal + slope * 2) * 10) / 10),
    Math.max(5, Math.round((lastVal + slope * 4) * 10) / 10),
    Math.max(5, Math.round((lastVal + slope * 6) * 10) / 10)
  ];
}

function initCharts() {
  if (!latencyChartRef.value || !throughputChartRef.value) return;

  const latCtx = latencyChartRef.value.getContext('2d');
  const tpCtx = throughputChartRef.value.getContext('2d');

  // Gradient for Latency
  const latGradient = latCtx.createLinearGradient(0, 0, 0, 220);
  latGradient.addColorStop(0, 'rgba(0, 240, 255, 0.35)');
  latGradient.addColorStop(1, 'rgba(0, 240, 255, 0.0)');

  // Latency Chart with Predictive Horizon
  latencyChart = new Chart(latCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Live Latency (ms)',
          data: [],
          borderColor: '#00f0ff',
          backgroundColor: latGradient,
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          fill: true,
          tension: 0.3
        },
        {
          label: 'Jitter (ms)',
          data: [],
          borderColor: '#b5179e',
          backgroundColor: 'transparent',
          borderWidth: 1.5,
          pointRadius: 1.5,
          borderDash: [3, 3],
          tension: 0.3
        },
        {
          label: 'AI Predictive Horizon (ms)',
          data: [],
          borderColor: '#ffb703',
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 3,
          borderDash: [5, 5],
          tension: 0.3
        }
      ]
    },
    options: commonChartOptions
  });

  // Throughput & Loss Chart
  const tpGradient = tpCtx.createLinearGradient(0, 0, 0, 220);
  tpGradient.addColorStop(0, 'rgba(0, 255, 136, 0.3)');
  tpGradient.addColorStop(1, 'rgba(0, 255, 136, 0.0)');

  throughputChart = new Chart(tpCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Throughput (Mbps)',
          data: [],
          borderColor: '#00ff88',
          backgroundColor: tpGradient,
          borderWidth: 2,
          pointRadius: 2,
          fill: true,
          tension: 0.3,
          yAxisID: 'y'
        },
        {
          label: 'Packet Loss (%)',
          data: [],
          borderColor: '#ff0055',
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      ...commonChartOptions,
      scales: {
        ...commonChartOptions.scales,
        y: {
          ...commonChartOptions.scales.y,
          position: 'left',
          title: { display: true, text: 'Mbps', color: '#00ff88', font: { family: 'Fira Code', size: 9 } }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#ff0055', font: { family: 'Fira Code', size: 9 } },
          title: { display: true, text: 'Loss %', color: '#ff0055', font: { family: 'Fira Code', size: 9 } }
        }
      }
    }
  });

  updateChartsData(props.telemetryData);
}

function updateChartsData(data) {
  if (!data || !data.length) return;

  const labels = data.map(d => d.timestamp ? d.timestamp.split(' ')[1] : '');
  const latencies = data.map(d => d.latency ?? 0);
  const jitters = data.map(d => d.jitter ?? 0);
  const throughputs = data.map(d => d.throughput ?? 0);
  const packetLosses = data.map(d => d.packet_loss ?? 0);

  // Compute AI Predictive Horizon forecast
  const forecast = calculateForecast(latencies);
  const fullLabels = [...labels];
  const forecastSeries = new Array(latencies.length).fill(null);
  
  if (forecast.length > 0 && latencies.length > 0) {
    forecastSeries[latencies.length - 1] = latencies[latencies.length - 1];
    for (let i = 1; i < forecast.length; i++) {
      fullLabels.push(`+${i * 10}s`);
      forecastSeries.push(forecast[i]);
    }
  }

  if (latencyChart) {
    latencyChart.data.labels = fullLabels;
    latencyChart.data.datasets[0].data = latencies;
    latencyChart.data.datasets[1].data = jitters;
    latencyChart.data.datasets[2].data = forecastSeries;
    latencyChart.update('none');
  }

  if (throughputChart) {
    throughputChart.data.labels = labels;
    throughputChart.data.datasets[0].data = throughputs;
    throughputChart.data.datasets[1].data = packetLosses;
    throughputChart.update('none');
  }
}

watch(() => props.telemetryData, (newData) => {
  updateChartsData(newData);
}, { deep: true });

onMounted(() => {
  initCharts();
});

onUnmounted(() => {
  if (latencyChart) latencyChart.destroy();
  if (throughputChart) throughputChart.destroy();
});
</script>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.15rem;
}

.chart-card {
  padding: 1.15rem 1.35rem;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.65rem;
  margin-bottom: 0.85rem;
}

.chart-tag {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--cyan);
  letter-spacing: 1.2px;
}

.chart-title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: 0.8px;
}

.forecast-status-pill {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.status-ok {
  background: rgba(0, 255, 136, 0.12);
  border: 1px solid rgba(0, 255, 136, 0.35);
  color: var(--neon-green);
}

.status-warn {
  background: rgba(255, 183, 3, 0.15);
  border: 1px solid var(--amber);
  color: var(--amber);
}

.dot-ok { background: var(--neon-green) !important; box-shadow: 0 0 6px var(--neon-green) !important; }
.dot-warn { background: var(--amber) !important; box-shadow: 0 0 8px var(--amber) !important; }

.chart-legend, .chart-footer-legend {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.chart-footer-legend {
  margin-top: 0.65rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  justify-content: flex-end;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.legend-dot.cyan { background: var(--cyan); box-shadow: 0 0 6px var(--cyan); }
.legend-dot.purple { background: var(--neon-purple); box-shadow: 0 0 6px var(--neon-purple); }
.legend-dot.green { background: var(--neon-green); box-shadow: 0 0 6px var(--neon-green); }
.legend-dot.crimson { background: var(--crimson); box-shadow: 0 0 6px var(--crimson); }
.legend-dot.amber { background: var(--amber); box-shadow: 0 0 6px var(--amber); }

.chart-wrapper {
  height: 180px;
  width: 100%;
  position: relative;
}
</style>
