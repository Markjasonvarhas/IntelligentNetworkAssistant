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
        :refreshInterval="refreshInterval"
        :countdown="countdown"
        @update:refreshInterval="onIntervalChanged"
        @toggle-matrix="matrixEnabled = !matrixEnabled"
      />

      <!-- Main Dynamic Content Views -->
      <main class="main-content">
        <!-- View 1: Live Telemetry & AI Diagnosis Dashboard -->
        <section v-if="activeTab === 'dashboard'" class="tab-view dashboard-view">
          <!-- Top Row Full-Width: Automatic Visitor Network Detection Banner -->
          <ClientNetworkBanner :networkInfo="visitorNetworkInfo" />

          <!-- Real-Time HUD Metric Cards (4 Cards Grid) -->
          <MetricCards :metrics="latestMetrics" />

          <!-- Main NOC Command Center 2-Column Desktop Grid -->
          <div class="noc-desktop-grid">
            <!-- Left Column: Primary AI Diagnosis Terminal & Waveform Charts -->
            <div class="noc-col-primary">
              <DiagnosisPanel 
                :diagnosis="latestDiagnosis" 
                :scanning="scanning"
                @trigger-scan="runManualScan"
                @change-host="onHostChanged"
              />
              <TelemetryCharts :telemetryData="telemetryStream" />
            </div>

            <!-- Right Column: Network Quality Index & 10-Packet Inspection -->
            <div class="noc-col-secondary">
              <QualityScoreCard :healthScores="latestMetrics.health_scores || defaultHealthScores" />
              <PacketSequenceView 
                :latencyValues="latestMetrics.latency_values" 
                :host="latestMetrics.host"
              />
            </div>
          </div>
        </section>

        <!-- View 2: Visual Hop-by-Hop Traceroute & Bottleneck Pinpointer -->
        <section v-else-if="activeTab === 'traceroute'" class="tab-view">
          <VisualTraceroute />
        </section>

        <!-- View 3: DNS Speed Benchmark & 1-Click Optimizer -->
        <section v-else-if="activeTab === 'dns'" class="tab-view">
          <DnsBenchmark />
        </section>

        <!-- View 4: Autonomous Network Self-Healing Toolkit -->
        <section v-else-if="activeTab === 'selfhealing'" class="tab-view">
          <NetworkSelfHealing />
        </section>

        <!-- View 5: Multi-Target Ping Matrix -->
        <section v-else-if="activeTab === 'multiprobe'" class="tab-view">
          <MultiTargetMatrix />
        </section>

        <!-- View 6: Fault Simulation Sandbox -->
        <section v-else-if="activeTab === 'simulation'" class="tab-view">
          <SimulationSandbox />
        </section>

        <!-- View 7: Diagnostic Logs & History Audit -->
        <section v-else-if="activeTab === 'history'" class="tab-view">
          <HistoryView />
        </section>
      </main>

      <!-- Footer Telemetry Strip -->
      <footer class="cyber-footer">
        <div class="footer-left">
          <span>INTELLIGENT NETWORK ASSISTANT • NOC MONITORING & PERFORMANCE TELEMETRY</span>
        </div>
        <div class="footer-right">
          <span>WSL2 KERNEL • PYTHON FLASK • SCIKIT-LEARN • VUE 3</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import MatrixRain from './components/MatrixRain.vue';
import HeaderBar from './components/HeaderBar.vue';
import ClientNetworkBanner from './components/ClientNetworkBanner.vue';
import MetricCards from './components/MetricCards.vue';
import QualityScoreCard from './components/QualityScoreCard.vue';
import DiagnosisPanel from './components/DiagnosisPanel.vue';
import PacketSequenceView from './components/PacketSequenceView.vue';
import TelemetryCharts from './components/TelemetryCharts.vue';
import VisualTraceroute from './components/VisualTraceroute.vue';
import DnsBenchmark from './components/DnsBenchmark.vue';
import NetworkSelfHealing from './components/NetworkSelfHealing.vue';
import MultiTargetMatrix from './components/MultiTargetMatrix.vue';
import SimulationSandbox from './components/SimulationSandbox.vue';
import HistoryView from './components/HistoryView.vue';

import {
  fetchSystemStatus,
  fetchClientNetworkInfo,
  fetchTelemetryStream,
  fetchRealtimeStream,
  triggerLiveDiagnosis
} from './services/api';

const activeTab = ref('dashboard');
const matrixEnabled = ref(true);
const sentinelEnabled = ref(false);
const scanning = ref(false);

const systemStatus = ref({
  online: false,
  platform: 'Linux',
  is_wsl_linux: true,
  model_loaded: true,
  model_type: 'DecisionTreeClassifier'
});

const visitorNetworkInfo = ref({
  ip: 'Detecting...',
  isp: 'Detecting ISP / Carrier...',
  city: 'Local Area',
  region: '',
  country: 'Detecting Location',
  country_code: 'LOC',
  asn: 'Resolving ASN...'
});

const defaultHealthScores = {
  overall_health_score: 96.0,
  mos_score: 4.42,
  gaming: { grade: 'S Tier (Ultra Responsive)', status: 'optimal' },
  streaming: { grade: '4K UHD (Buffer-Free)', status: 'optimal' },
  voip: { grade: 'HD Voice (Lossless)', status: 'optimal' }
};

const latestMetrics = ref({
  minimum_latency: 22.1,
  maximum_latency: 26.8,
  average_latency: 24.3,
  packet_loss: 0.0,
  jitter: 1.6,
  throughput: 68.4,
  latency_values: [22.1, 23.4, 22.8, 24.1, 23.0, 22.5, 23.9, 26.8, 23.1, 22.9],
  host: '8.8.8.8',
  health_scores: defaultHealthScores
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
let sentinelTimer = null;
let realtimeStreamTimer = null;

// Simple Web Audio API cyber synth sound
function playCyberBeep(freq = 880, type = 'sine', duration = 0.08) {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch (e) {}
}

function onHostChanged(newHost) {
  latestMetrics.value.host = newHost;
  streamLiveProbe();
}

async function streamLiveProbe() {
  if (scanning.value) return;
  try {
    const probe = await fetchRealtimeStream(latestMetrics.value.host);
    if (probe && probe.latency !== null) {
      latestMetrics.value.average_latency = probe.latency;
      latestMetrics.value.minimum_latency = probe.minimum_latency;
      latestMetrics.value.maximum_latency = probe.maximum_latency;
      latestMetrics.value.packet_loss = probe.packet_loss;
      latestMetrics.value.jitter = probe.jitter;
      if (probe.latency_values && probe.latency_values.length) {
        latestMetrics.value.latency_values = probe.latency_values;
      }
      
      const newPoint = {
        timestamp: probe.timestamp,
        latency: probe.latency,
        packet_loss: probe.packet_loss,
        jitter: probe.jitter,
        throughput: latestMetrics.value.throughput
      };
      const updated = [...telemetryStream.value, newPoint];
      if (updated.length > 40) updated.shift();
      telemetryStream.value = updated;
    }
  } catch (e) {}
}

function toggleSentinel() {
  sentinelEnabled.value = !sentinelEnabled.value;
  if (sentinelEnabled.value) {
    playCyberBeep(1200, 'square', 0.12);
    runManualScan(latestMetrics.value.host);
    sentinelTimer = setInterval(() => {
      if (sentinelEnabled.value && !scanning.value) {
        runManualScan(latestMetrics.value.host, false);
      }
    }, 10000);
  } else {
    playCyberBeep(440, 'sine', 0.1);
    if (sentinelTimer) clearInterval(sentinelTimer);
  }
}

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
    }
  } catch (err) {}
}

async function runManualScan(host = '8.8.8.8', speed = true) {
  scanning.value = true;
  try {
    const res = await triggerLiveDiagnosis(host, 10, speed);
    if (res && res.metrics) {
      latestMetrics.value = res.metrics;
    }
    if (res && res.diagnosis) {
      latestDiagnosis.value = res.diagnosis;
      if (res.diagnosis.severity === 'critical') {
        playCyberBeep(350, 'sawtooth', 0.3);
      } else {
        playCyberBeep(980, 'sine', 0.08);
      }
    }
    await loadTelemetry();
  } catch (err) {
    console.error('Scan error:', err);
  } finally {
    scanning.value = false;
  }
}

async function loadVisitorNetwork() {
  try {
    const info = await fetchClientNetworkInfo();
    if (info && info.ip) {
      visitorNetworkInfo.value = info;
    }
  } catch (e) {
    visitorNetworkInfo.value = {
      ip: '127.0.0.1',
      isp: 'Local LAN / Wi-Fi Gateway',
      city: 'Local Network',
      country: 'Localhost',
      asn: 'Private Subnet'
    };
  }
}

const refreshInterval = ref(5); // Default: 5 seconds (Recommended)
const countdown = ref(5);
let tickerTimer = null;

function onIntervalChanged(sec) {
  refreshInterval.value = sec;
  countdown.value = sec;
}

onMounted(() => {
  checkStatus();
  loadVisitorNetwork();
  loadTelemetry();
  // Rapid 1.5s sub-second real-time streaming probe
  realtimeStreamTimer = setInterval(streamLiveProbe, 1500);

  // 1-second auto-refresh countdown ticker
  tickerTimer = setInterval(() => {
    if (refreshInterval.value > 0) {
      countdown.value--;
      if (countdown.value <= 0) {
        countdown.value = refreshInterval.value;
        if (!scanning.value) {
          runManualScan(latestMetrics.value.host, false);
        }
      }
    }
  }, 1000);

  // Periodic status refresh
  pollInterval = setInterval(() => {
    checkStatus();
  }, 6000);
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
  if (sentinelTimer) clearInterval(sentinelTimer);
  if (realtimeStreamTimer) clearInterval(realtimeStreamTimer);
  if (tickerTimer) clearInterval(tickerTimer);
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
  max-width: 1560px;
  margin: 0 auto;
  padding: 1.25rem 1.75rem;
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

/* 2-Column Command Center Desktop Grid */
.noc-desktop-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 1.25rem;
  align-items: start;
}

.noc-col-primary, .noc-col-secondary {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

@media (max-width: 1100px) {
  .noc-desktop-grid {
    grid-template-columns: 1fr;
  }
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
