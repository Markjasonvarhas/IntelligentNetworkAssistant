<template>
  <div class="cyber-card repair-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">AUTONOMOUS NETWORK REMEDIATION</span>
        <h3 class="panel-title">1-CLICK NETWORK SELF-HEALING & OS REPAIR TOOLKIT</h3>
      </div>
      <span class="tool-badge">OS REMEDIATION SUITE</span>
    </div>

    <p class="panel-desc">
      Instant 1-click diagnostic remediation commands for Windows & Linux to resolve socket exhaustion, stale ARP tables, DNS poisoning, and TCP stack corruption.
    </p>

    <!-- Repair Cards Grid -->
    <div class="repair-grid">
      <div 
        v-for="tool in repairTools" 
        :key="tool.id"
        class="repair-card"
      >
        <div class="card-top">
          <div class="tool-icon-box">
            <span class="tool-emoji">{{ tool.icon }}</span>
          </div>
          <div class="tool-info">
            <h4 class="tool-name">{{ tool.name }}</h4>
            <span class="tool-category">{{ tool.category }}</span>
          </div>
        </div>

        <p class="tool-desc">{{ tool.description }}</p>

        <!-- Command Boxes -->
        <div class="cmd-section">
          <!-- Windows Command -->
          <div class="cmd-row">
            <div class="cmd-meta">
              <span class="cmd-os">WINDOWS:</span>
              <button class="copy-cmd-btn" @click="copyCommand(tool.windows, `${tool.id}_win`)">
                {{ copiedId === `${tool.id}_win` ? 'COPIED! ✓' : 'COPY SCRIPT' }}
              </button>
            </div>
            <code class="cmd-text">{{ tool.windows }}</code>
          </div>

          <!-- Linux Command -->
          <div class="cmd-row">
            <div class="cmd-meta">
              <span class="cmd-os">LINUX / WSL:</span>
              <button class="copy-cmd-btn" @click="copyCommand(tool.linux, `${tool.id}_lin`)">
                {{ copiedId === `${tool.id}_lin` ? 'COPIED! ✓' : 'COPY SCRIPT' }}
              </button>
            </div>
            <code class="cmd-text">{{ tool.linux }}</code>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const copiedId = ref(null);

const repairTools = [
  {
    id: 'dns_flush',
    icon: '⚡',
    name: 'Flush DNS Resolver Cache',
    category: 'DNS Cache & Resolution',
    description: 'Clears stale or poisoned DNS cache records to resolve domain lookup timeouts and redirect errors.',
    windows: 'ipconfig /flushdns',
    linux: 'sudo systemd-resolve --flush-caches'
  },
  {
    id: 'winsock_reset',
    icon: '🔄',
    name: 'Reset TCP/IP & Winsock Sockets',
    category: 'Socket & Protocol Stack',
    description: 'Restores TCP/IP stack to default state and recovers from corrupted LSP socket layer configurations.',
    windows: 'netsh winsock reset; netsh int ip reset',
    linux: 'sudo systemctl restart NetworkManager'
  },
  {
    id: 'dhcp_renew',
    icon: '📡',
    name: 'Renew DHCP Lease & Route',
    category: 'IP Addressing & Gateway',
    description: 'Re-negotiates local IP lease with the router DHCP server to resolve IP conflicts and gateway deadlocks.',
    windows: 'ipconfig /release; ipconfig /renew',
    linux: 'sudo dhclient -r && sudo dhclient'
  },
  {
    id: 'arp_clear',
    icon: '🛡️',
    name: 'Clear Stale ARP Cache Tables',
    category: 'Layer 2 MAC Resolution',
    description: 'Flushes Address Resolution Protocol (ARP) tables to recover from duplicate MAC addresses or rogue gateway switches.',
    windows: 'arp -d *',
    linux: 'sudo ip -s -s neigh flush all'
  },
  {
    id: 'tcp_autotune',
    icon: '🚀',
    name: 'Optimize TCP Window Auto-Tuning',
    category: 'Throughput & Bandwidth',
    description: 'Enables high-performance TCP receive window auto-tuning for maximum throughput on broadband & fiber links.',
    windows: 'netsh int tcp set global autotuninglevel=normal',
    linux: 'sudo sysctl -w net.ipv4.tcp_window_scaling=1'
  }
];

function copyCommand(text, id) {
  if (!text) return;
  navigator.clipboard.writeText(text);
  copiedId.value = id;
  setTimeout(() => { copiedId.value = null; }, 2000);
}
</script>

<style scoped>
.repair-panel {
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

.tool-badge {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--cyan);
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}

.panel-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 1.25rem;
}

.repair-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.repair-card {
  background: rgba(6, 9, 19, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.75rem;
  transition: all 0.2s ease;
}

.repair-card:hover {
  border-color: rgba(0, 240, 255, 0.3);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tool-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 6px;
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-emoji { font-size: 1.2rem; }

.tool-info {
  display: flex;
  flex-direction: column;
}

.tool-name {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 800;
  color: #fff;
}

.tool-category {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--cyan);
}

.tool-desc {
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.cmd-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cmd-row {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.cmd-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cmd-os {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

.copy-cmd-btn {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: var(--cyan);
  font-family: var(--font-mono);
  font-size: 0.6rem;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.copy-cmd-btn:hover { background: rgba(0, 240, 255, 0.25); color: #fff; }

.cmd-text {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--cyan);
  background: rgba(0, 0, 0, 0.6);
  padding: 0.3rem 0.45rem;
  border-radius: 3px;
  word-break: break-all;
}
</style>
