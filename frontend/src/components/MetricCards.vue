<template>
  <div class="metrics-grid">
    <!-- Latency Card -->
    <div class="cyber-card metric-card" :class="getLatencyClass(metrics.average_latency)">
      <div class="card-header">
        <span class="metric-label">ROUND-TRIP LATENCY</span>
        <span class="status-indicator">
          <span class="pulse-dot"></span>
          {{ getLatencyStatus(metrics.average_latency) }}
        </span>
      </div>
      <div class="metric-value-row">
        <span class="metric-number">{{ formatNumber(metrics.average_latency) }}</span>
        <span class="metric-unit">ms</span>
      </div>
      <div class="card-footer-stats">
        <div class="sub-stat">
          <span class="sub-label">MIN:</span>
          <span class="sub-value">{{ formatNumber(metrics.minimum_latency) }} ms</span>
        </div>
        <div class="sub-stat">
          <span class="sub-label">MAX:</span>
          <span class="sub-value">{{ formatNumber(metrics.maximum_latency) }} ms</span>
        </div>
      </div>
      <div class="card-glow-bar"></div>
    </div>

    <!-- Packet Loss Card -->
    <div class="cyber-card metric-card" :class="getLossClass(metrics.packet_loss)">
      <div class="card-header">
        <span class="metric-label">PACKET LOSS</span>
        <span class="status-indicator">
          <span class="pulse-dot"></span>
          {{ getLossStatus(metrics.packet_loss) }}
        </span>
      </div>
      <div class="metric-value-row">
        <span class="metric-number">{{ formatNumber(metrics.packet_loss) }}</span>
        <span class="metric-unit">%</span>
      </div>
      <div class="card-footer-stats">
        <div class="sub-stat">
          <span class="sub-label">TARGET:</span>
          <span class="sub-value">{{ metrics.host || '8.8.8.8' }}</span>
        </div>
        <div class="sub-stat">
          <span class="sub-label">WINDOW:</span>
          <span class="sub-value">10 ICMP Pkts</span>
        </div>
      </div>
      <div class="card-glow-bar"></div>
    </div>

    <!-- Jitter Card -->
    <div class="cyber-card metric-card" :class="getJitterClass(metrics.jitter)">
      <div class="card-header">
        <span class="metric-label">DELAY JITTER</span>
        <span class="status-indicator">
          <span class="pulse-dot"></span>
          {{ getJitterStatus(metrics.jitter) }}
        </span>
      </div>
      <div class="metric-value-row">
        <span class="metric-number">{{ formatNumber(metrics.jitter) }}</span>
        <span class="metric-unit">ms</span>
      </div>
      <div class="card-footer-stats">
        <div class="sub-stat">
          <span class="sub-label">METRIC:</span>
          <span class="sub-value">RFC 3550 Standard</span>
        </div>
        <div class="sub-stat">
          <span class="sub-label">STABILITY:</span>
          <span class="sub-value">{{ (metrics.jitter < 4) ? 'OPTIMAL' : 'UNSTABLE' }}</span>
        </div>
      </div>
      <div class="card-glow-bar"></div>
    </div>

    <!-- Throughput Card -->
    <div class="cyber-card metric-card" :class="getThroughputClass(metrics.throughput)">
      <div class="card-header">
        <span class="metric-label">THROUGHPUT</span>
        <span class="status-indicator">
          <span class="pulse-dot"></span>
          {{ getThroughputStatus(metrics.throughput) }}
        </span>
      </div>
      <div class="metric-value-row">
        <span class="metric-number">{{ formatNumber(metrics.throughput) }}</span>
        <span class="metric-unit">Mbps</span>
      </div>
      <div class="card-footer-stats">
        <div class="sub-stat">
          <span class="sub-label">PAYLOAD:</span>
          <span class="sub-value">5 MB HTTPS</span>
        </div>
        <div class="sub-stat">
          <span class="sub-label">GATEWAY:</span>
          <span class="sub-value">Cloudflare CDN</span>
        </div>
      </div>
      <div class="card-glow-bar"></div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({
      minimum_latency: 0,
      maximum_latency: 0,
      average_latency: 0,
      packet_loss: 0,
      jitter: 0,
      throughput: 0,
      host: '8.8.8.8'
    })
  }
});

function formatNumber(val) {
  if (val === undefined || val === null) return '--';
  return Number(val).toFixed(2);
}

function getLatencyClass(lat) {
  if (!lat && lat !== 0) return '';
  if (lat > 150) return 'card-critical';
  if (lat > 60) return 'card-warning';
  return 'card-healthy';
}
function getLatencyStatus(lat) {
  if (!lat && lat !== 0) return 'WAITING';
  if (lat > 150) return 'HIGH LATENCY';
  if (lat > 60) return 'ELEVATED';
  return 'OPTIMAL';
}

function getLossClass(loss) {
  if (!loss && loss !== 0) return '';
  if (loss > 5) return 'card-critical';
  if (loss > 0) return 'card-warning';
  return 'card-healthy';
}
function getLossStatus(loss) {
  if (!loss && loss !== 0) return 'WAITING';
  if (loss > 5) return 'PACKET LOSS';
  if (loss > 0) return 'DEGRADED';
  return 'ZERO LOSS';
}

function getJitterClass(jit) {
  if (!jit && jit !== 0) return '';
  if (jit > 15) return 'card-critical';
  if (jit > 5) return 'card-warning';
  return 'card-healthy';
}
function getJitterStatus(jit) {
  if (!jit && jit !== 0) return 'WAITING';
  if (jit > 15) return 'HIGH JITTER';
  if (jit > 5) return 'DEVIATED';
  return 'STABLE';
}

function getThroughputClass(tp) {
  if (!tp && tp !== 0) return '';
  if (tp < 5) return 'card-warning';
  return 'card-healthy';
}
function getThroughputStatus(tp) {
  if (!tp && tp !== 0) return 'WAITING';
  if (tp < 5) return 'CONGESTED';
  if (tp < 25) return 'MODERATE';
  return 'HIGH SPEED';
}
</script>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.15rem;
  margin-bottom: 1.25rem;
}

.metric-card {
  padding: 1.15rem 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 140px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-label {
  font-family: var(--font-display);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 1.2px;
  color: var(--text-secondary);
}

.status-indicator {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.metric-value-row {
  margin: 0.6rem 0;
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.metric-number {
  font-family: var(--font-display);
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.5px;
}

.metric-unit {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.card-footer-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-family: var(--font-mono);
  font-size: 0.68rem;
}

.sub-label {
  color: var(--text-muted);
  margin-right: 0.25rem;
}

.sub-value {
  color: var(--text-secondary);
  font-weight: 600;
}

/* Color Modifiers */
.card-healthy .metric-number {
  color: var(--neon-green);
  text-shadow: 0 0 16px rgba(0, 255, 136, 0.4);
}
.card-healthy .status-indicator {
  color: var(--neon-green);
}
.card-healthy .card-glow-bar {
  background: var(--neon-green);
  box-shadow: 0 0 10px var(--neon-green);
}

.card-warning .metric-number {
  color: var(--amber);
  text-shadow: 0 0 16px rgba(255, 183, 3, 0.4);
}
.card-warning .status-indicator {
  color: var(--amber);
}
.card-warning .card-glow-bar {
  background: var(--amber);
  box-shadow: 0 0 10px var(--amber);
}

.card-critical .metric-number {
  color: var(--crimson);
  text-shadow: 0 0 16px rgba(255, 0, 85, 0.5);
}
.card-critical .status-indicator {
  color: var(--crimson);
}
.card-critical .card-glow-bar {
  background: var(--crimson);
  box-shadow: 0 0 10px var(--crimson);
}

.card-glow-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--cyan);
}
</style>
