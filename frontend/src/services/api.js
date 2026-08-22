const API_BASE = '/api';

export async function fetchSystemStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error('Failed to fetch status');
  return res.json();
}

export async function fetchClientNetworkInfo() {
  const res = await fetch(`${API_BASE}/client-network-info`);
  if (!res.ok) throw new Error('Failed to fetch client network info');
  return res.json();
}

export async function fetchLiveMetrics(host = '8.8.8.8', count = 10, speed = true) {
  const res = await fetch(`${API_BASE}/metrics?host=${encodeURIComponent(host)}&count=${count}&speed=${speed}`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
}

export async function fetchRealtimeStream(host = '8.8.8.8') {
  const res = await fetch(`${API_BASE}/realtime-stream?host=${encodeURIComponent(host)}`);
  if (!res.ok) throw new Error('Failed to stream realtime probe');
  return res.json();
}

export async function fetchMultiProbe() {
  const res = await fetch(`${API_BASE}/multi-probe`);
  if (!res.ok) throw new Error('Failed to fetch multi probe');
  return res.json();
}

export async function triggerLiveDiagnosis(host = '8.8.8.8', count = 10, speed = true) {
  const res = await fetch(`${API_BASE}/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, count, speed })
  });
  if (!res.ok) throw new Error('Diagnosis failed');
  return res.json();
}

export async function triggerCustomSimulation(metricsPayload) {
  const res = await fetch(`${API_BASE}/diagnose-custom`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metricsPayload)
  });
  if (!res.ok) throw new Error('Custom diagnosis failed');
  return res.json();
}

export async function fetchDiagnosisHistory(limit = 50, offset = 0) {
  const res = await fetch(`${API_BASE}/history?limit=${limit}&offset=${offset}`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function fetchTelemetryStream(limit = 60) {
  const res = await fetch(`${API_BASE}/telemetry?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch telemetry stream');
  return res.json();
}

export async function fetchStatistics() {
  const res = await fetch(`${API_BASE}/statistics`);
  if (!res.ok) throw new Error('Failed to fetch statistics');
  return res.json();
}

export async function fetchModelPerformance() {
  const res = await fetch(`${API_BASE}/model-performance`);
  if (!res.ok) throw new Error('Failed to fetch model metrics');
  return res.json();
}

export async function triggerModelRetrain() {
  const res = await fetch(`${API_BASE}/retrain`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Model retraining failed');
  return res.json();
}
