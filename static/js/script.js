/**
 * script.js
 * =========
 * Frontend JavaScript for the AI Agent for Seasonal Crop Planning.
 * Handles form submission, API communication, result rendering,
 * Chart.js visualizations, and UI interactions.
 */

'use strict';

// ─── CROP EMOJI MAP ───────────────────────────────────────────
const CROP_EMOJIS = {
  rice:        '🍚', maize:      '🌽', wheat:      '🌾',
  chickpea:    '🫘', cotton:     '🌿', lentil:     '🫛',
  pigeonpeas:  '🌱', blackgram:  '🫘', mungbean:   '🫘',
  banana:      '🍌', mango:      '🥭', apple:      '🍎',
  grapes:      '🍇', watermelon: '🍉', muskmelon:  '🍈',
  orange:      '🍊', papaya:     '🥝', coconut:    '🥥',
  coffee:      '☕', jute:       '🌿', kidneybeans:'🫘',
  mothbeans:   '🌱', pomegranate:'🍒', sugarcane:  '🌿',
  default:     '🌾',
};

function getCropEmoji(crop) {
  return CROP_EMOJIS[crop?.toLowerCase()] || CROP_EMOJIS.default;
}

// ─── CHART INSTANCES ──────────────────────────────────────────
let barChartInstance   = null;
let radarChartInstance = null;

// ─── CHART.JS DEFAULTS ────────────────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";

// ═════════════════════════════════════════════════════════════
// HEALTH CHECK
// ═════════════════════════════════════════════════════════════
async function checkSystemHealth() {
  const banner = document.getElementById('systemStatus');
  const text   = document.getElementById('systemStatusText');
  if (!banner || !text) return;

  try {
    const res  = await fetch('/api/health');
    const data = await res.json();

    if (data.model_ready && data.dataset_ready) {
      banner.classList.add('status-banner--ready');
      text.textContent = '✓ System ready — model and dataset loaded successfully.';
    } else if (data.model_ready && !data.dataset_ready) {
      banner.classList.add('status-banner--ready');
      text.textContent = '✓ Model ready. Dataset path info: ' + (data.dataset_message || '');
    } else {
      banner.classList.add('status-banner--error');
      let msg = '⚠ ';
      if (!data.model_ready)   msg += data.model_message   || 'Model not ready. ';
      if (!data.dataset_ready) msg += data.dataset_message || 'Dataset not ready.';
      text.textContent = msg;
    }
  } catch (err) {
    banner.classList.add('status-banner--error');
    text.textContent = '⚠ Could not reach the Flask server. Is python app.py running?';
  }
}

// ═════════════════════════════════════════════════════════════
// FORM VALIDATION
// ═════════════════════════════════════════════════════════════
function collectFormData() {
  const f = document.getElementById('plannerForm');
  const waterVal = f.querySelector('input[name="water_availability"]:checked');

  return {
    location:           f.querySelector('#location')?.value?.trim() || '',
    season:             f.querySelector('#season')?.value || '',
    N:                  f.querySelector('#nitrogen')?.value || '',
    P:                  f.querySelector('#phosphorus')?.value || '',
    K:                  f.querySelector('#potassium')?.value || '',
    ph:                 f.querySelector('#ph')?.value || '',
    land_area:          f.querySelector('#landArea')?.value || '',
    temperature:        f.querySelector('#temperature')?.value || '',
    humidity:           f.querySelector('#humidity')?.value || '',
    rainfall:           f.querySelector('#rainfall')?.value || '',
    water_availability: waterVal ? waterVal.value : '',
  };
}

function clientSideValidate(data) {
  const errors = [];
  const numericChecks = [
    { key: 'N',           min: 0,    max: 300,  label: 'Nitrogen (N)' },
    { key: 'P',           min: 0,    max: 300,  label: 'Phosphorus (P)' },
    { key: 'K',           min: 0,    max: 300,  label: 'Potassium (K)' },
    { key: 'temperature', min: -10,  max: 55,   label: 'Temperature' },
    { key: 'humidity',    min: 0,    max: 100,  label: 'Humidity' },
    { key: 'ph',          min: 0,    max: 14,   label: 'Soil pH' },
    { key: 'rainfall',    min: 0,    max: 5000, label: 'Rainfall' },
    { key: 'land_area',   min: 0.01, max: 10000,label: 'Land Area' },
  ];

  for (const { key, min, max, label } of numericChecks) {
    const raw = data[key];
    if (raw === '' || raw == null) {
      errors.push(`${label} is required.`);
      continue;
    }
    const val = parseFloat(raw);
    if (isNaN(val)) {
      errors.push(`${label} must be a valid number.`);
    } else if (val < min || val > max) {
      errors.push(`${label} must be between ${min} and ${max}. You entered: ${val}`);
    }
  }

  if (!data.season) errors.push('Season is required.');
  if (!data.water_availability) errors.push('Water availability is required.');

  return errors;
}

function showFormErrors(errors) {
  const box = document.getElementById('formErrors');
  if (!box) return;
  if (!errors || errors.length === 0) {
    box.classList.add('hidden');
    box.innerHTML = '';
    return;
  }
  box.classList.remove('hidden');
  box.innerHTML = `<ul>${errors.map(e => `<li>${e}</li>`).join('')}</ul>`;
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ═════════════════════════════════════════════════════════════
// SUBMIT HANDLER
// ═════════════════════════════════════════════════════════════
async function handleFormSubmit(e) {
  e.preventDefault();

  const data   = collectFormData();
  const errors = clientSideValidate(data);

  showFormErrors(errors);
  if (errors.length > 0) return;

  // Show loader
  const btn    = document.getElementById('submitBtn');
  const loader = document.getElementById('submitLoader');
  const btnTxt = btn.querySelector('.btn__text');
  btn.disabled = true;
  loader.classList.remove('hidden');
  btnTxt.textContent = 'Analysing…';

  try {
    const res  = await fetch('/api/plan', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });

    const result = await res.json();

    if (!res.ok) {
      const msg = result.details
        ? result.details
        : [result.error || 'Server error. Please try again.'];
      showFormErrors(Array.isArray(msg) ? msg : [msg]);
      return;
    }

    // Hide planner, show results
    renderResults(result, data);

  } catch (err) {
    showFormErrors([`Network error: ${err.message}. Is Flask running?`]);
  } finally {
    btn.disabled = false;
    loader.classList.add('hidden');
    btnTxt.textContent = 'Generate Crop Plan';
  }
}

// ═════════════════════════════════════════════════════════════
// RENDER RESULTS
// ═════════════════════════════════════════════════════════════
function renderResults(plan, formData) {
  // Show results section
  const resultsEl = document.getElementById('results');
  resultsEl.classList.remove('hidden');
  resultsEl.scrollIntoView({ behavior: 'smooth' });

  const crop      = plan.recommended_crop;
  const emoji     = getCropEmoji(crop);
  const modelScore = parseFloat(plan.model_score || 0);
  const finalScore = parseFloat(plan.final_score  || 0);
  const recs       = plan.recommendations || [];
  const topRec     = recs[0] || {};

  // ── Location subtitle ──
  const locEl = document.getElementById('resultLocation');
  if (locEl) {
    locEl.textContent = formData.location
      ? `Location: ${formData.location} | Season: ${formData.season}`
      : `Season: ${formData.season}`;
  }

  // ── Top crop card ──
  setText('topCropIcon', emoji);
  setText('topCropName', crop.charAt(0).toUpperCase() + crop.slice(1));
  setText('topCropSeason',
    topRec.suitable_seasons?.length
      ? 'Suitable: ' + topRec.suitable_seasons.join(', ')
      : '');

  // Animated score circle
  animateScoreCircle('scoreArc', modelScore);
  setText('modelScoreVal', `${modelScore.toFixed(1)}%`);
  setText('finalScoreVal', finalScore.toFixed(1));

  // ── Summary cards ──
  setText('sumSeason',   formData.season);
  setText('sumWater',    topRec.water_requirement || '—');
  setText('sumDuration', topRec.growing_duration  || '—');
  setText('sumLand',     formData.land_area ? `${formData.land_area} ac` : '—');

  // ── Charts ──
  renderBarChart(plan.top5_ml_scores || recs);
  renderRadarChart(formData);

  // ── Top 5 Table ──
  renderRecsTable(recs);

  // ── Comparison Cards ──
  renderComparisonCards(recs);

  // ── Environmental Analysis ──
  renderEnvAnalysis(plan.environment_analysis || []);

  // ── Seasonal Analysis ──
  setText('seasonAnalysis', plan.season_analysis || '—');
  renderSeasonInfo(plan.season_info || {});

  // ── Water Analysis ──
  const waterEl = document.getElementById('waterAnalysis');
  if (waterEl) {
    const warn = plan.water_warning;
    waterEl.textContent = plan.water_analysis || '—';
    waterEl.style.color = warn ? '#fbbf24' : '';
  }

  // ── Advisory ──
  setText('advisoryText', plan.advisory || '—');
  const badgeEl = document.getElementById('advisoryBadge');
  if (badgeEl && plan.advisory_source) {
    badgeEl.textContent = `⚡ ${plan.advisory_source}`;
  }

  // ── Explanation steps ──
  renderExplanation(plan.explanation || []);
  renderLocationAnalysis(plan.location_analysis || {});

  // ── Nav highlight ──
  setActiveNav('results');
}

// ─── SCORE CIRCLE ANIMATION ────────────────────────────────
function animateScoreCircle(arcId, pct) {
  const arc  = document.getElementById(arcId);
  if (!arc) return;
  const circ = 2 * Math.PI * 42; // r=42
  const fill = (pct / 100) * circ;
  // Small delay for visual effect
  setTimeout(() => {
    arc.setAttribute('stroke-dasharray', `${fill} ${circ - fill}`);
  }, 300);
}

// ─── BAR CHART ────────────────────────────────────────────
function renderBarChart(scores) {
  const ctx = document.getElementById('barChart');
  if (!ctx) return;

  const top5 = scores.slice(0, 5);
  const labels = top5.map(s => (s.crop || '').charAt(0).toUpperCase() + (s.crop || '').slice(1));
  const values = top5.map(s => parseFloat(s.model_score || 0).toFixed(2));

  if (barChartInstance) barChartInstance.destroy();

  barChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Model Suitability Score (%)',
        data: values,
        backgroundColor: [
          'rgba(34,197,94,0.7)',
          'rgba(34,197,94,0.5)',
          'rgba(34,197,94,0.4)',
          'rgba(34,197,94,0.3)',
          'rgba(34,197,94,0.2)',
        ],
        borderColor: 'rgba(34,197,94,0.9)',
        borderWidth: 1.5,
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.parsed.y}% model suitability`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8', font: { size: 12 } }
        },
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: {
            color: '#94a3b8',
            callback: v => v + '%'
          }
        }
      },
      animation: { duration: 900, easing: 'easeOutQuart' }
    }
  });
}

// ─── RADAR CHART ────────────────────────────────────────────
function renderRadarChart(formData) {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;

  // Normalize each param to 0–100 scale for radar readability
  const normalize = (val, min, max) => {
    const v = parseFloat(val) || 0;
    return Math.min(100, Math.max(0, ((v - min) / (max - min)) * 100));
  };

  const radarData = [
    normalize(formData.N,           0,   300),
    normalize(formData.P,           0,   300),
    normalize(formData.K,           0,   300),
    normalize(formData.temperature, -10, 55),
    normalize(formData.humidity,    0,   100),
    normalize(formData.ph,          0,   14),
    normalize(formData.rainfall,    0,   3000),
  ];

  const labels = ['Nitrogen\n(N)', 'Phosphorus\n(P)', 'Potassium\n(K)',
                   'Temperature', 'Humidity', 'Soil pH', 'Rainfall'];

  if (radarChartInstance) radarChartInstance.destroy();

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels,
      datasets: [{
        label: 'Normalised Input (0–100)',
        data: radarData,
        backgroundColor: 'rgba(34,197,94,0.12)',
        borderColor: 'rgba(34,197,94,0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(34,197,94,0.9)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.parsed.r.toFixed(1)} (normalised)`
          }
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          grid:     { color: 'rgba(255,255,255,0.07)' },
          angleLines:{ color: 'rgba(255,255,255,0.07)' },
          ticks:    { display: false },
          pointLabels:{ color: '#94a3b8', font: { size: 11 } }
        }
      },
      animation: { duration: 900 }
    }
  });
}

// ─── RECOMMENDATIONS TABLE ──────────────────────────────────
function renderRecsTable(recs) {
  const tbody = document.getElementById('recTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  recs.forEach((r, i) => {
    const cropName = r.crop.charAt(0).toUpperCase() + r.crop.slice(1);
    const emoji    = getCropEmoji(r.crop);
    const pct      = parseFloat(r.model_score || 0).toFixed(1);
    const final    = parseFloat(r.final_score  || 0).toFixed(1);
    const seasonOk = r.season_compatible;
    const waterOk  = r.water_compatible;

    const tr = document.createElement('tr');
    if (i === 0) tr.classList.add('top-row');
    tr.innerHTML = `
      <td><span class="rank-badge rank-badge--${i+1}">${i+1}</span></td>
      <td>${emoji} <strong>${cropName}</strong></td>
      <td>
        <div class="score-bar">
          <div class="score-bar__track">
            <div class="score-bar__fill" style="width:${pct}%"></div>
          </div>
          <span class="score-bar__val">${pct}%</span>
        </div>
      </td>
      <td>
        <div class="score-bar">
          <div class="score-bar__track">
            <div class="score-bar__fill" style="width:${final}%"></div>
          </div>
          <span class="score-bar__val">${final}</span>
        </div>
      </td>
      <td>
        <span class="compat-tag ${seasonOk ? 'compat-tag--ok' : 'compat-tag--warn'}">
          ${seasonOk ? '✓' : '⚠'} ${seasonOk ? 'Compatible' : 'Check'}
        </span>
      </td>
      <td>${r.water_requirement || '—'}</td>
      <td>${r.growing_duration  || '—'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ─── COMPARISON CARDS ───────────────────────────────────────
function renderComparisonCards(recs) {
  const container = document.getElementById('comparisonCards');
  if (!container) return;
  container.innerHTML = '';

  recs.slice(0, 5).forEach((r, i) => {
    const cropName = r.crop.charAt(0).toUpperCase() + r.crop.slice(1);
    const emoji    = getCropEmoji(r.crop);

    const div = document.createElement('div');
    div.className = 'comp-card' + (i === 0 ? ' comp-card--top' : '');
    div.innerHTML = `
      <div class="comp-card__crop">${emoji} ${cropName}</div>
      <div class="comp-card__row">
        <span>Model Score</span>
        <span class="comp-card__val">${parseFloat(r.model_score||0).toFixed(1)}%</span>
      </div>
      <div class="comp-card__row">
        <span>Combined</span>
        <span class="comp-card__val">${parseFloat(r.final_score||0).toFixed(1)}/100</span>
      </div>
      <div class="comp-card__row">
        <span>Season</span>
        <span class="comp-card__val">${r.season_compatible ? '✓ Good' : '⚠ Check'}</span>
      </div>
      <div class="comp-card__row">
        <span>Water Req.</span>
        <span class="comp-card__val">${r.water_requirement || '—'}</span>
      </div>
      <div class="comp-card__row">
        <span>Duration</span>
        <span class="comp-card__val">${r.growing_duration || '—'}</span>
      </div>
      <div class="comp-card__note">${r.key_consideration || ''}</div>
    `;
    container.appendChild(div);
  });
}

// ─── ENVIRONMENTAL ANALYSIS ─────────────────────────────────
function renderEnvAnalysis(items) {
  const container = document.getElementById('envAnalysis');
  if (!container) return;
  container.innerHTML = '';

  items.forEach(item => {
    const icons = { ok: '✓', warning: '⚠', info: 'ℹ' };
    const div = document.createElement('div');
    div.className = `env-item env-item--${item.type}`;
    div.innerHTML = `
      <span class="env-item__icon">${icons[item.type] || 'ℹ'}</span>
      <span class="env-item__msg">${item.message}</span>
    `;
    container.appendChild(div);
  });
}

// ─── SEASON INFO ────────────────────────────────────────────
function renderSeasonInfo(info) {
  const box = document.getElementById('seasonInfo');
  if (!box) return;
  if (!info || !info.description) { box.innerHTML = ''; return; }

  box.innerHTML = `
    <strong>${info.description || ''}</strong><br/>
    ${info.general_conditions || ''}
    ${info.crops?.length
      ? '<br/><br/><strong>Generally associated crops:</strong> ' + info.crops.slice(0,8).join(', ')
      : ''}
  `;
}

// ─── EXPLANATION STEPS ──────────────────────────────────────
function renderExplanation(steps) {
  const container = document.getElementById('explainSteps');
  if (!container) return;
  container.innerHTML = '';

  steps.forEach(s => {
    const div = document.createElement('div');
    div.className = 'explain-step';
    div.innerHTML = `
      <div class="explain-step__num">${s.step}</div>
      <div class="explain-step__content">
        <div class="explain-step__title">${s.title}</div>
        <div class="explain-step__detail">${s.detail}</div>
      </div>
    `;
    container.appendChild(div);
  });
}

// ═════════════════════════════════════════════════════════════
// UTILITY HELPERS
// ═════════════════════════════════════════════════════════════
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val || '—';
}

function setActiveNav(section) {
  document.querySelectorAll('.nav__link').forEach(a => {
    a.classList.toggle('active', a.dataset.section === section);
  });
}

// ─── SMOOTH SCROLL NAV ────────────────────────────────────
function initNavigation() {
  document.querySelectorAll('.nav__link, .hero__cta a, #heroStartBtn').forEach(link => {
    link.addEventListener('click', e => {
      const href = link.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });

        // Close mobile menu
        const nav = document.getElementById('nav');
        nav?.classList.remove('open');

        // Update active
        const section = href.slice(1);
        setActiveNav(section);
      }
    });
  });

  // Mobile menu toggle
  const menuBtn = document.getElementById('menuBtn');
  const nav     = document.getElementById('nav');
  menuBtn?.addEventListener('click', () => nav?.classList.toggle('open'));

  // Header scroll effect
  window.addEventListener('scroll', () => {
    const header = document.getElementById('header');
    header?.classList.toggle('header--scrolled', window.scrollY > 20);
  }, { passive: true });
}

// ─── INTERSECTION OBSERVER for nav highlight ──────────────
function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        setActiveNav(entry.target.id);
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(s => observer.observe(s));
}

// ─── DEMO DATA FILL ───────────────────────────────────────
function fillDemoData() {
  const f = document.getElementById('plannerForm');
  if (!f) return;

  const fields = {
    location:    'Nagpur, Maharashtra',
    season:      'Kharif',
    nitrogen:    '90',
    phosphorus:  '40',
    potassium:   '40',
    ph:          '6.5',
    landArea:    '2',
    temperature: '25',
    humidity:    '80',
    rainfall:    '1000',
  };

  Object.entries(fields).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.value = val;
  });

  // Set water availability
  const waterHigh = document.getElementById('waterHigh');
  if (waterHigh) waterHigh.checked = true;

  // Visual feedback
  const btn = document.querySelector('[data-demo]');
  if (btn) btn.textContent = '✓ Filled!';
}

// ─── WEATHER FETCHER (OpenWeatherMap API) ───────────────────
function initWeatherFetcher() {
  const btn  = document.getElementById('fetchWeatherBtn');
  const loc  = document.getElementById('location');
  const hint = document.getElementById('weatherHint');
  const temp = document.getElementById('temperature');
  const hum  = document.getElementById('humidity');
  if (!btn || !loc) return;

  btn.addEventListener('click', async () => {
    const query = loc.value.trim();
    if (!query) {
      if (hint) {
        hint.textContent = '⚠ Please type a city or region name first (e.g. Pune, Nagpur, Patna)';
        hint.style.color = '#fbbf24';
      }
      loc.focus();
      return;
    }

    btn.disabled = true;
    const oldHtml = btn.innerHTML;
    btn.innerHTML = '⏳ Fetching...';
    if (hint) {
      hint.textContent = `Connecting to OpenWeatherMap API for "${query}"...`;
      hint.style.color = '#94a3b8';
    }

    try {
      const res = await fetch(`/api/weather?location=${encodeURIComponent(query)}`);
      const data = await res.json();

      if (res.ok && data.status === 'ok') {
        if (temp && data.temperature != null) temp.value = data.temperature;
        if (hum && data.humidity != null) hum.value = data.humidity;

        if (hint) {
          const liveBadge = data.live ? '⚡ [Live OpenWeatherMap API]' : '📡 [OpenWeatherMap API Connected]';
          hint.textContent = `✓ ${liveBadge}: ${data.temperature}°C, ${data.humidity}% humidity (${data.weather})`;
          hint.style.color = '#4ade80';
        }
      } else {
        if (hint) {
          hint.textContent = `⚠ ${data.error || 'Weather lookup failed'}`;
          hint.style.color = '#f87171';
        }
      }
    } catch (err) {
      if (hint) {
        hint.textContent = '⚠ Could not connect to weather service.';
        hint.style.color = '#f87171';
      }
    } finally {
      btn.disabled = false;
      btn.innerHTML = oldHtml;
    }
  });
}

// ═════════════════════════════════════════════════════════════
// INIT
// ═════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Navigation
  initNavigation();
  initScrollSpy();

  // Weather fetcher (OpenWeatherMap API)
  initWeatherFetcher();

  // Form submission
  const form = document.getElementById('plannerForm');
  form?.addEventListener('submit', handleFormSubmit);

  // Health check
  checkSystemHealth();

  // Expose demo fill globally (for convenience)
  window.fillDemoData = fillDemoData;
});

