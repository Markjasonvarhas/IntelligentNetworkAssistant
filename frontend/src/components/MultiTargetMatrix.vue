<template>
  <div class="cyber-card probe-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">DISTRIBUTED NODE TELEMETRY</span>
        <h3 class="panel-title">MULTI-TARGET PING MATRIX</h3>
      </div>
      <button class="cyber-btn btn-sm" :disabled="probing" @click="runProbes">
        <svg v-if="!probing" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
        </svg>
        <span v-else class="spinner-icon"></span>
        {{ probing ? 'PROBING NODES...' : 'PROBE ALL TARGETS' }}
      </button>
    </div>

    <p class="panel-desc">
      Concurrent multi-hop latency telemetry across global primary DNS, CDN, and recursive resolver backbones to isolate upstream ISP routing bottlenecks.
    </p>

    <!-- Node Cards Grid -->
    <div class="probe-grid">
      <div 
        v-for="target in probeResults" 
        :key="target.host" 
        class="probe-card"
        :class="getCardClass(target)"
      >
        <div class="card-top">
          <div class="node-meta">
            <span class="node-type">{{ target.type }}</span>
            <h4 class="node-name">{{ target.name }}</h4>
            <span class="node-ip">{{ target.host }}</span>
          </div>
          <span class="pulse-dot" :class="{ 'dot-offline': target.status === 'offline' }"></span>
        </div>

        <div class="card-metrics">
          <div class="m-box">
            <span class="m-lbl">LATENCY</span>
            <span class="m-val">{{ target.latency !== null ? `${target.latency} ms` : 'TIMEOUT' }}</span>
          </div>
          <div class="m-box">
            <span class="m-lbl">PACKET LOSS</span>
            <span class="m-val" :class="{ 'text-crimson': target.loss > 0 }">{{ target.loss }}%</span>
          </div>
          <div class="m-box">
            <span class="m-lbl">JITTER</span>
            <span class="m-val">{{ target.jitter !== null ? `${target.jitter} ms` : '--' }}</span>
          </div>
        </div>

        <!-- Latency Bar Visualizer -->
        <div class="latency-bar-track">
          <div 
            class="latency-bar-fill"
            :style="{ width: `${Math.min(100, ((target.latency || 20) / 200) * 100)}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchMultiProbe } from '../services/api';

const probing = ref(false);
const probeResults = ref([
  { name: 'Google DNS', host: '8.8.8.8', type: 'Global DNS', latency: 23.4, loss: 0, jitter: 1.8, status: 'online' },
  { name: 'Cloudflare DNS', host: '1.1.1.1', type: 'Global CDN / DNS', latency: 19.8, loss: 0, jitter: 1.2, status: 'online' },
  { name: 'OpenDNS (Cisco)', host: '208.67.222.222', type: 'Security DNS', latency: 24.1, loss: 0, jitter: 2.1, status: 'online' },
  { name: 'Quad9 Secure', host: '9.9.9.9', type: 'Privacy DNS', latency: 28.6, loss: 0, jitter: 2.5, status: 'online' }
]);

async function runProbes() {
  probing.value = true;
  try {
    const data = await fetchMultiProbe();
    if (data && data.length) {
      probeResults.value = data;
    }
  } catch (err) {
    console.error('Probe error:', err);
  } finally {
    probing.value = false;
  }
}

function getCardClass(target) {
  if (target.status === 'offline' || (target.loss && target.loss > 10)) return 'probe-critical';
  if (target.latency > 100 || (target.loss && target.loss > 0)) return 'probe-warning';
  return 'probe-healthy';
}

onMounted(() => {
  runProbes();
});
</script>

<style scoped>
.probe-panel {
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.75rem;
  margin-bottom: 0.6rem;
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

.btn-sm {
  padding: 0.4rem 0.85rem;
  font-size: 0.72rem;
}

.panel-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 1.15rem;
}

.probe-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.probe-card {
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.2s ease;
}

.probe-healthy { border-color: rgba(0, 255, 136, 0.2); }
.probe-warning { border-color: rgba(255, 183, 3, 0.3); }
.probe-critical { border-color: rgba(255, 0, 85, 0.4); }

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.85rem;
}

.node-type {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--cyan);
  letter-spacing: 0.5px;
}

.node-name {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
}

.node-ip {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.dot-offline { background: var(--crimson) !important; box-shadow: 0 0 8px var(--crimson) !important; }

.card-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.m-box {
  display: flex;
  flex-direction: column;
}

.m-lbl {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--text-muted);
}

.m-val {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 700;
  color: #fff;
}

.text-crimson { color: var(--crimson) !important; }

.latency-bar-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.latency-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--neon-green), var(--cyan));
  border-radius: 2px;
  transition: width 0.4s ease;
}

.probe-critical .latency-bar-fill { background: var(--crimson); }
.probe-warning .latency-bar-fill { background: var(--amber); }

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
