<template>
  <div class="cyber-card sentinel-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">L4 SERVICE AUDIT & MTU FRAGMENTATION DISCOVERY</span>
        <h3 class="panel-title">CRITICAL PORTS & PATH MTU DISCOVERY SENTINEL</h3>
      </div>

      <div class="sentinel-actions">
        <input 
          type="text" 
          v-model="targetHost" 
          class="cyber-input-target" 
          placeholder="8.8.8.8 or google.com"
          :disabled="scanning"
        />
        <button class="cyber-btn btn-sm" :disabled="scanning" @click="runFullAudit">
          <svg v-if="!scanning" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span v-else class="spinner-icon"></span>
          {{ scanning ? 'AUDITING L4 / MTU...' : 'RUN PORT & MTU AUDIT' }}
        </button>
      </div>
    </div>

    <!-- 2-Column Sentinel Grid -->
    <div class="sentinel-grid">
      <!-- Left: Critical Port Sentinel -->
      <div class="sentinel-card">
        <div class="sub-card-header">
          <div>
            <span class="sub-tag">L4 PROTOCOL PORTS</span>
            <h4 class="sub-title">ACTIVE SERVICE PORTS & TLS HANDSHAKE</h4>
          </div>
          <span class="open-badge">{{ portData.open_count || 0 }} / {{ portData.ports?.length || 5 }} OPEN</span>
        </div>

        <div class="ports-list">
          <div 
            v-for="p in portData.ports" 
            :key="p.port"
            class="port-item"
            :class="getPortItemClass(p.status)"
          >
            <div class="port-left">
              <span class="port-num">{{ p.port }}</span>
              <div class="port-info">
                <span class="port-service">{{ p.service }}</span>
                <span class="port-desc">{{ p.desc }}</span>
              </div>
            </div>

            <div class="port-right">
              <span v-if="p.connect_ms" class="port-ms text-cyan">{{ p.connect_ms }} ms</span>
              <span v-if="p.tls_handshake_ms" class="tls-pill">TLS: {{ p.tls_handshake_ms }}ms</span>
              <span class="port-status-badge" :class="p.status === 'OPEN' ? 'badge-open' : 'badge-closed'">
                <span class="pulse-dot" :class="p.status === 'OPEN' ? 'dot-open' : 'dot-closed'"></span>
                {{ p.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Path MTU & Packet Fragmentation Discovery -->
      <div class="sentinel-card">
        <div class="sub-card-header">
          <div>
            <span class="sub-tag">L3 PACKET SIZING</span>
            <h4 class="sub-title">PATH MTU (MAX TRANSMISSION UNIT)</h4>
          </div>
          <span class="mtu-badge">OPTIMAL MTU: {{ mtuData.optimal_mtu || 1500 }} B</span>
        </div>

        <div class="mtu-list">
          <div 
            v-for="m in mtuData.mtu_breakdown" 
            :key="m.mtu"
            class="mtu-item"
            :class="{ 'mtu-optimal': m.is_optimal }"
          >
            <div class="mtu-left">
              <span class="mtu-val">{{ m.mtu }} B</span>
              <div class="mtu-info">
                <span class="mtu-type">{{ m.type }}</span>
                <span class="mtu-bytes">Payload: {{ m.payload_bytes }} bytes (DF bit set)</span>
              </div>
            </div>

            <div class="mtu-right">
              <span v-if="m.is_optimal" class="optimal-pill">RECOMMENDED ✓</span>
              <span class="mtu-status-text" :class="m.status.includes('PASS') ? 'text-green' : 'text-crimson'">
                {{ m.status }}
              </span>
            </div>
          </div>
        </div>

        <!-- MTU OS Tuning Command -->
        <div class="mtu-command-box">
          <div class="mtu-cmd-header">
            <span class="cmd-lbl">RECOMMENDED TCP MSS CLAMPING: <strong>{{ mtuData.recommended_tcp_mss || 1460 }} bytes</strong></span>
            <button class="copy-btn" @click="copyMtuCommand">
              {{ copied ? 'COPIED! ✓' : 'COPY MTU COMMAND' }}
            </button>
          </div>
          <code class="mtu-code">{{ mtuData.tuning_command?.windows }}</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchPortScan, fetchPathMtu } from '../services/api';

const targetHost = ref('8.8.8.8');
const scanning = ref(false);
const copied = ref(false);

const portData = ref({
  host: '8.8.8.8',
  open_count: 3,
  ports: [
    { port: 53, service: 'DNS', desc: 'Domain Name System Resolution', status: 'OPEN', connect_ms: 14.2 },
    { port: 443, service: 'HTTPS / TLS', desc: 'Secure Web Traffic & TLS Handshake', status: 'OPEN', connect_ms: 18.6, tls_handshake_ms: 22.4, ssl_version: 'TLSv1.3' },
    { port: 853, service: 'DNS-over-TLS', desc: 'Encrypted DoT Privacy Stream', status: 'OPEN', connect_ms: 24.1, tls_handshake_ms: 29.8, ssl_version: 'TLSv1.3' },
    { port: 80, service: 'HTTP', desc: 'Standard Web Traffic / Redirect', status: 'CLOSED / REJECTED', connect_ms: null },
    { port: 22, service: 'SSH', desc: 'Secure Shell Encrypted Admin', status: 'CLOSED / REJECTED', connect_ms: null }
  ]
});

const mtuData = ref({
  host: '8.8.8.8',
  optimal_mtu: 1500,
  recommended_tcp_mss: 1460,
  mtu_breakdown: [
    { mtu: 1500, type: 'Standard Ethernet / Fiber Optic', payload_bytes: 1472, status: 'PASS (UNFRAGMENTED)', is_optimal: true },
    { mtu: 1492, type: 'PPPoE / DSL Broadband', payload_bytes: 1464, status: 'PASS (UNFRAGMENTED)', is_optimal: false },
    { mtu: 1420, type: 'WireGuard / Cloudflare WARP VPN', payload_bytes: 1392, status: 'PASS (UNFRAGMENTED)', is_optimal: false },
    { mtu: 1280, type: 'IPv6 Minimum Baseline', payload_bytes: 1252, status: 'PASS (UNFRAGMENTED)', is_optimal: false }
  ],
  tuning_command: {
    windows: "netsh interface ipv4 set subinterface 'Wi-Fi' mtu=1500 store=persistent",
    linux: "sudo ip link set dev eth0 mtu 1500"
  }
});

async function runFullAudit() {
  scanning.value = true;
  try {
    const [pRes, mRes] = await Promise.allSettled([
      fetchPortScan(targetHost.value),
      fetchPathMtu(targetHost.value)
    ]);
    if (pRes.status === 'fulfilled' && pRes.value?.ports) portData.value = pRes.value;
    if (mRes.status === 'fulfilled' && mRes.value?.optimal_mtu) mtuData.value = mRes.value;
  } catch (err) {
    console.error('Audit error:', err);
  } finally {
    scanning.value = false;
  }
}

function getPortItemClass(status) {
  if (status === 'OPEN') return 'item-open';
  if (status.includes('TIMEOUT')) return 'item-warn';
  return 'item-closed';
}

function copyMtuCommand() {
  navigator.clipboard.writeText(mtuData.value.tuning_command?.windows || '');
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 2000);
}

onMounted(() => {
  runFullAudit();
});
</script>

<style scoped>
.sentinel-panel {
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

.sentinel-actions {
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

.sentinel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.25rem;
}

.sentinel-card {
  background: rgba(6, 9, 19, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sub-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 0.5rem;
}

.sub-tag {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--cyan);
}

.sub-title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 800;
  color: #fff;
}

.open-badge, .mtu-badge {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--cyan);
}

.ports-list, .mtu-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.port-item, .mtu-item {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  padding: 0.55rem 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.item-open {
  border-color: rgba(0, 255, 136, 0.25);
  background: rgba(0, 255, 136, 0.04);
}

.mtu-optimal {
  border-color: rgba(0, 255, 136, 0.35);
  background: rgba(0, 255, 136, 0.06);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.15);
}

.port-left, .mtu-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.port-num, .mtu-val {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--cyan);
  min-width: 45px;
}

.port-info, .mtu-info {
  display: flex;
  flex-direction: column;
}

.port-service, .mtu-type {
  font-family: var(--font-display);
  font-size: 0.78rem;
  font-weight: 700;
  color: #fff;
}

.port-desc, .mtu-bytes {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.port-right, .mtu-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.port-ms {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
}

.tls-pill {
  background: rgba(181, 23, 158, 0.15);
  border: 1px solid var(--neon-purple);
  color: #e0aaff;
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
}

.optimal-pill {
  background: rgba(0, 255, 136, 0.15);
  border: 1px solid var(--neon-green);
  color: var(--neon-green);
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
}

.port-status-badge {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.badge-open {
  background: rgba(0, 255, 136, 0.12);
  border: 1px solid rgba(0, 255, 136, 0.35);
  color: var(--neon-green);
}

.badge-closed {
  background: rgba(255, 0, 85, 0.1);
  border: 1px solid rgba(255, 0, 85, 0.25);
  color: var(--crimson);
}

.dot-open { background: var(--neon-green); box-shadow: 0 0 6px var(--neon-green); }
.dot-closed { background: var(--crimson); box-shadow: 0 0 6px var(--crimson); }

.mtu-status-text {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
}
.text-green { color: var(--neon-green); }
.text-crimson { color: var(--crimson); }
.text-cyan { color: var(--cyan); }

.mtu-command-box {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 4px;
  padding: 0.65rem;
  margin-top: 0.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.mtu-cmd-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cmd-lbl {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--text-secondary);
}

.copy-btn {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--cyan);
  font-family: var(--font-mono);
  font-size: 0.6rem;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.copy-btn:hover { background: rgba(0, 240, 255, 0.25); color: #fff; }

.mtu-code {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--cyan);
  background: rgba(0, 0, 0, 0.6);
  padding: 0.3rem 0.45rem;
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
