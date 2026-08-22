<template>
  <header class="cyber-card header-bar">
    <div class="header-brand">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" stroke="#00f0ff" stroke-opacity="0.4"/>
          <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" stroke="#00f0ff"/>
          <path d="M2 12h20" stroke="#00f0ff"/>
          <circle cx="12" cy="12" r="3" fill="#00ff88"/>
        </svg>
      </div>
      <div class="brand-text">
        <h1 class="brand-title">NETWORK<span class="neon-glow-cyan">NOC</span> AI</h1>
        <p class="brand-subtitle">Automated Fault Diagnosis & Performance Telemetry</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs">
      <button 
        class="nav-tab" 
        :class="{ active: activeTab === 'dashboard' }"
        @click="$emit('update:activeTab', 'dashboard')"
      >
        <span class="tab-indicator"></span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
        LIVE TELEMETRY
      </button>

      <button 
        class="nav-tab" 
        :class="{ active: activeTab === 'simulation' }"
        @click="$emit('update:activeTab', 'simulation')"
      >
        <span class="tab-indicator"></span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
        FAULT SIMULATOR
      </button>

      <button 
        class="nav-tab" 
        :class="{ active: activeTab === 'history' }"
        @click="$emit('update:activeTab', 'history')"
      >
        <span class="tab-indicator"></span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        DIAGNOSIS LOGS
      </button>

      <button 
        class="nav-tab" 
        :class="{ active: activeTab === 'evaluation' }"
        @click="$emit('update:activeTab', 'evaluation')"
      >
        <span class="tab-indicator"></span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"/>
          <line x1="12" y1="20" x2="12" y2="4"/>
          <line x1="6" y1="20" x2="6" y2="14"/>
        </svg>
        RESEARCH EVALUATION
      </button>
    </nav>

    <!-- Header Controls & Telemetry Pills -->
    <div class="header-controls">
      <div class="status-pill">
        <span class="pulse-dot" :style="{ color: systemStatus.online ? 'var(--neon-green)' : 'var(--crimson)' }"></span>
        <span class="status-text">{{ systemStatus.online ? 'WSL2 ONLINE' : 'OFFLINE' }}</span>
      </div>

      <button 
        class="matrix-toggle-btn"
        :class="{ active: matrixEnabled }"
        @click="$emit('toggle-matrix')"
        title="Toggle Matrix Digital Rain Background"
      >
        <span class="matrix-symbol">λ</span>
        MATRIX FX: {{ matrixEnabled ? 'ON' : 'OFF' }}
      </button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  activeTab: {
    type: String,
    default: 'dashboard'
  },
  systemStatus: {
    type: Object,
    default: () => ({ online: true, platform: 'Linux' })
  },
  matrixEnabled: {
    type: Boolean,
    default: true
  }
});

defineEmits(['update:activeTab', 'toggle-matrix']);
</script>

<style scoped>
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.5rem;
  margin-bottom: 1.25rem;
  z-index: 10;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.4));
}

.brand-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: 2px;
  color: #fff;
}

.brand-subtitle {
  font-size: 0.72rem;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  font-family: var(--font-mono);
}

.nav-tabs {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(6, 9, 19, 0.6);
  padding: 0.3rem;
  border-radius: 6px;
  border: 1px solid rgba(0, 240, 255, 0.15);
}

.nav-tab {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 0.5rem 0.9rem;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: all 0.2s ease;
  position: relative;
}

.nav-tab:hover {
  color: var(--cyan);
  background: rgba(0, 240, 255, 0.08);
}

.nav-tab.active {
  color: var(--cyan);
  background: rgba(0, 240, 255, 0.15);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
}

.tab-indicator {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: transparent;
}
.nav-tab.active .tab-indicator {
  background: var(--cyan);
  box-shadow: 0 0 6px var(--cyan);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.matrix-toggle-btn {
  background: rgba(0, 255, 136, 0.08);
  color: var(--neon-green);
  border: 1px solid rgba(0, 255, 136, 0.3);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.matrix-toggle-btn.active {
  background: rgba(0, 255, 136, 0.18);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.25);
}

.matrix-symbol {
  font-weight: 800;
  color: #fff;
}

@media (max-width: 1024px) {
  .header-bar {
    flex-direction: column;
    gap: 0.8rem;
    align-items: stretch;
  }
  .nav-tabs {
    overflow-x: auto;
  }
}
</style>
