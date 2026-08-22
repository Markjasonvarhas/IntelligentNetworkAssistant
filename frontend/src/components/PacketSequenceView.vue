<template>
  <div class="cyber-card packet-seq-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">DEEP ICMP INSPECTION</span>
        <h3 class="panel-title">10-PACKET SEQUENCE & DELAY VARIATION</h3>
      </div>
      <div class="seq-meta">
        <span class="meta-label">TARGET:</span>
        <span class="meta-val">{{ host || '8.8.8.8' }}</span>
      </div>
    </div>

    <p class="panel-desc">
      Granular per-packet arrival delay distribution. Highlights intermediate queue buffering spikes and packet drop events.
    </p>

    <!-- Visual 10-Packet Bars -->
    <div class="packet-bars-container">
      <div 
        v-for="(val, idx) in packetSlots" 
        :key="idx" 
        class="packet-slot"
      >
        <div class="bar-column">
          <div 
            v-if="val !== null" 
            class="pkt-bar"
            :class="getPacketClass(val)"
            :style="{ height: `${Math.max(15, Math.min(100, (val / maxLatency) * 100))}%` }"
          >
            <span class="pkt-tooltip">{{ val }} ms</span>
          </div>
          <div v-else class="pkt-lost-indicator">
            <span class="lost-x">✕</span>
            <span class="lost-lbl">DROP</span>
          </div>
        </div>
        <div class="pkt-label-row">
          <span class="pkt-seq-num">#{{ idx + 1 }}</span>
          <span class="pkt-val-text">{{ val !== null ? `${val}ms` : 'LOST' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  latencyValues: {
    type: Array,
    default: () => [22.1, 23.4, 22.8, 24.1, 23.0, 22.5, 23.9, 24.2, 23.1, 22.9]
  },
  host: {
    type: String,
    default: '8.8.8.8'
  }
});

const packetSlots = computed(() => {
  const slots = [];
  const list = props.latencyValues || [];
  for (let i = 0; i < 10; i++) {
    slots.push(i < list.length ? list[i] : (list.length > 0 && i >= list.length ? null : 23.0));
  }
  return slots;
});

const maxLatency = computed(() => {
  const vals = (props.latencyValues || []).filter(v => v !== null);
  if (!vals.length) return 50;
  return Math.max(50, Math.max(...vals) * 1.2);
});

function getPacketClass(val) {
  if (val > 150) return 'bar-critical';
  if (val > 60) return 'bar-warning';
  return 'bar-healthy';
}
</script>

<style scoped>
.packet-seq-panel {
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

.seq-meta {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.meta-label { color: var(--text-muted); margin-right: 0.35rem; }
.meta-val { color: var(--cyan); font-weight: 700; }

.panel-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 1.15rem;
}

.packet-bars-container {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0.5rem;
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.1);
  border-radius: 6px;
  padding: 1rem 0.75rem 0.75rem 0.75rem;
}

.packet-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.bar-column {
  height: 120px;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
  position: relative;
}

.pkt-bar {
  width: 70%;
  border-radius: 3px 3px 0 0;
  transition: height 0.4s ease;
  position: relative;
  cursor: pointer;
}

.bar-healthy {
  background: linear-gradient(180deg, var(--neon-green), rgba(0, 255, 136, 0.3));
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.4);
}
.bar-warning {
  background: linear-gradient(180deg, var(--amber), rgba(255, 183, 3, 0.3));
  box-shadow: 0 0 8px rgba(255, 183, 3, 0.4);
}
.bar-critical {
  background: linear-gradient(180deg, var(--crimson), rgba(255, 0, 85, 0.3));
  box-shadow: 0 0 8px rgba(255, 0, 85, 0.4);
}

.pkt-lost-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--crimson);
}
.lost-x { font-size: 1.2rem; font-weight: 800; }
.lost-lbl { font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700; }

.pkt-tooltip {
  display: none;
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(6, 9, 19, 0.95);
  border: 1px solid var(--cyan);
  color: #fff;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  white-space: nowrap;
}
.pkt-bar:hover .pkt-tooltip { display: block; }

.pkt-label-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--font-mono);
}
.pkt-seq-num { font-size: 0.65rem; color: var(--text-muted); }
.pkt-val-text { font-size: 0.68rem; color: var(--text-secondary); font-weight: 600; }

@media (max-width: 768px) {
  .packet-bars-container {
    gap: 0.25rem;
    padding: 0.5rem;
  }
}
</style>
