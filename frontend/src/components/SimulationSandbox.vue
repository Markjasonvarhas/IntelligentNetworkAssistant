<template>
  <div class="simulation-view">
    <div class="cyber-card simulation-panel scanlines">
      <div class="panel-header">
        <div class="header-left">
          <span class="panel-tag">SANDBOX ENVIRONMENT</span>
          <h2 class="panel-title">INTERACTIVE FAULT SIMULATOR</h2>
        </div>
        <span class="sim-pill">REAL-TIME INFERENCE</span>
      </div>

      <p class="sim-intro">
        Adjust independent network performance metrics or load research test presets to evaluate the machine learning diagnosis model under simulated fault conditions.
      </p>

      <!-- Preset Scenarios -->
      <div class="presets-row">
        <span class="presets-label">FAULT SCENARIOS:</span>
        <div class="preset-buttons">
          <button class="preset-btn" @click="loadPreset('normal')">
            <span class="preset-dot green"></span> Normal Baseline
          </button>
          <button class="preset-btn" @click="loadPreset('high_latency')">
            <span class="preset-dot amber"></span> High Latency (+200ms)
          </button>
          <button class="preset-btn" @click="loadPreset('packet_loss')">
            <span class="preset-dot crimson"></span> Packet Loss (10%)
          </button>
          <button class="preset-btn" @click="loadPreset('high_jitter')">
            <span class="preset-dot purple"></span> High Jitter (30ms)
          </button>
          <button class="preset-btn" @click="loadPreset('congestion')">
            <span class="preset-dot amber"></span> Congestion Bottleneck
          </button>
        </div>
      </div>

      <!-- Sliders Grid -->
      <div class="sliders-grid">
        <!-- Average Latency Slider -->
        <div class="slider-box">
          <div class="slider-header">
            <span class="slider-name">AVERAGE LATENCY</span>
            <span class="slider-val cyan">{{ simParams.average_latency }} ms</span>
          </div>
          <input 
            type="range" 
            min="5" 
            max="600" 
            step="1" 
            v-model.number="simParams.average_latency" 
            class="cyber-slider slider-cyan"
            @input="runSimDiagnosis"
          />
          <div class="slider-scale">
            <span>5 ms</span>
            <span>300 ms</span>
            <span>600 ms</span>
          </div>
        </div>

        <!-- Packet Loss Slider -->
        <div class="slider-box">
          <div class="slider-header">
            <span class="slider-name">PACKET LOSS</span>
            <span class="slider-val crimson">{{ simParams.packet_loss }} %</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="50" 
            step="0.5" 
            v-model.number="simParams.packet_loss" 
            class="cyber-slider slider-crimson"
            @input="runSimDiagnosis"
          />
          <div class="slider-scale">
            <span>0%</span>
            <span>25%</span>
            <span>50%</span>
          </div>
        </div>

        <!-- Jitter Slider -->
        <div class="slider-box">
          <div class="slider-header">
            <span class="slider-name">DELAY JITTER</span>
            <span class="slider-val purple">{{ simParams.jitter }} ms</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="120" 
            step="0.5" 
            v-model.number="simParams.jitter" 
            class="cyber-slider slider-purple"
            @input="runSimDiagnosis"
          />
          <div class="slider-scale">
            <span>0 ms</span>
            <span>60 ms</span>
            <span>120 ms</span>
          </div>
        </div>

        <!-- Throughput Slider -->
        <div class="slider-box">
          <div class="slider-header">
            <span class="slider-name">THROUGHPUT</span>
            <span class="slider-val green">{{ simParams.throughput }} Mbps</span>
          </div>
          <input 
            type="range" 
            min="0.2" 
            max="150" 
            step="0.5" 
            v-model.number="simParams.throughput" 
            class="cyber-slider slider-green"
            @input="runSimDiagnosis"
          />
          <div class="slider-scale">
            <span>0.2 Mbps</span>
            <span>75 Mbps</span>
            <span>150 Mbps</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Simulation Diagnosis Output -->
    <div class="cyber-card sim-output-card" v-if="simDiagnosis">
      <div class="output-header">
        <div class="output-title-group">
          <span class="panel-tag">SIMULATION INFERENCE RESULT</span>
          <h3 class="output-title">{{ simDiagnosis.title }}</h3>
        </div>
        <div class="output-badge" :class="`badge-${simDiagnosis.severity}`">
          <span class="pulse-dot"></span>
          {{ (simDiagnosis.fault || '').toUpperCase().replace('_', ' ') }} ({{ simDiagnosis.confidence_percent }})
        </div>
      </div>

      <div class="output-details-grid">
        <div class="output-desc-box">
          <span class="box-tag">EXPLANATION</span>
          <p>{{ simDiagnosis.description }}</p>
        </div>

        <div class="output-actions-box">
          <span class="box-tag">PRIMARY RECOMMENDATION</span>
          <p>{{ simDiagnosis.recommendations[0] || 'Nominal operation.' }}</p>
        </div>
      </div>

      <!-- Probability Distribution Bar -->
      <div class="prob-distribution" v-if="simDiagnosis.class_probabilities && Object.keys(simDiagnosis.class_probabilities).length">
        <span class="prob-title">MODEL CLASS POSTERIOR PROBABILITIES:</span>
        <div class="prob-bars">
          <div 
            v-for="(prob, cls) in simDiagnosis.class_probabilities" 
            :key="cls" 
            class="prob-item"
          >
            <div class="prob-header">
              <span class="cls-name">{{ cls.replace('_', ' ') }}</span>
              <span class="cls-pct">{{ (prob * 100).toFixed(1) }}%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: `${prob * 100}%` }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { triggerCustomSimulation } from '../services/api';

const simParams = ref({
  minimum_latency: 22.0,
  maximum_latency: 26.0,
  average_latency: 24.0,
  packet_loss: 0.0,
  jitter: 1.5,
  throughput: 65.0
});

const simDiagnosis = ref(null);

const presets = {
  normal: { min: 20, max: 26, avg: 23, loss: 0, jitter: 1.5, tp: 70 },
  high_latency: { min: 215, max: 235, avg: 225, loss: 0, jitter: 3.5, tp: 15 },
  packet_loss: { min: 10, max: 28, avg: 14, loss: 10.0, jitter: 1.8, tp: 45 },
  high_jitter: { min: 15, max: 90, avg: 45, loss: 0, jitter: 32.0, tp: 60 },
  congestion: { min: 65, max: 120, avg: 92, loss: 4.0, jitter: 22.0, tp: 1.2 }
};

function loadPreset(key) {
  const p = presets[key];
  if (!p) return;
  simParams.value = {
    minimum_latency: p.min,
    maximum_latency: p.max,
    average_latency: p.avg,
    packet_loss: p.loss,
    jitter: p.jitter,
    throughput: p.tp
  };
  runSimDiagnosis();
}

async function runSimDiagnosis() {
  // Sync min/max with avg
  const avg = simParams.value.average_latency;
  const jit = simParams.value.jitter;
  simParams.value.minimum_latency = Math.max(5, Math.round(avg - jit * 1.5));
  simParams.value.maximum_latency = Math.round(avg + jit * 1.5);

  try {
    const res = await triggerCustomSimulation(simParams.value);
    simDiagnosis.value = res.diagnosis;
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

onMounted(() => {
  runSimDiagnosis();
});
</script>

<style scoped>
.simulation-view {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.simulation-panel {
  padding: 1.5rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.9rem;
  margin-bottom: 1rem;
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

.sim-pill {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--neon-green);
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
}

.sim-intro {
  font-size: 0.88rem;
  color: var(--text-secondary);
  margin-bottom: 1.25rem;
}

.presets-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.presets-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.preset-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.preset-btn {
  background: rgba(6, 9, 19, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: all 0.2s ease;
}

.preset-btn:hover {
  border-color: var(--cyan);
  background: rgba(0, 240, 255, 0.1);
}

.preset-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.preset-dot.green { background: var(--neon-green); }
.preset-dot.amber { background: var(--amber); }
.preset-dot.crimson { background: var(--crimson); }
.preset-dot.purple { background: var(--neon-purple); }

.sliders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.slider-box {
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.1);
  padding: 1rem 1.15rem;
  border-radius: 6px;
}

.slider-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.slider-name {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.slider-val {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  font-weight: 700;
}
.slider-val.cyan { color: var(--cyan); }
.slider-val.crimson { color: var(--crimson); }
.slider-val.purple { color: var(--neon-purple); }
.slider-val.green { color: var(--neon-green); }

.cyber-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.1);
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.cyber-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.8);
}

.slider-scale {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
}

/* Output Card */
.sim-output-card {
  padding: 1.5rem;
}

.output-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.9rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.output-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
}

.output-badge {
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.35rem 0.85rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.output-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.15rem;
  margin-bottom: 1.25rem;
}

.output-desc-box, .output-actions-box {
  background: rgba(6, 9, 19, 0.4);
  border: 1px solid rgba(0, 240, 255, 0.1);
  padding: 1rem;
  border-radius: 6px;
}

.box-tag {
  display: block;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cyan);
  letter-spacing: 1px;
  margin-bottom: 0.35rem;
}

.output-desc-box p, .output-actions-box p {
  font-size: 0.88rem;
  line-height: 1.4;
  color: var(--text-primary);
}

.prob-distribution {
  background: rgba(6, 9, 19, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 1rem;
  border-radius: 6px;
}

.prob-title {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  letter-spacing: 1px;
  display: block;
  margin-bottom: 0.75rem;
}

.prob-bars {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.85rem;
}

.prob-header {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  margin-bottom: 0.25rem;
}

.cls-name { color: var(--text-secondary); text-transform: uppercase; }
.cls-pct { color: var(--cyan); font-weight: 700; }

.bar-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--neon-green));
  border-radius: 2px;
  transition: width 0.4s ease;
}

@media (max-width: 900px) {
  .output-details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
