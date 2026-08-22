<template>
  <div class="evaluation-view">
    <div class="cyber-card eval-panel scanlines">
      <div class="panel-header">
        <div class="header-left">
          <span class="panel-tag">RESEARCH METRICS & DEFENSE BENCHMARK</span>
          <h2 class="panel-title">MACHINE LEARNING MODEL EVALUATION</h2>
        </div>
        <div class="header-actions">
          <button class="cyber-btn" :disabled="retraining" @click="handleRetrain">
            <svg v-if="!retraining" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            <span v-else class="spinner-icon"></span>
            {{ retraining ? 'RETRAINING PIPELINE...' : 'RETRAIN MODEL' }}
          </button>
        </div>
      </div>

      <!-- High-Level Research Metrics Banner -->
      <div class="metrics-banner" v-if="metricsData && metricsData.selected_model_metrics">
        <div class="metric-block">
          <span class="m-label">ACTIVE MODEL</span>
          <span class="m-val cyan">{{ metricsData.model_name || 'Decision Tree' }}</span>
        </div>
        <div class="metric-block">
          <span class="m-label">ACCURACY</span>
          <span class="m-val green">{{ (metricsData.selected_model_metrics.accuracy * 100).toFixed(2) }}%</span>
        </div>
        <div class="metric-block">
          <span class="m-label">WEIGHTED F1-SCORE</span>
          <span class="m-val green">{{ metricsData.selected_model_metrics.f1_score.toFixed(4) }}</span>
        </div>
        <div class="metric-block">
          <span class="m-label">WEIGHTED PRECISION</span>
          <span class="m-val green">{{ metricsData.selected_model_metrics.precision.toFixed(4) }}</span>
        </div>
        <div class="metric-block">
          <span class="m-label">DATASET SAMPLES</span>
          <span class="m-val cyan">{{ (metricsData.train_samples || 0) + (metricsData.test_samples || 0) }}</span>
        </div>
      </div>

      <!-- Comparative Benchmark Table -->
      <div class="eval-section" v-if="metricsData && metricsData.model_comparisons">
        <h3 class="section-heading">
          <span class="accent-bar"></span>
          ALGORITHM BENCHMARK COMPARISON (RESEARCH EVALUATION)
        </h3>
        <p class="section-desc">
          Comparative evaluation of three supervised learning models trained using Stratified Train/Test Split (75% / 25%) with standardized feature scaling:
        </p>

        <div class="table-wrapper">
          <table class="cyber-table">
            <thead>
              <tr>
                <th>ALGORITHM</th>
                <th>ACCURACY</th>
                <th>F1-SCORE (WEIGHTED)</th>
                <th>PRECISION</th>
                <th>RECALL</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(modelData, mName) in metricsData.model_comparisons" 
                :key="mName"
                :class="{ 'highlight-row': mName === metricsData.model_name }"
              >
                <td class="col-mname">
                  <strong>{{ mName }}</strong>
                  <span v-if="mName === metricsData.model_name" class="best-badge">SELECTED</span>
                </td>
                <td class="col-num">{{ (modelData.accuracy * 100).toFixed(2) }}%</td>
                <td class="col-num bold">{{ modelData.f1_score.toFixed(4) }}</td>
                <td class="col-num">{{ modelData.precision.toFixed(4) }}</td>
                <td class="col-num">{{ modelData.recall.toFixed(4) }}</td>
                <td>
                  <span class="badge-status" :class="mName === metricsData.model_name ? 'badge-healthy' : 'badge-warning'">
                    {{ mName === metricsData.model_name ? 'ACTIVE DEPLOYMENT' : 'CANDIDATE' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Confusion Matrix & Class Distribution Split -->
      <div class="split-eval-grid" v-if="metricsData && metricsData.target_classes">
        <!-- Confusion Matrix Heatmap -->
        <div class="eval-sub-box">
          <h4 class="sub-heading">
            CONFUSION MATRIX HEATMAP
          </h4>
          <p class="sub-caption">Test Partition (n = {{ metricsData.test_samples || 25 }})</p>

          <div class="cm-table-wrapper" v-if="metricsData.selected_model_metrics.confusion_matrix">
            <table class="cm-table">
              <thead>
                <tr>
                  <th class="cm-corner">Actual \ Pred</th>
                  <th v-for="cls in metricsData.target_classes" :key="cls" class="cm-header-cell">
                    {{ cls.replace('_', ' ') }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rIdx) in metricsData.selected_model_metrics.confusion_matrix" :key="rIdx">
                  <td class="cm-row-label">{{ metricsData.target_classes[rIdx].replace('_', ' ') }}</td>
                  <td 
                    v-for="(val, cIdx) in row" 
                    :key="cIdx" 
                    class="cm-cell"
                    :class="getCellHeatClass(rIdx, cIdx, val)"
                  >
                    {{ val }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Class Distribution -->
        <div class="eval-sub-box">
          <h4 class="sub-heading">DATASET CLASS REPRESENTATION</h4>
          <p class="sub-caption">Independent sample counts collected in WSL2:</p>

          <div class="dist-list" v-if="metricsData.class_distribution">
            <div v-for="(count, cls) in metricsData.class_distribution" :key="cls" class="dist-row">
              <div class="dist-header">
                <span class="dist-name">{{ cls.replace('_', ' ').toUpperCase() }}</span>
                <span class="dist-count">{{ count }} samples</span>
              </div>
              <div class="dist-bar-track">
                <div 
                  class="dist-bar-fill"
                  :style="{ width: `${(count / totalSamples) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { fetchModelPerformance, triggerModelRetrain } from '../services/api';

const metricsData = ref(null);
const retraining = ref(false);

async function loadMetrics() {
  try {
    const data = await fetchModelPerformance();
    if (data && data.status !== 'not_trained') {
      metricsData.value = data;
    }
  } catch (err) {
    console.error('Error loading model metrics:', err);
  }
}

async function handleRetrain() {
  retraining.value = true;
  try {
    await triggerModelRetrain();
    await loadMetrics();
  } catch (err) {
    console.error('Failed to retrain:', err);
  } finally {
    retraining.value = false;
  }
}

const totalSamples = computed(() => {
  if (!metricsData.value || !metricsData.value.class_distribution) return 1;
  return Object.values(metricsData.value.class_distribution).reduce((a, b) => a + b, 0);
});

function getCellHeatClass(rIdx, cIdx, val) {
  if (val === 0) return 'cm-zero';
  if (rIdx === cIdx) return 'cm-correct';
  return 'cm-error';
}

onMounted(() => {
  loadMetrics();
});
</script>

<style scoped>
.eval-panel {
  padding: 1.5rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.9rem;
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

.metrics-banner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  background: rgba(6, 9, 19, 0.6);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 6px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
}

.metric-block {
  display: flex;
  flex-direction: column;
}

.m-label {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  letter-spacing: 1px;
  margin-bottom: 0.25rem;
}

.m-val {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 800;
}
.m-val.cyan { color: var(--cyan); }
.m-val.green { color: var(--neon-green); text-shadow: 0 0 12px rgba(0, 255, 136, 0.4); }

.eval-section {
  margin-bottom: 1.5rem;
}

.section-heading {
  font-family: var(--font-display);
  font-size: 0.95rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.accent-bar {
  width: 4px;
  height: 16px;
  background: var(--cyan);
  border-radius: 2px;
}

.section-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0.9rem;
}

.table-wrapper {
  overflow-x: auto;
}

.cyber-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.cyber-table th {
  font-family: var(--font-display);
  font-size: 0.72rem;
  color: var(--text-muted);
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid rgba(0, 240, 255, 0.2);
  background: rgba(6, 9, 19, 0.6);
}

.cyber-table td {
  padding: 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-family: var(--font-mono);
  font-size: 0.82rem;
}

.highlight-row {
  background: rgba(0, 240, 255, 0.08);
}

.col-mname {
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.best-badge {
  background: var(--cyan);
  color: var(--bg-primary);
  font-family: var(--font-display);
  font-size: 0.6rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
}

.split-eval-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.eval-sub-box {
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.15);
  border-radius: 6px;
  padding: 1.15rem;
}

.sub-heading {
  font-family: var(--font-display);
  font-size: 0.85rem;
  color: var(--cyan);
  letter-spacing: 1px;
  margin-bottom: 0.25rem;
}

.sub-caption {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-bottom: 0.9rem;
}

/* Confusion Matrix Heatmap */
.cm-table-wrapper {
  overflow-x: auto;
}

.cm-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  font-family: var(--font-mono);
}

.cm-corner {
  font-size: 0.65rem;
  color: var(--text-muted);
  padding: 0.45rem;
}

.cm-header-cell {
  font-size: 0.68rem;
  color: var(--cyan);
  padding: 0.45rem;
  text-transform: uppercase;
}

.cm-row-label {
  font-size: 0.68rem;
  color: var(--text-secondary);
  text-align: right;
  padding: 0.45rem 0.6rem;
  text-transform: uppercase;
}

.cm-cell {
  padding: 0.6rem;
  font-weight: 700;
  font-size: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.cm-correct {
  background: rgba(0, 255, 136, 0.25);
  color: var(--neon-green);
  box-shadow: inset 0 0 10px rgba(0, 255, 136, 0.3);
}

.cm-error {
  background: rgba(255, 0, 85, 0.3);
  color: var(--crimson);
}

.cm-zero {
  color: var(--text-muted);
  opacity: 0.4;
}

/* Distribution List */
.dist-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dist-header {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
}

.dist-name { color: #fff; }
.dist-count { color: var(--cyan); font-weight: 700; }

.dist-bar-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.dist-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--neon-purple));
  border-radius: 3px;
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

@media (max-width: 900px) {
  .split-eval-grid {
    grid-template-columns: 1fr;
  }
}
</style>
