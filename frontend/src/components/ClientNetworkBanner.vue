<template>
  <div class="cyber-card client-network-banner scanlines">
    <div class="banner-content">
      <!-- Left: ISP & Carrier Info -->
      <div class="isp-block">
        <div class="isp-icon-box" :class="{ 'vpn-shield-active': networkInfo.vpn?.is_vpn }">
          <!-- Shield Icon if VPN, else Network WiFi Icon -->
          <svg v-if="networkInfo.vpn?.is_vpn" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <polyline points="9 12 11 14 15 10"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
            <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
            <line x1="12" y1="20" x2="12.01" y2="20"/>
          </svg>
        </div>
        <div class="isp-text">
          <span class="banner-tag">CONNECTED VISITOR NETWORK</span>
          <h3 class="isp-name">{{ networkInfo.isp || 'Detecting Network...' }}</h3>
          <span class="asn-pill">{{ networkInfo.asn || 'Private Subnet' }}</span>
        </div>
      </div>

      <!-- Center: IP Address & Location -->
      <div class="geo-block">
        <div class="meta-item">
          <span class="meta-lbl">PUBLIC IP:</span>
          <span class="meta-val cyan">{{ networkInfo.ip || '127.0.0.1' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-lbl">LOCATION:</span>
          <span class="meta-val green">
            {{ formatLocation(networkInfo) }}
          </span>
        </div>
      </div>

      <!-- Center-Right: VPN & Tunnel Security Telemetry -->
      <div class="vpn-telemetry-block" :class="networkInfo.vpn?.is_vpn ? 'vpn-on' : 'vpn-off'">
        <div class="meta-item">
          <span class="meta-lbl">VPN / TUNNEL:</span>
          <span class="vpn-status-text">
            <span class="pulse-dot" :class="networkInfo.vpn?.is_vpn ? 'dot-vpn' : 'dot-direct'"></span>
            {{ networkInfo.vpn?.is_vpn ? networkInfo.vpn.vpn_name : 'DIRECT ISP (NO VPN)' }}
          </span>
        </div>
        <div class="meta-item">
          <span class="meta-lbl">ROUTING:</span>
          <span class="meta-val highlight-route">
            {{ networkInfo.vpn?.is_vpn ? networkInfo.vpn.tunnel_type : 'Native Physical Gateway' }}
          </span>
        </div>
      </div>

      <!-- Right: Client Link & Browser Telemetry -->
      <div class="client-telemetry-block">
        <div class="meta-item">
          <span class="meta-lbl">INTERFACE:</span>
          <span class="meta-val">{{ clientLinkType }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-lbl">OVERHEAD:</span>
          <span class="meta-val" :class="networkInfo.vpn?.is_vpn ? 'text-amber' : 'text-green'">
            {{ networkInfo.vpn?.overhead_estimate || '0 ms' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  networkInfo: {
    type: Object,
    default: () => ({
      ip: '127.0.0.1',
      isp: 'Local Gateway / Wi-Fi',
      city: 'Local',
      region: '',
      country: 'Local Network',
      country_code: 'LOC',
      asn: 'Private LAN',
      vpn: {
        is_vpn: false,
        vpn_name: 'None (Direct ISP)',
        tunnel_type: 'Direct Physical Routing',
        security_status: 'Direct Link',
        overhead_estimate: '0 ms (Native)',
        dns_shield: 'ISP Default DNS'
      }
    })
  }
});

const clientLinkType = ref('Wi-Fi / Ethernet Broadband');

function formatLocation(info) {
  if (!info) return 'Local Network';
  const parts = [];
  if (info.city && info.city !== 'Local City' && info.city !== 'Local') parts.push(info.city);
  if (info.country && info.country !== 'Local') parts.push(info.country);
  return parts.length ? parts.join(', ') : 'Local LAN Network';
}

function detectBrowserLink() {
  if (typeof navigator !== 'undefined' && 'connection' in navigator) {
    const conn = navigator.connection;
    const type = conn.type || conn.effectiveType || 'Broadband';
    const downlink = conn.downlink ? `${conn.downlink} Mbps` : '';
    clientLinkType.value = `${type.toUpperCase()} ${downlink ? '(' + downlink + ')' : ''}`;
  }
}

onMounted(() => {
  detectBrowserLink();
});
</script>

<style scoped>
.client-network-banner {
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.25rem;
  background: rgba(10, 15, 30, 0.9);
  border: 1px solid rgba(0, 240, 255, 0.35);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.isp-block {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.isp-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: rgba(0, 240, 255, 0.12);
  border: 1px solid rgba(0, 240, 255, 0.4);
  color: var(--cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.25);
  transition: all 0.3s ease;
}

.vpn-shield-active {
  background: rgba(0, 255, 136, 0.15) !important;
  border-color: var(--neon-green) !important;
  color: var(--neon-green) !important;
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.4) !important;
}

.isp-text {
  display: flex;
  flex-direction: column;
}

.banner-tag {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--cyan);
  letter-spacing: 1px;
}

.isp-name {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
}

.asn-pill {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.geo-block, .vpn-telemetry-block, .client-telemetry-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  background: rgba(6, 9, 19, 0.45);
  padding: 0.45rem 0.85rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.vpn-on {
  border-color: rgba(0, 255, 136, 0.25);
}

.vpn-status-text {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.dot-vpn {
  background: var(--neon-green) !important;
  box-shadow: 0 0 8px var(--neon-green) !important;
}

.dot-direct {
  background: var(--cyan) !important;
  box-shadow: 0 0 8px var(--cyan) !important;
}

.highlight-route {
  color: var(--cyan);
  font-size: 0.72rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.meta-lbl {
  color: var(--text-muted);
  font-size: 0.65rem;
}

.meta-val {
  color: var(--text-primary);
  font-weight: 600;
}
.meta-val.cyan { color: var(--cyan); }
.meta-val.green { color: var(--neon-green); }
.text-amber { color: var(--amber); }
.text-green { color: var(--neon-green); }

@media (max-width: 900px) {
  .banner-content {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
