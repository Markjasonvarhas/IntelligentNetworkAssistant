<template>
  <div class="cyber-card quality-panel scanlines">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-tag">NETWORK QUALITY INDEX & QOS ASSURANCE</span>
        <h3 class="panel-title">EXPERIENCE & HEALTH RATINGS</h3>
      </div>
      <div class="mos-pill">
        <span class="mos-lbl">VOIP MOS:</span>
        <span class="mos-val">{{ healthScores.mos_score || '4.40' }} / 4.50</span>
      </div>
    </div>

    <div class="ratings-grid">
      <!-- Overall Health Index Radial -->
      <div class="health-score-box">
        <div class="score-circle">
          <svg viewBox="0 0 100 100" class="score-svg">
            <circle cx="50" cy="50" r="40" class="score-bg"/>
            <circle 
              cx="50" cy="50" r="40" 
              class="score-progress"
              :class="getHealthClass(healthScores.overall_health_score)"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
            />
          </svg>
          <div class="score-text">
            <span class="score-num">{{ Math.round(healthScores.overall_health_score || 95) }}</span>
            <span class="score-unit">/ 100</span>
          </div>
        </div>
        <span class="score-caption">HEALTH INDEX</span>
      </div>

      <!-- Application Experience Tiers -->
      <div class="tier-cards">
        <!-- Gaming Tier -->
        <div class="tier-card" :class="`tier-${healthScores.gaming?.status || 'optimal'}`">
          <div class="tier-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/>
              <line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/>
              <rect x="2" y="6" width="20" height="12" rx="6"/>
            </svg>
          </div>
          <div class="tier-info">
            <span class="tier-category">GAMING RESPONSIVENESS</span>
            <span class="tier-badge">{{ healthScores.gaming?.grade || 'S Tier (Ultra Responsive)' }}</span>
          </div>
        </div>

        <!-- 4K Video Streaming Tier -->
        <div class="tier-card" :class="`tier-${healthScores.streaming?.status || 'optimal'}`">
          <div class="tier-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7"/>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
            </svg>
          </div>
          <div class="tier-info">
            <span class="tier-category">4K VIDEO STREAMING</span>
            <span class="tier-badge">{{ healthScores.streaming?.grade || '4K UHD (Buffer-Free)' }}</span>
          </div>
        </div>

        <!-- VoIP / Call Tier -->
        <div class="tier-card" :class="`tier-${healthScores.voip?.status || 'optimal'}`">
          <div class="tier-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </div>
          <div class="tier-info">
            <span class="tier-category">VOIP & VIDEO CONFERENCING</span>
            <span class="tier-badge">{{ healthScores.voip?.grade || 'HD Voice (Lossless)' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  healthScores: {
    type: Object,
    default: () => ({
      overall_health_score: 95.0,
      mos_score: 4.40,
      gaming: { grade: 'S Tier (Ultra Responsive)', status: 'optimal' },
      streaming: { grade: '4K UHD (Buffer-Free)', status: 'optimal' },
      voip: { grade: 'HD Voice (Lossless)', status: 'optimal' }
    })
  }
});

const circumference = 2 * Math.PI * 40; // ~251.32

const dashOffset = computed(() => {
  const score = props.healthScores?.overall_health_score || 95;
  return circumference - ((score / 100) * circumference);
});

function getHealthClass(score) {
  if (!score && score !== 0) return 'progress-optimal';
  if (score >= 80) return 'progress-optimal';
  if (score >= 50) return 'progress-fair';
  return 'progress-poor';
}
</script>

<style scoped>
.quality-panel {
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 240, 255, 0.15);
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
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

.mos-pill {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  padding: 0.3rem 0.65rem;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  display: flex;
  gap: 0.4rem;
}
.mos-lbl { color: var(--text-muted); }
.mos-val { color: var(--cyan); font-weight: 700; }

.ratings-grid {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 1.5rem;
  align-items: center;
}

.health-score-box {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-circle {
  position: relative;
  width: 105px;
  height: 105px;
}

.score-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.score-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 8;
}

.score-progress {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease-in-out;
}

.progress-optimal {
  stroke: var(--neon-green);
  filter: drop-shadow(0 0 6px var(--neon-green));
}
.progress-fair {
  stroke: var(--amber);
  filter: drop-shadow(0 0 6px var(--amber));
}
.progress-poor {
  stroke: var(--crimson);
  filter: drop-shadow(0 0 6px var(--crimson));
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-num {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}

.score-unit {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

.score-caption {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-secondary);
  margin-top: 0.4rem;
  letter-spacing: 1px;
}

.tier-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.85rem;
}

.tier-card {
  background: rgba(6, 9, 19, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.2s ease;
}

.tier-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

.tier-optimal .tier-icon {
  color: var(--neon-green);
  background: rgba(0, 255, 136, 0.12);
}
.tier-good .tier-icon {
  color: var(--cyan);
  background: rgba(0, 240, 255, 0.12);
}
.tier-fair .tier-icon {
  color: var(--amber);
  background: rgba(255, 183, 3, 0.12);
}
.tier-poor .tier-icon {
  color: var(--crimson);
  background: rgba(255, 0, 85, 0.12);
}

.tier-info {
  display: flex;
  flex-direction: column;
}

.tier-category {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.tier-badge {
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 700;
  color: #fff;
}

.tier-optimal .tier-badge { color: var(--neon-green); }
.tier-good .tier-badge { color: var(--cyan); }
.tier-fair .tier-badge { color: var(--amber); }
.tier-poor .tier-badge { color: var(--crimson); }

@media (max-width: 768px) {
  .ratings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
