<template>
  <div class="cyber-card dns-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">RESOLVER LATENCY BENCHMARK & OPTIMIZATION</span>
        <h3 class="panel-title">GLOBAL DNS SPEED BENCHMARK & 1-CLICK OPTIMIZER</h3>
      </div>

      <div class="dns-actions">
        <input 
          type="text" 
          v-model="testDomain" 
          class="cyber-input-target" 
          placeholder="google.com"
          :disabled="benchmarking"
        />
        <button class="cyber-btn btn-sm" :disabled="benchmarking" @click="runBenchmark">
          <svg v-if="!benchmarking" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
          <span v-else class="spinner-icon"></span>
          {{ benchmarking ? 'BENCHMARKING...' : 'RUN BENCHMARK' }}
        </button>
      </div>
    </div>

    <!-- Fastest Winner Recommendation Banner -->
    <div v-if="benchmarkData.fastest_resolver" class="winner-banner">
      <div class="winner-trophy">⚡</div>
      <div class="winner-text">
        <span class="winner-tag">RECOMMENDED FASTEST DNS RESOLVER</span>
        <h4 class="winner-name">
          {{ benchmarkData.fastest_resolver.name }} ({{ benchmarkData.fastest_resolver.ip }}) 
          <span class="winner-ms">— {{ benchmarkData.fastest_resolver.resolve_time_ms }} ms</span>
        </h4>
        <p class="winner-desc">{{ benchmarkData.fastest_resolver.feature }}</p>
      </div>
    </div>

    <!-- Resolver Comparison Grid -->
    <div class="resolvers-grid">
      <div 
        v-for="item in benchmarkData.results" 
        :key="item.ip"
        class="resolver-card"
        :class="{ 'card-winner': item.is_fastest }"
      >
        <div class="res-top">
          <div>
            <h4 class="res-name">{{ item.name }}</h4>
            <span class="res-ip">{{ item.ip }}</span>
          </div>
          <span v-if="item.is_fastest" class="fastest-pill">FASTEST ⚡</span>
        </div>

        <div class="res-time-box">
          <span class="res-time-num">{{ item.resolve_time_ms !== null ? `${item.resolve_time_ms} ms` : 'TIMEOUT' }}</span>
          <span class="res-tier">{{ item.tier }}</span>
        </div>

        <!-- Latency Bar Track -->
        <div class="res-bar-track">
          <div 
            class="res-bar-fill"
            :style="{ width: `${Math.min(100, Math.max(10, ((item.resolve_time_ms || 50) / maxResolveTime) * 100))}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 1-Click OS Optimization Commands -->
    <div class="optimizer-box">
      <h4 class="opt-title">1-CLICK DNS CONFIGURATION COMMANDS</h4>
      <div class="opt-commands-grid">
        <div class="opt-cmd-item">
          <div class="opt-cmd-header">
            <span class="os-lbl">WINDOWS (POWERSHELL ADMIN):</span>
            <button class="copy-btn" @click="copyText(benchmarkData.optimizer_commands?.windows_powershell)">
              {{ copiedKey === 'ps' ? 'COPIED! ✓' : 'COPY COMMAND' }}
            </button>
          </div>
          <code class="opt-code">{{ benchmarkData.optimizer_commands?.windows_powershell }}</code>
        </div>

        <div class="opt-cmd-item">
          <div class="opt-cmd-header">
            <span class="os-lbl">FLUSH DNS RESOLVER CACHE:</span>
            <button class="copy-btn" @click="copyText('ipconfig /flushdns')">
              {{ copiedKey === 'flush' ? 'COPIED! ✓' : 'COPY COMMAND' }}
            </button>
          </div>
          <code class="opt-code">ipconfig /flushdns</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { fetchDnsBenchmark } from '../services/api';

const testDomain = ref('google.com');
const benchmarking = ref(false);
const copiedKey = ref(null);

const benchmarkData = ref({
  benchmark_domain: 'google.com',
  fastest_resolver: { name: 'Cloudflare DNS', ip: '1.1.1.1', resolve_time_ms: 11.2, feature: 'Ultra-Fast Privacy / 1.1.1.1' },
  results: [
    { name: 'Cloudflare DNS', ip: '1.1.1.1', resolve_time_ms: 11.2, tier: 'Fastest Global', is_fastest: true, feature: 'Ultra-Fast Privacy' },
    { name: 'Google Public DNS', ip: '8.8.8.8', resolve_time_ms: 14.8, tier: 'Enterprise Standard', is_fastest: false, feature: 'Global High-Availability' },
    { name: 'Quad9 Secure', ip: '9.9.9.9', resolve_time_ms: 18.5, tier: 'Security Focused', is_fastest: false, feature: 'Malware Threat Shield' },
    { name: 'OpenDNS (Cisco)', ip: '208.67.222.222', resolve_time_ms: 19.3, tier: 'Content Filtered', is_fastest: false, feature: 'Cisco Umbrella' },
    { name: 'AdGuard DNS', ip: '94.140.14.14', resolve_time_ms: 28.6, tier: 'Privacy / AdBlock', is_fastest: false, feature: 'Ad & Tracker Blocking' }
  ],
  optimizer_commands: {
    windows_powershell: "Set-DnsClientServerAddress -InterfaceAlias 'Wi-Fi' -ServerAddresses ('1.1.1.1', '8.8.8.8')",
    linux_bash: "echo 'nameserver 1.1.1.1' | sudo tee /etc/resolv.conf",
    flush_cache_windows: "ipconfig /flushdns"
  }
});

const maxResolveTime = computed(() => {
  const times = (benchmarkData.value.results || []).map(r => r.resolve_time_ms).filter(t => t !== null);
  return times.length ? Math.max(40, Math.max(...times) * 1.2) : 50;
});

async function runBenchmark() {
  benchmarking.value = true;
  try {
    const res = await fetchDnsBenchmark(testDomain.value);
    if (res && res.results) {
      benchmarkData.value = res;
    }
  } catch (err) {
    console.error('DNS benchmark error:', err);
  } finally {
    benchmarking.value = false;
  }
}

function copyText(text) {
  if (!text) return;
  navigator.clipboard.writeText(text);
  copiedKey.value = text.includes('flush') ? 'flush' : 'ps';
  setTimeout(() => { copiedKey.value = null; }, 2000);
}

onMounted(() => {
  runBenchmark();
});
</script>

<style scoped>
.dns-panel {
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

.dns-actions {
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
  width: 150px;
  outline: none;
}

.winner-banner {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid var(--neon-green);
  border-radius: 6px;
  padding: 0.85rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
}

.winner-trophy { font-size: 1.5rem; }
.winner-tag {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--neon-green);
  letter-spacing: 1px;
}
.winner-name {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 800;
  color: #fff;
}
.winner-ms { color: var(--neon-green); }
.winner-desc { font-size: 0.75rem; color: var(--text-secondary); }

.resolvers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.resolver-card {
  background: rgba(6, 9, 19, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.6rem;
  transition: all 0.2s ease;
}

.card-winner {
  border-color: var(--neon-green) !important;
  background: rgba(0, 255, 136, 0.06) !important;
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.2) !important;
}

.res-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.res-name {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff;
}

.res-ip {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.fastest-pill {
  background: rgba(0, 255, 136, 0.15);
  border: 1px solid var(--neon-green);
  color: var(--neon-green);
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
}

.res-time-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.res-time-num {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--cyan);
}
.card-winner .res-time-num { color: var(--neon-green); }

.res-tier {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--text-secondary);
}

.res-bar-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.res-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--neon-green));
  border-radius: 2px;
  transition: width 0.4s ease;
}

.optimizer-box {
  background: rgba(6, 9, 19, 0.6);
  border: 1px solid rgba(0, 240, 255, 0.15);
  border-radius: 6px;
  padding: 1rem 1.25rem;
}

.opt-title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 0.75rem;
}

.opt-commands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0.75rem;
}

.opt-cmd-item {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  padding: 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.opt-cmd-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.os-lbl {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.copy-btn {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--cyan);
  font-family: var(--font-mono);
  font-size: 0.62rem;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.copy-btn:hover { background: rgba(0, 240, 255, 0.25); color: #fff; }

.opt-code {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--cyan);
  background: rgba(0, 0, 0, 0.5);
  padding: 0.35rem 0.5rem;
  border-radius: 3px;
  word-break: break-all;
}

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
