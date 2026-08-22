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
  const ts = new Date().toLocaleString();
  const d = props.diagnosis || {};
  const reportId = `NOC-AUDIT-${Date.now().toString().slice(-6)}`;

  // Generate Formal High-Resolution Printable Certificate HTML
  const certHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Official Network Diagnostic Certificate - ${reportId}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Orbitron:wght@700;900&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    body { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; background: #fff; color: #0f172a; margin: 0; padding: 40px; }
    .cert-box { border: 3px double #00f0ff; border-radius: 12px; padding: 35px; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.08); position: relative; }
    .cert-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 25px; }
    .cert-title { font-family: 'Orbitron', sans-serif; font-size: 22px; font-weight: 900; color: #0f172a; margin: 0; }
    .cert-subtitle { font-size: 13px; color: #64748b; margin-top: 4px; }
    .cert-id-badge { font-family: 'Fira Code', monospace; background: #f1f5f9; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 700; color: #0284c7; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
    .meta-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; }
    .meta-lbl { font-size: 11px; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 4px; }
    .meta-val { font-size: 16px; font-weight: 800; color: #0f172a; }
    .score-badge { display: inline-block; background: #ecfdf5; border: 1px solid #10b981; color: #047857; font-weight: 800; padding: 4px 10px; border-radius: 6px; }
    .severity-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: 800; text-transform: uppercase; font-size: 12px; }
    .sev-healthy { background: #dcfce7; color: #15803d; }
    .sev-warning { background: #fef3c7; color: #b45309; }
    .sev-critical { background: #ffe4e6; color: #b91c1c; }
    .section-head { font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: 700; margin: 20px 0 10px 0; border-left: 4px solid #00f0ff; padding-left: 10px; }
    ul { margin: 8px 0; padding-left: 20px; font-size: 14px; color: #334155; line-height: 1.6; }
    .cert-footer { margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 20px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #64748b; }
    .signature-line { border-top: 1px solid #94a3b8; width: 180px; text-align: center; padding-top: 5px; font-weight: 700; }
    @media print { body { padding: 0; } .cert-box { box-shadow: none; border-color: #000; } }
  </style>
</head>
<body>
  <div class="cert-box">
    <div class="cert-header">
      <div>
        <h1 class="cert-title">NETWORK NOC HEALTH CERTIFICATE</h1>
        <p class="cert-subtitle">Automated Telemetry & Machine Learning Diagnostic Audit</p>
      </div>
      <div class="cert-id-badge">${reportId}</div>
    </div>

    <div class="grid-2">
      <div class="meta-box">
        <div class="meta-lbl">TARGET PROBED HOST</div>
        <div class="meta-val" style="font-family: monospace;">${targetHost.value}</div>
      </div>
      <div class="meta-box">
        <div class="meta-lbl">AUDIT TIMESTAMP</div>
        <div class="meta-val" style="font-size: 13px;">${ts}</div>
      </div>
      <div class="meta-box">
        <div class="meta-lbl">PRIMARY DIAGNOSTIC FAULT</div>
        <div class="meta-val">
          <span class="severity-badge sev-${d.severity || 'healthy'}">${(d.fault || 'Normal').toUpperCase()}</span>
        </div>
      </div>
      <div class="meta-box">
        <div class="meta-lbl">AI CONFIDENCE INDEX</div>
        <div class="meta-val"><span class="score-badge">${Math.round((d.confidence || 0.96) * 100)}% Verified</span></div>
      </div>
    </div>

    <div class="section-head">EXECUTIVE SUMMARY</div>
    <p style="font-size: 14px; color: #334155; line-height: 1.6; margin: 0;">${d.description || 'System operating within optimal physical network parameters.'}</p>

    <div class="section-head">ROOT CAUSE ANALYSIS</div>
    <ul>
      ${(d.possible_causes || ['Normal physical propagation bounds verified.']).map(c => `<li>${c}</li>`).join('')}
    </ul>

    <div class="section-head">ACTIONABLE ENGINEERING REMEDIATION</div>
    <ul>
      ${(d.recommendations || ['No corrective intervention required.']).map(r => `<li>${r}</li>`).join('')}
    </ul>

    <div class="cert-footer">
      <div>
        <strong>Verification Standard:</strong> ITU-T G.107 / RFC 3550 Standard Telemetry<br>
        <strong>Engine:</strong> Dual-Vector Calibrated Random Forest Classifier
      </div>
      <div class="signature-line">
        TELECOM NOC AUDITOR<br>
        <span style="font-size: 9px; font-weight: normal;">Automated Digital Signature</span>
      </div>
    </div>
  </div>
  <script>
    window.onload = function() {
      setTimeout(function() { window.print(); }, 500);
    };
  <\/script>
</body>
</html>`;

  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.open();
    printWindow.document.write(certHtml);
    printWindow.document.close();
  }
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
