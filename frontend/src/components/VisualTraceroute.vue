<template>
  <div class="cyber-card traceroute-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">AUTONOMOUS TOPOLOGICAL INSPECTION</span>
        <h3 class="panel-title">VISUAL HOP-BY-HOP TRACEROUTE & BOTTLENECK LOCATOR</h3>
      </div>
      
      <div class="trace-actions">
        <input 
          type="text" 
          v-model="targetHost" 
          class="cyber-input-target" 
          placeholder="8.8.8.8 or google.com"
          :disabled="tracing"
        />
        <button class="cyber-btn btn-sm" :disabled="tracing" @click="runTrace">
          <svg v-if="!tracing" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 14 14"/>
          </svg>
          <span v-else class="spinner-icon"></span>
          {{ tracing ? 'TRACING HOPS...' : 'TRACE ROUTE' }}
        </button>
      </div>
    </div>

    <!-- Bottleneck AI Alert Banner -->
    <div v-if="traceData.bottleneck_detected" class="bottleneck-banner">
      <div class="alert-icon">⚠️</div>
      <div class="alert-text">
        <h4 class="alert-title">BOTTLENECK ISOLATED AT HOP #{{ traceData.bottleneck_hop?.hop }}</h4>
        <p class="alert-desc">{{ traceData.bottleneck_hop?.bottleneck_reason }}</p>
      </div>
    </div>

    <div v-else-if="traceData.hops?.length" class="healthy-route-banner">
      <div class="alert-icon">✓</div>
      <div class="alert-text">
        <h4 class="alert-title">OPTIMAL ROUTING PATH</h4>
        <p class="alert-desc">All intermediate hops operating within nominal propagation delay bounds with zero intermediate bottlenecks.</p>
      </div>
    </div>

    <!-- Visual Topological Nodes -->
    <div class="hops-container">
      <div 
        v-for="(hop, idx) in traceData.hops" 
        :key="hop.hop"
        class="hop-node-wrapper"
      >
        <!-- Connecting Cable Line -->
        <div v-if="idx > 0" class="hop-cable" :class="{ 'cable-bottleneck': hop.is_bottleneck }">
          <span class="cable-delta">+{{ hop.delta }}ms</span>
        </div>

        <!-- Hop Card -->
        <div class="hop-card" :class="getHopCardClass(hop)">
          <div class="hop-header">
            <span class="hop-badge">HOP #{{ hop.hop }}</span>
            <span class="hop-status-dot" :class="hop.is_bottleneck ? 'dot-red' : 'dot-green'"></span>
          </div>

          <h4 class="hop-label">{{ hop.label }}</h4>
          <span class="hop-ip">{{ hop.ip }}</span>
          <span class="hop-type">{{ hop.type }}</span>

          <div class="hop-rtt-box">
            <span class="rtt-lbl">RTT DELAY:</span>
            <span class="rtt-val" :class="hop.is_bottleneck ? 'text-crimson' : 'text-cyan'">
              {{ hop.rtt !== null ? `${hop.rtt} ms` : 'FILTERED (*)' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchTraceroute } from '../services/api';

const targetHost = ref('8.8.8.8');
const tracing = ref(false);

const traceData = ref({
  target: '8.8.8.8',
  total_hops: 4,
  bottleneck_detected: false,
  bottleneck_hop: null,
  hops: [
    { hop: 1, ip: '192.168.1.1', label: 'Local Gateway / Router', type: 'Local LAN', rtt: 1.8, is_bottleneck: false, delta: 1.8 },
    { hop: 2, ip: '100.64.0.1', label: 'ISP Aggregation Gateway', type: 'ISP Broadband Edge', rtt: 12.4, is_bottleneck: false, delta: 10.6 },
    { hop: 3, ip: '112.198.0.25', label: 'Telco Regional Core Transit', type: 'Transit Backbone', rtt: 21.6, is_bottleneck: false, delta: 9.2 },
    { hop: 4, ip: '8.8.8.8', label: 'Google Public DNS', type: 'Destination Backbone', rtt: 24.3, is_bottleneck: false, delta: 2.7 }
  ]
});

async function runTrace() {
  tracing.value = true;
  try {
    const res = await fetchTraceroute(targetHost.value);
    if (res && res.hops) {
      traceData.value = res;
    }
  } catch (err) {
    console.error('Traceroute error:', err);
  } finally {
    tracing.value = false;
  }
}

function getHopCardClass(hop) {
  if (hop.is_bottleneck) return 'hop-bottleneck';
  if (hop.rtt === null) return 'hop-filtered';
  return 'hop-normal';
}

onMounted(() => {
  runTrace();
});
</script>

<style scoped>
.traceroute-panel {
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.panel-tag {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cyan);
  letter-spacing: 1.2px;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 800;
  color: #fff;
}

.trace-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cyber-input-target {
  background: rgba(6, 9, 19, 0.8);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--cyan);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  padding: 0.4rem 0.75rem;
  border-radius: 4px;
  width: 170px;
  outline: none;
}

.btn-sm {
  padding: 0.4rem 0.85rem;
  font-size: 0.72rem;
}

.bottleneck-banner {
  background: rgba(255, 0, 85, 0.15);
  border: 1px solid var(--crimson);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 0 15px rgba(255, 0, 85, 0.2);
}

.healthy-route-banner {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid var(--neon-green);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.alert-icon { font-size: 1.2rem; }
.alert-title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 800;
  color: #fff;
}
.alert-desc {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.hops-container {
  display: flex;
  align-items: center;
  overflow-x: auto;
  padding: 1rem 0.5rem;
  gap: 0.25rem;
}

.hop-node-wrapper {
  display: flex;
  align-items: center;
}

.hop-cable {
  width: 50px;
  height: 2px;
  background: rgba(0, 240, 255, 0.3);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cable-bottleneck {
  background: var(--crimson) !important;
  box-shadow: 0 0 8px var(--crimson);
}

.cable-delta {
  position: absolute;
  top: -18px;
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--cyan);
  background: rgba(6, 9, 19, 0.9);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
}
.cable-bottleneck .cable-delta { color: var(--crimson); }

.hop-card {
  min-width: 180px;
  background: rgba(6, 9, 19, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  transition: all 0.2s ease;
}

.hop-bottleneck {
  border-color: var(--crimson) !important;
  background: rgba(255, 0, 85, 0.1) !important;
  box-shadow: 0 0 15px rgba(255, 0, 85, 0.3) !important;
}

.hop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hop-badge {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--cyan);
  font-weight: 700;
}

.dot-green { background: var(--neon-green); box-shadow: 0 0 6px var(--neon-green); }
.dot-red { background: var(--crimson); box-shadow: 0 0 8px var(--crimson); }

.hop-label {
  font-family: var(--font-display);
  font-size: 0.82rem;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hop-ip {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.hop-type {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-secondary);
}

.hop-rtt-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.4);
  padding: 0.3rem 0.5rem;
  border-radius: 3px;
  margin-top: 0.4rem;
  font-family: var(--font-mono);
  font-size: 0.68rem;
}

.rtt-lbl { color: var(--text-muted); }
.rtt-val { font-weight: 700; }
.text-cyan { color: var(--cyan); }
.text-crimson { color: var(--crimson); }

.spinner-icon {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(0, 240, 255, 0.2);
  border-top-color: var(--cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
