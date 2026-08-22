<template>
  <div class="history-view">
    <div class="cyber-card history-panel scanlines">
      <div class="panel-header">
        <div class="header-left">
          <span class="panel-tag">PERSISTENT TELEMETRY LOGS</span>
          <h2 class="panel-title">DIAGNOSTIC AUDIT TRAIL</h2>
        </div>
        <div class="header-controls">
          <button class="cyber-btn" @click="fetchHistory">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            REFRESH
          </button>
        </div>
      </div>

      <!-- Search & Filters -->
      <div class="filter-bar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search by fault, host, or timestamp..." 
            class="cyber-search-input"
          />
        </div>
        <div class="filter-pills">
          <button 
            class="filter-pill" 
            :class="{ active: activeFilter === 'all' }"
            @click="activeFilter = 'all'"
          >
            ALL ({{ historyList.length }})
          </button>
          <button 
            v-for="fault in uniqueFaults" 
            :key="fault" 
            class="filter-pill"
            :class="{ active: activeFilter === fault }"
            @click="activeFilter = fault"
          >
            {{ fault.toUpperCase().replace('_', ' ') }}
          </button>
        </div>
      </div>

      <!-- History Table -->
      <div class="table-wrapper">
        <table class="cyber-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>TIMESTAMP</th>
              <th>TARGET</th>
              <th>LATENCY</th>
              <th>LOSS</th>
              <th>JITTER</th>
              <th>THROUGHPUT</th>
              <th>AI DIAGNOSIS</th>
              <th>CONFIDENCE</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredHistory" :key="item.id" class="table-row">
              <td class="col-id">#{{ item.id }}</td>
              <td class="col-time">{{ item.timestamp }}</td>
              <td class="col-host">{{ item.host }}</td>
              <td class="col-num">{{ item.metrics.average_latency }} ms</td>
              <td class="col-num" :class="{ 'text-crimson': item.metrics.packet_loss > 0 }">
                {{ item.metrics.packet_loss }}%
              </td>
              <td class="col-num">{{ item.metrics.jitter }} ms</td>
              <td class="col-num">{{ item.metrics.throughput }} Mbps</td>
              <td>
                <span class="badge-status" :class="`badge-${item.diagnosis.severity || 'healthy'}`">
                  {{ item.diagnosis.fault.toUpperCase().replace('_', ' ') }}
                </span>
              </td>
              <td class="col-conf">{{ item.diagnosis.confidence_percent }}</td>
              <td>
                <button class="inspect-btn" @click="inspectRecord(item)">
                  VIEW
                </button>
              </td>
            </tr>
            <tr v-if="filteredHistory.length === 0">
              <td colspan="10" class="empty-table-cell">
                No matching diagnosis records found in SQLite database.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Inspection Modal -->
    <div class="modal-backdrop" v-if="selectedRecord" @click.self="selectedRecord = null">
      <div class="cyber-card modal-card">
        <div class="modal-header">
          <h3 class="modal-title">DIAGNOSIS INSPECTION: #{{ selectedRecord.id }}</h3>
          <button class="modal-close" @click="selectedRecord = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="modal-meta-grid">
            <div><span class="meta-lbl">Timestamp:</span> {{ selectedRecord.timestamp }}</div>
            <div><span class="meta-lbl">Target:</span> {{ selectedRecord.host }}</div>
            <div><span class="meta-lbl">Avg Latency:</span> {{ selectedRecord.metrics.average_latency }} ms</div>
            <div><span class="meta-lbl">Packet Loss:</span> {{ selectedRecord.metrics.packet_loss }}%</div>
            <div><span class="meta-lbl">Jitter:</span> {{ selectedRecord.metrics.jitter }} ms</div>
            <div><span class="meta-lbl">Throughput:</span> {{ selectedRecord.metrics.throughput }} Mbps</div>
          </div>

          <div class="modal-diag-box">
            <span class="badge-status" :class="`badge-${selectedRecord.diagnosis.severity}`">
              {{ selectedRecord.diagnosis.fault.toUpperCase().replace('_', ' ') }} ({{ selectedRecord.diagnosis.confidence_percent }})
            </span>
            <h4 class="modal-diag-title">{{ selectedRecord.diagnosis.title }}</h4>
            <p class="modal-desc">{{ selectedRecord.diagnosis.description }}</p>
          </div>

          <div class="modal-lists-grid">
            <div class="modal-list-box">
              <span class="box-tag amber">POSSIBLE CAUSES</span>
              <ul>
                <li v-for="(cause, idx) in selectedRecord.diagnosis.possible_causes" :key="idx">
                  {{ cause }}
                </li>
              </ul>
            </div>
            <div class="modal-list-box">
              <span class="box-tag green">RECOMMENDED ACTIONS</span>
              <ul>
                <li v-for="(act, idx) in selectedRecord.diagnosis.recommendations" :key="idx">
                  {{ act }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { fetchDiagnosisHistory } from '../services/api';

const historyList = ref([]);
const searchQuery = ref('');
const activeFilter = ref('all');
const selectedRecord = ref(null);

async function fetchHistory() {
  try {
    const data = await fetchDiagnosisHistory(100, 0);
    historyList.value = data;
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

const uniqueFaults = computed(() => {
  const set = new Set();
  historyList.value.forEach(item => {
    if (item.diagnosis && item.diagnosis.fault) {
      set.add(item.diagnosis.fault);
    }
  });
  return Array.from(set);
});

const filteredHistory = computed(() => {
  return historyList.value.filter(item => {
    const matchFilter = activeFilter.value === 'all' || (item.diagnosis && item.diagnosis.fault === activeFilter.value);
    const q = searchQuery.value.toLowerCase().trim();
    if (!q) return matchFilter;
    const matchSearch = (
      (item.timestamp && item.timestamp.toLowerCase().includes(q)) ||
      (item.host && item.host.toLowerCase().includes(q)) ||
      (item.diagnosis && item.diagnosis.fault && item.diagnosis.fault.toLowerCase().includes(q)) ||
      (item.diagnosis && item.diagnosis.title && item.diagnosis.title.toLowerCase().includes(q))
    );
    return matchFilter && matchSearch;
  });
});

function inspectRecord(rec) {
  selectedRecord.value = rec;
}

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
.history-panel {
  padding: 1.5rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.9rem;
  margin-bottom: 1.25rem;
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

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  background: rgba(6, 9, 19, 0.6);
  border: 1px solid rgba(0, 240, 255, 0.2);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  width: 320px;
}

.search-icon {
  margin-right: 0.4rem;
  font-size: 0.8rem;
}

.cyber-search-input {
  background: transparent;
  border: none;
  color: #fff;
  font-family: var(--font-body);
  font-size: 0.85rem;
  width: 100%;
  outline: none;
}

.filter-pills {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.filter-pill {
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-pill:hover, .filter-pill.active {
  border-color: var(--cyan);
  color: var(--cyan);
  background: rgba(0, 240, 255, 0.12);
}

.table-wrapper {
  overflow-x: auto;
}

.cyber-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.84rem;
}

.cyber-table th {
  font-family: var(--font-display);
  font-size: 0.72rem;
  letter-spacing: 1px;
  color: var(--text-muted);
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid rgba(0, 240, 255, 0.2);
  background: rgba(6, 9, 19, 0.6);
}

.cyber-table td {
  padding: 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.table-row:hover {
  background: rgba(0, 240, 255, 0.04);
}

.col-id { font-family: var(--font-mono); color: var(--text-muted); }
.col-time { font-family: var(--font-mono); color: var(--text-secondary); }
.col-host { font-family: var(--font-mono); color: var(--cyan); }
.col-num { font-family: var(--font-mono); }
.col-conf { font-family: var(--font-mono); font-weight: 700; color: var(--neon-green); }

.text-crimson { color: var(--crimson); font-weight: 700; }

.inspect-btn {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid var(--cyan);
  color: var(--cyan);
  font-family: var(--font-display);
  font-size: 0.7rem;
  padding: 0.25rem 0.6rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.inspect-btn:hover {
  background: var(--cyan);
  color: var(--bg-primary);
}

.empty-table-cell {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(6, 9, 19, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1.5rem;
}

.modal-card {
  width: 100%;
  max-width: 650px;
  padding: 1.5rem;
  background: #0d1426;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 240, 255, 0.2);
  padding-bottom: 0.8rem;
  margin-bottom: 1rem;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  color: #fff;
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1.2rem;
  cursor: pointer;
}
.modal-close:hover { color: #fff; }

.modal-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  background: rgba(6, 9, 19, 0.5);
  padding: 0.85rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}
.meta-lbl { color: var(--text-muted); margin-right: 0.35rem; }

.modal-diag-box {
  margin-bottom: 1rem;
}
.modal-diag-title { font-size: 1.05rem; margin: 0.5rem 0 0.3rem 0; color: #fff; }
.modal-desc { font-size: 0.88rem; color: var(--text-secondary); }

.modal-lists-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-list-box {
  background: rgba(6, 9, 19, 0.5);
  padding: 0.85rem;
  border-radius: 4px;
}
.modal-list-box ul { padding-left: 1.2rem; font-size: 0.8rem; color: var(--text-secondary); }
.modal-list-box li { margin-bottom: 0.35rem; }

.box-tag { display: block; font-family: var(--font-mono); font-size: 0.65rem; margin-bottom: 0.4rem; letter-spacing: 1px; font-weight: 700; }
.box-tag.amber { color: var(--amber); }
.box-tag.green { color: var(--neon-green); }
</style>
