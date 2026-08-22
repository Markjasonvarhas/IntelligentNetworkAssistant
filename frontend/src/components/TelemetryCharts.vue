<template>
  <div class="charts-grid">
    <!-- Latency & Jitter Chart -->
    <div class="cyber-card chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <span class="chart-tag">TELEMETRY WAVEFORM 01</span>
          <h3 class="chart-title">LATENCY & JITTER VARIATION (ms)</h3>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><span class="legend-dot cyan"></span> Latency (ms)</span>
          <span class="legend-item"><span class="legend-dot purple"></span> Jitter (ms)</span>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas ref="latencyChartRef"></canvas>
      </div>
    </div>

    <!-- Packet Loss & Throughput Chart -->
    <div class="cyber-card chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <span class="chart-tag">TELEMETRY WAVEFORM 02</span>
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

let latencyChart = null;
let throughputChart = null;

const commonChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 600,
    easing: 'easeOutQuart'
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(6, 9, 19, 0.9)',
      titleFont: { family: 'Orbitron', size: 11 },
      bodyFont: { family: 'Fira Code', size: 11 },
      borderColor: 'rgba(0, 240, 255, 0.3)',
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
        maxTicksLimit: 8
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

function initCharts() {
  if (!latencyChartRef.value || !throughputChartRef.value) return;

  const latCtx = latencyChartRef.value.getContext('2d');
  const tpCtx = throughputChartRef.value.getContext('2d');

  // Gradient for Latency
  const latGradient = latCtx.createLinearGradient(0, 0, 0, 250);
  latGradient.addColorStop(0, 'rgba(0, 240, 255, 0.35)');
  latGradient.addColorStop(1, 'rgba(0, 240, 255, 0.0)');

  // Latency Chart
  latencyChart = new Chart(latCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Latency (ms)',
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
          borderWidth: 2,
          pointRadius: 2,
          borderDash: [4, 4],
          tension: 0.3
        }
      ]
    },
    options: commonChartOptions
  });

  // Throughput & Loss Chart
  const tpGradient = tpCtx.createLinearGradient(0, 0, 0, 250);
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

  if (latencyChart) {
    latencyChart.data.labels = labels;
    latencyChart.data.datasets[0].data = latencies;
    latencyChart.data.datasets[1].data = jitters;
    latencyChart.update();
  }

  if (throughputChart) {
    throughputChart.data.labels = labels;
    throughputChart.data.datasets[0].data = throughputs;
    throughputChart.data.datasets[1].data = packetLosses;
    throughputChart.update();
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
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.chart-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.9rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chart-tag {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cyan);
  letter-spacing: 1px;
}

.chart-title {
  font-family: var(--font-display);
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: #fff;
}

.chart-legend {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.legend-item {
  display: flex;
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

.chart-wrapper {
  position: relative;
  height: 220px;
  width: 100%;
}

@media (max-width: 900px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
