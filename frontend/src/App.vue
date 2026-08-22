<template>
  <div class="app-root">
    <!-- Matrix Digital Rain Canvas Background -->
    <MatrixRain :enabled="matrixEnabled" />

    <div class="app-container">
      <!-- Cyber Header Bar -->
      <HeaderBar 
        :activeTab="activeTab" 
        @update:activeTab="activeTab = $event"
        :systemStatus="systemStatus"
        :matrixEnabled="matrixEnabled"
        @toggle-matrix="matrixEnabled = !matrixEnabled"
      />

      <!-- Main Dynamic Content Views -->
      <main class="main-content">
        <!-- View 1: Live Telemetry & AI Diagnosis Dashboard -->
        <section v-if="activeTab === 'dashboard'" class="tab-view">
          <MetricCards :metrics="latestMetrics" />
          <DiagnosisPanel 
            :diagnosis="latestDiagnosis" 
            :scanning="scanning"
            @trigger-scan="runManualScan"
          />
          <TelemetryCharts :telemetryData="telemetryStream" />
        </section>

        <!-- View 2: Fault Simulation Sandbox -->
        <section v-else-if="activeTab === 'simulation'" class="tab-view">
          <SimulationSandbox />
        </section>

        <!-- View 3: Diagnostic Logs & History Audit -->
        <section v-else-if="activeTab === 'history'" class="tab-view">
          <HistoryView />
        </section>

        <!-- View 4: Machine Learning Research Evaluation -->
        <section v-else-if="activeTab === 'evaluation'" class="tab-view">
          <ModelEvaluationView />
        </section>
      </main>

      <!-- Footer Telemetry Strip -->
      <footer class="cyber-footer">
        <div class="footer-left">
          <span>BSIT RESEARCH PROJECT • INTELLIGENT NETWORK TROUBLESHOOTING ASSISTANT</span>
        </div>
        <div class="footer-right">
          <span>PYTHON 3.14 • FLASK • SCIKIT-LEARN • VUE 3</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import MatrixRain from './components/MatrixRain.vue';
import HeaderBar from './components/HeaderBar.vue';
import MetricCards from './components/MetricCards.vue';
import DiagnosisPanel from './components/DiagnosisPanel.vue';
import TelemetryCharts from './components/TelemetryCharts.vue';
import SimulationSandbox from './components/SimulationSandbox.vue';
import HistoryView from './components/HistoryView.vue';
import ModelEvaluationView from './components/ModelEvaluationView.vue';

import {
  fetchSystemStatus,
  fetchTelemetryStream,
  triggerLiveDiagnosis
} from './services/api';

const activeTab = ref('dashboard');
const matrixEnabled = ref(true);
const scanning = ref(false);

const systemStatus = ref({
  online: false,
  platform: 'Unknown',
  is_wsl_linux: false,
  model_loaded: false,
  model_type: 'Loading...'
});

const latestMetrics = ref({
  minimum_latency: 22.0,
  maximum_latency: 26.0,
  average_latency: 24.0,
  packet_loss: 0.0,
  jitter: 1.5,
  throughput: 65.0,
  host: '8.8.8.8'
});

const latestDiagnosis = ref({
  fault: 'normal',
  title: 'Healthy Network Condition',
  severity: 'healthy',
  confidence: 0.96,
  description: 'Network telemetry is operating within optimal baseline thresholds with low latency and zero packet loss.',
  possible_causes: [
    'Network connection and routing path are stable.',
    'Gateway interface responding nominally.'
  ],
  recommendations: [
    'Continue periodic monitoring.'
  ]
});

const telemetryStream = ref([]);
let pollInterval = null;

async function checkStatus() {
  try {
    const status = await fetchSystemStatus();
    systemStatus.value = {
      online: status.status === 'online',
      platform: status.platform,
      is_wsl_linux: status.is_wsl_linux,
      model_loaded: status.model_loaded,
      model_type: status.model_type
    };
  } catch (err) {
    systemStatus.value.online = false;
  }
}

async function loadTelemetry() {
  try {
    const data = await fetchTelemetryStream(40);
    if (data && data.length) {
      telemetryStream.value = data;
      // Sync latest card metrics with the most recent telemetry point
      const lastPoint = data[data.length - 1];
      if (lastPoint) {
        latestMetrics.value.average_latency = lastPoint.latency;
        latestMetrics.value.packet_loss = lastPoint.packet_loss;
        latestMetrics.value.jitter = lastPoint.jitter;
        latestMetrics.value.throughput = lastPoint.throughput;
      }
    }
  } catch (err) {
    // console.warn('Telemetry load pending...');
  }
}

async function runManualScan(host = '8.8.8.8') {
  scanning.value = true;
  try {
    const res = await triggerLiveDiagnosis(host, 10, true);
    if (res && res.metrics) {
      latestMetrics.value = res.metrics;
    }
    if (res && res.diagnosis) {
      latestDiagnosis.value = res.diagnosis;
    }
    await loadTelemetry();
  } catch (err) {
    console.error('Scan error:', err);
  } finally {
    scanning.value = false;
  }
}

onMounted(() => {
  checkStatus();
  loadTelemetry();
  // Poll telemetry and status every 6 seconds
  pollInterval = setInterval(() => {
    checkStatus();
    loadTelemetry();
  }, 6000);
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  position: relative;
  background-color: var(--bg-primary);
}

.app-container {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}

.tab-view {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.cyber-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 0.5rem 0.5rem 0.5rem;
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  letter-spacing: 0.8px;
  flex-wrap: wrap;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .app-container {
    padding: 0.75rem;
  }
  .cyber-footer {
    flex-direction: column;
    text-align: center;
  }
}
</style>
