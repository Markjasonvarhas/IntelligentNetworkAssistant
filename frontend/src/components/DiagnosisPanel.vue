<template>
  <div class="cyber-card diagnosis-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">AUTOMATED INFERENCE ENGINE</span>
        <h2 class="panel-title">AUTOMATED FAULT DIAGNOSIS</h2>
      </div>

      <!-- Trigger Scan Controls -->
      <div class="header-actions">
        <!-- Target Host Quick Selector -->
        <div class="host-selector">
          <span class="host-label">TARGET:</span>
          <input 
            type="text" 
            v-model="targetHost" 
            class="cyber-input-host" 
            placeholder="8.8.8.8, google.com, 192.168.1.1"
            :disabled="scanning"
            @change="$emit('change-host', targetHost)"
          />
          <div class="quick-presets">
            <button class="preset-pill" @click="setTarget('8.8.8.8')">8.8.8.8</button>
            <button class="preset-pill" @click="setTarget('1.1.1.1')">1.1.1.1</button>
            <button class="preset-pill" @click="setTarget('google.com')">google.com</button>
            <button class="preset-pill" @click="setTarget('192.168.1.1')">Gateway</button>
          </div>
        </div>

        <button 
          class="cyber-btn" 
          :disabled="scanning" 
          @click="handleTriggerScan"
        >
          <svg v-if="!scanning" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          <span v-else class="spinner-icon"></span>
          {{ scanning ? 'ANALYZING...' : 'RUN AI DIAGNOSIS' }}
        </button>

        <button 
          class="cyber-btn btn-export" 
          @click="exportAuditReport"
          title="Export Formal Diagnostic Audit Report (Markdown)"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          EXPORT AUDIT REPORT
        </button>
      </div>
    </div>

    <!-- Diagnostic Readout Body -->
    <div class="diagnosis-body">
      <!-- Left Column: Fault Classification & Radial Confidence Meter -->
      <div class="diag-left-col">
        <div class="fault-badge-container">
          <span class="sub-heading">CLASSIFICATION RESULT</span>
          <div class="fault-badge" :class="`badge-${diagnosis.severity || 'healthy'}`">
            <span class="pulse-dot"></span>
            <span class="fault-text">{{ (diagnosis.fault || 'WAITING').toUpperCase().replace('_', ' ') }}</span>
          </div>
          <h3 class="fault-title">{{ diagnosis.title || 'Awaiting Diagnostic Scan' }}</h3>
        </div>

        <!-- Radial Confidence Meter -->
        <div class="confidence-container">
          <div class="confidence-circle">
            <svg viewBox="0 0 100 100" class="gauge-svg">
              <circle cx="50" cy="50" r="42" class="gauge-bg"/>
              <circle 
                cx="50" cy="50" r="42" 
                class="gauge-progress"
                :class="`progress-${diagnosis.severity || 'healthy'}`"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="dashOffset"
              />
            </svg>
            <div class="gauge-text">
              <span class="gauge-value">{{ confidencePercent }}</span>
              <span class="gauge-label">CONFIDENCE</span>
            </div>
          </div>
          <p class="confidence-caption">
            Posterior ML probability for <strong>{{ diagnosis.fault || 'target' }}</strong> class.
          </p>
        </div>
      </div>

      <!-- Right Column: Problem Description, Causes, and Action Checklist -->
      <div class="diag-right-col">
        <!-- Problem Description -->
        <div class="diag-section">
          <span class="section-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            PROBLEM SUMMARY
          </span>
          <p class="description-text">
            {{ diagnosis.description || 'System initialized in standby. Click "TRIGGER DIAGNOSIS" to analyze real-time Linux ping latency, packet loss, jitter variation, and Cloudflare throughput against the trained machine learning model.' }}
          </p>
        </div>

        <!-- Split Lists: Possible Causes & Recommended Actions -->
        <div class="diag-grid-split">
          <!-- Possible Causes -->
          <div class="diag-sub-box">
            <span class="sub-box-title neon-glow-amber">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              POSSIBLE ROOT CAUSES
            </span>
            <ul class="cause-list" v-if="diagnosis.possible_causes && diagnosis.possible_causes.length">
              <li v-for="(cause, idx) in diagnosis.possible_causes" :key="idx">
                <span class="list-num">0{{ idx + 1 }}.</span>
                <span>{{ cause }}</span>
              </li>
            </ul>
            <div v-else class="empty-list-note">No active anomalies detected.</div>
          </div>

          <!-- Recommended Actions -->
          <div class="diag-sub-box">
            <span class="sub-box-title neon-glow-green">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 11 12 14 22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
              RECOMMENDED ACTIONS
            </span>
            <ul class="action-list" v-if="diagnosis.recommendations && diagnosis.recommendations.length">
              <li v-for="(action, idx) in diagnosis.recommendations" :key="idx">
                <span class="action-bullet">▶</span>
                <span>{{ action }}</span>
              </li>
            </ul>
            <div v-else class="empty-list-note">Network telemetry is nominal.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  diagnosis: {
    type: Object,
    default: () => ({
      fault: 'normal',
      title: 'Healthy Network Condition',
      severity: 'healthy',
      confidence: 0.95,
      description: 'System running nominal telemetry.',
      possible_causes: [],
      recommendations: []
    })
  },
  scanning: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['trigger-scan', 'change-host']);

const targetHost = ref('8.8.8.8');
const circumference = 2 * Math.PI * 42; // ~263.89

function setTarget(host) {
  targetHost.value = host;
  emit('change-host', host);
}

const confidencePercent = computed(() => {
  if (!props.diagnosis.confidence) return '0%';
  return `${Math.round(props.diagnosis.confidence * 100)}%`;
});

const dashOffset = computed(() => {
  const conf = props.diagnosis.confidence || 0;
  return circumference - (conf * circumference);
});

function handleTriggerScan() {
  emit('trigger-scan', targetHost.value);
}

function exportAuditReport() {
  const ts = new Date().toISOString();
  const d = props.diagnosis || {};
  const report = `# INTELLIGENT NETWORK DIAGNOSTIC AUDIT REPORT
Generated At: ${ts}
Target Probed: ${targetHost.value}

## 1. EXECUTIVE DIAGNOSTIC CLASSIFICATION
- Primary Condition: ${(d.fault || 'normal').toUpperCase()}
- Classification Title: ${d.title || 'Healthy Network Condition'}
- Severity Level: ${(d.severity || 'healthy').toUpperCase()}
- AI Confidence Level: ${Math.round((d.confidence || 0.95) * 100)}%
- Statistical Engine: Dual-Vector Calibrated Random Forest & RFC Safety Envelope

## 2. DETAILED SUMMARY
${d.description || 'System operating under nominal parameters.'}

## 3. ROOT CAUSE ANALYSIS
${(d.possible_causes || []).map((c, i) => `${i + 1}. ${c}`).join('\n')}

## 4. ACTIONABLE REMEDIATION RECOMMENDATIONS
${(d.recommendations || []).map((r, i) => `[ ] ${r}`).join('\n')}

## 5. TELEMETRY HIGHLIGHTS
${(d.metric_highlights || []).map(m => `- ${m}`).join('\n')}

---
*Report generated automatically by Intelligent Network Troubleshooting Assistant (NOC AI)*
`;

  const blob = new Blob([report], { type: 'text/markdown;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `network_diagnostic_audit_report_${Date.now()}.md`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
</script>

<style scoped>
.diagnosis-panel {
  padding: 1.5rem;
  margin-bottom: 1.25rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.panel-tag {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--cyan);
  letter-spacing: 1.5px;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: #fff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.host-selector {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(6, 9, 19, 0.7);
  padding: 0.35rem 0.65rem;
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 4px;
}

.host-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
}

.cyber-input-host {
  background: transparent;
  border: none;
  color: var(--cyan);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  width: 150px;
  outline: none;
}

.quick-presets {
  display: flex;
  gap: 0.3rem;
  margin-left: 0.4rem;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  padding-left: 0.4rem;
}

.preset-pill {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 240, 255, 0.2);
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 0.65rem;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.preset-pill:hover {
  background: rgba(0, 240, 255, 0.2);
  color: var(--cyan);
  border-color: var(--cyan);
}

.spinner-icon {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(0, 240, 255, 0.2);
  border-top-color: var(--cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.diagnosis-body {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
}

.diag-left-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem;
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.1);
  border-radius: 6px;
}

.fault-badge-container {
  margin-bottom: 1rem;
  width: 100%;
}

.sub-heading {
  display: block;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}

.fault-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}

.fault-title {
  font-size: 0.95rem;
  color: var(--text-primary);
  font-weight: 700;
}

.confidence-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.confidence-circle {
  position: relative;
  width: 130px;
  height: 130px;
}

.gauge-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.gauge-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 8;
}

.gauge-progress {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease-in-out;
}

.progress-healthy {
  stroke: var(--neon-green);
  filter: drop-shadow(0 0 6px var(--neon-green));
}
.progress-warning {
  stroke: var(--amber);
  filter: drop-shadow(0 0 6px var(--amber));
}
.progress-critical {
  stroke: var(--crimson);
  filter: drop-shadow(0 0 6px var(--crimson));
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge-value {
  font-family: var(--font-display);
  font-size: 1.45rem;
  font-weight: 800;
  color: #fff;
}

.gauge-label {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.confidence-caption {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-top: 0.6rem;
  line-height: 1.3;
}

/* Right Column */
.diag-right-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.diag-section {
  background: rgba(6, 9, 19, 0.4);
  border: 1px solid rgba(0, 240, 255, 0.1);
  padding: 0.9rem 1.15rem;
  border-radius: 6px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 1px;
  margin-bottom: 0.4rem;
}

.description-text {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.45;
}

.diag-grid-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.diag-sub-box {
  background: rgba(6, 9, 19, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.9rem 1.15rem;
  border-radius: 6px;
}

.sub-box-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 0.6rem;
}

.cause-list, .action-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cause-list li, .action-list li {
  font-size: 0.84rem;
  color: var(--text-primary);
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  line-height: 1.35;
}

.list-num {
  font-family: var(--font-mono);
  color: var(--amber);
  font-size: 0.75rem;
  font-weight: 700;
}

.action-bullet {
  color: var(--neon-green);
  font-size: 0.65rem;
  margin-top: 0.2rem;
}

.empty-list-note {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-style: italic;
}

@media (max-width: 1024px) {
  .diagnosis-body {
    grid-template-columns: 1fr;
  }
  .diag-grid-split {
    grid-template-columns: 1fr;
  }
}
</style>
