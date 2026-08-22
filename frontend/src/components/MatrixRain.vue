<template>
  <div class="matrix-container" :class="{ 'matrix-hidden': !enabled }">
    <canvas ref="canvasRef" class="matrix-canvas"></canvas>
    <div class="matrix-overlay"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  enabled: {
    type: Boolean,
    default: true
  },
  opacity: {
    type: Number,
    default: 0.18
  }
});

const canvasRef = ref(null);
let animationFrameId = null;
let drops = [];
let characters = '01100101011101000110100000100000011011100110010101110100011001010110110101001001010000110100110101010000ABCDEF0123456789λΩΨ⚡⌘⌥⎇';
const fontSize = 14;

function initCanvas() {
  const canvas = canvasRef.value;
  if (!canvas) return;

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const columns = Math.floor(canvas.width / fontSize);
  drops = [];
  for (let i = 0; i < columns; i++) {
    drops[i] = Math.floor(Math.random() * -100);
  }
}

function drawMatrix() {
  const canvas = canvasRef.value;
  if (!canvas || !props.enabled) return;

  const ctx = canvas.getContext('2d');

  // Slight fade effect
  ctx.fillStyle = 'rgba(6, 9, 19, 0.08)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.font = `${fontSize}px 'Fira Code', monospace`;

  for (let i = 0; i < drops.length; i++) {
    const text = characters.charAt(Math.floor(Math.random() * characters.length));
    const x = i * fontSize;
    const y = drops[i] * fontSize;

    // Glowing head of the stream
    if (Math.random() > 0.95) {
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 8;
    } else {
      ctx.fillStyle = i % 4 === 0 ? 'rgba(0, 240, 255, 0.85)' : 'rgba(0, 255, 136, 0.75)';
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
    }

    ctx.fillText(text, x, y);

    if (y > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i]++;
  }

  animationFrameId = requestAnimationFrame(drawMatrix);
}

function handleResize() {
  initCanvas();
}

onMounted(() => {
  initCanvas();
  window.addEventListener('resize', handleResize);
  if (props.enabled) {
    animationFrameId = requestAnimationFrame(drawMatrix);
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});

watch(() => props.enabled, (newVal) => {
  if (newVal) {
    initCanvas();
    animationFrameId = requestAnimationFrame(drawMatrix);
  } else if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    const canvas = canvasRef.value;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }
});
</script>

<style scoped>
.matrix-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
  opacity: v-bind('props.opacity');
  transition: opacity 0.5s ease;
}

.matrix-hidden {
  opacity: 0;
}

.matrix-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.matrix-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, transparent 30%, rgba(6, 9, 19, 0.85) 90%);
}
</style>
