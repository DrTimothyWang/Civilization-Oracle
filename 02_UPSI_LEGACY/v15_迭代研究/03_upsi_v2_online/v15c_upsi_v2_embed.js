/**
 * UPSI_v2 Interactive Visualization Engine
 * ==========================================
 * Vanilla JS module for embedding UPSI_v2 visualizations in dashboards.
 * No external dependencies. Responsive. Self-contained.
 *
 * Version: v15c
 * Date: 2026-06-04
 */

(function (global) {
  'use strict';

  // ---------------------------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------------------------

  const QUADRANT_CONFIG = {
    'Stable':              { color: '#28a745', bg: '#d4edda', label: '🟢 Stable',              emoji: '🟢' },
    'Gradual Decline':     { color: '#ffc107', bg: '#fff3cd', label: '🟡 Gradual Decline',     emoji: '🟡' },
    'Sudden Crisis':       { color: '#fd7e14', bg: '#ffe5cc', label: '🟠 Sudden Crisis',       emoji: '🟠' },
    'Accelerating Collapse':{ color: '#dc3545', bg: '#f8d7da', label: '🔴 Accelerating Collapse', emoji: '🔴' },
  };

  const DEFAULTS = {
    pointBaseSize: 6,
    pointMaxSize: 18,
    fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    padding: 40,
  };

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function getQuadrantConfig(q) {
    return QUADRANT_CONFIG[q] || { color: '#888', bg: '#eee', label: q, emoji: '⚪' };
  }

  function createCanvas(containerId, width, height) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error('UPSI_v2: container not found:', containerId);
      return null;
    }
    container.innerHTML = '';
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    canvas.style.width = '100%';
    canvas.style.height = 'auto';
    canvas.style.display = 'block';
    container.appendChild(canvas);
    return canvas;
  }

  function setupHiDPICanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx, width: rect.width, height: rect.height };
  }

  function mapRange(value, inMin, inMax, outMin, outMax) {
    if (inMax === inMin) return outMin;
    return outMin + (value - inMin) * (outMax - outMin) / (inMax - inMin);
  }

  function formatDate(dateStr) {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  }

  function daysBetween(a, b) {
    const da = new Date(a), db = new Date(b);
    return Math.round((db - da) / (1000 * 60 * 60 * 24));
  }

  // ---------------------------------------------------------------------------
  // 1. Phase Portrait (Canvas-based)
  // ---------------------------------------------------------------------------

  function renderPhasePortrait(data, containerId, options) {
    options = options || {};
    const assetName = options.assetName || data.asset || 'Asset';
    const records = data.data || data;
    if (!records || records.length === 0) {
      document.getElementById(containerId).innerHTML = '<p style="padding:20px;text-align:center;color:#888">No data available</p>';
      return;
    }

    const container = document.getElementById(containerId);
    container.innerHTML = '';
    container.style.position = 'relative';
    container.style.width = '100%';
    container.style.minHeight = '400px';

    const canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.display = 'block';
    container.appendChild(canvas);

    // Tooltip element
    const tooltip = document.createElement('div');
    tooltip.style.position = 'absolute';
    tooltip.style.background = 'rgba(0,0,0,0.85)';
    tooltip.style.color = '#fff';
    tooltip.style.padding = '8px 12px';
    tooltip.style.borderRadius = '6px';
    tooltip.style.fontSize = '12px';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.display = 'none';
    tooltip.style.zIndex = '100';
    tooltip.style.maxWidth = '220px';
    tooltip.style.lineHeight = '1.5';
    container.appendChild(tooltip);

    // Slider container
    const sliderWrap = document.createElement('div');
    sliderWrap.style.padding = '10px 15px';
    sliderWrap.style.display = 'flex';
    sliderWrap.style.alignItems = 'center';
    sliderWrap.style.gap = '10px';
    sliderWrap.style.background = '#f8f9fa';
    sliderWrap.style.borderTop = '1px solid #dee2e6';

    const sliderLabel = document.createElement('label');
    sliderLabel.textContent = 'Time:';
    sliderLabel.style.fontSize = '12px';
    sliderLabel.style.color = '#495057';
    sliderLabel.style.fontWeight = '600';
    sliderLabel.style.whiteSpace = 'nowrap';

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.min = 1;
    slider.max = records.length;
    slider.value = records.length;
    slider.style.flex = '1';
    slider.style.cursor = 'pointer';

    const dateLabel = document.createElement('span');
    dateLabel.style.fontSize = '12px';
    dateLabel.style.color = '#495057';
    dateLabel.style.minWidth = '100px';
    dateLabel.style.textAlign = 'right';
    dateLabel.textContent = formatDate(records[records.length - 1].date);

    sliderWrap.appendChild(sliderLabel);
    sliderWrap.appendChild(slider);
    sliderWrap.appendChild(dateLabel);
    container.appendChild(sliderWrap);

    // Play button
    const playBtn = document.createElement('button');
    playBtn.textContent = '▶ Play';
    playBtn.style.marginLeft = '10px';
    playBtn.style.fontSize = '12px';
    playBtn.style.padding = '2px 8px';
    playBtn.style.cursor = 'pointer';
    playBtn.style.border = '1px solid #ced4da';
    playBtn.style.borderRadius = '4px';
    playBtn.style.background = '#fff';
    sliderWrap.appendChild(playBtn);

    let playing = false;
    let playInterval = null;

    function stopPlay() {
      playing = false;
      playBtn.textContent = '▶ Play';
      if (playInterval) { clearInterval(playInterval); playInterval = null; }
    }

    playBtn.addEventListener('click', () => {
      if (playing) { stopPlay(); return; }
      playing = true;
      playBtn.textContent = '⏸ Pause';
      slider.value = 1;
      playInterval = setInterval(() => {
        let v = parseInt(slider.value, 10);
        if (v >= records.length) { stopPlay(); return; }
        slider.value = v + 1;
        slider.dispatchEvent(new Event('input'));
      }, 300);
    });

    // Drawing
    let hoveredPoint = null;

    function draw() {
      const rect = container.getBoundingClientRect();
      const pad = DEFAULTS.padding;
      const chartW = Math.max(300, rect.width);
      const chartH = Math.max(300, rect.height - 60);
      canvas.width = chartW;
      canvas.height = chartH;

      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, chartW, chartH);

      const maxPoints = parseInt(slider.value, 10);
      const visible = records.slice(0, maxPoints);

      // Compute bounds
      const allPsi = records.map(r => r.psi);
      const allSpi = records.map(r => r.spi);
      let psiMin = Math.min(...allPsi) * 0.95;
      let psiMax = Math.max(...allPsi) * 1.05;
      let spiMin = Math.min(...allSpi) * 0.95;
      let spiMax = Math.max(...allSpi) * 1.05;
      if (data.thresholds) {
        psiMin = Math.min(psiMin, data.thresholds.psi_high * 0.9);
        psiMax = Math.max(psiMax, data.thresholds.psi_high * 1.1);
        spiMin = Math.min(spiMin, data.thresholds.spi_high * 0.9);
        spiMax = Math.max(spiMax, data.thresholds.spi_high * 1.1);
      }
      const x0 = pad, x1 = chartW - pad;
      const y0 = chartH - pad, y1 = pad;

      // Background quadrants
      const psiHigh = data.thresholds ? data.thresholds.psi_high : (psiMin + psiMax) / 2;
      const spiHigh = data.thresholds ? data.thresholds.spi_high : (spiMin + spiMax) / 2;
      const xMid = mapRange(psiHigh, psiMin, psiMax, x0, x1);
      const yMid = mapRange(spiHigh, spiMin, spiMax, y0, y1);

      ctx.fillStyle = getQuadrantConfig('Stable').bg;
      ctx.fillRect(x0, yMid, xMid - x0, y0 - yMid);
      ctx.fillStyle = getQuadrantConfig('Gradual Decline').bg;
      ctx.fillRect(xMid, yMid, x1 - xMid, y0 - yMid);
      ctx.fillStyle = getQuadrantConfig('Sudden Crisis').bg;
      ctx.fillRect(x0, y1, xMid - x0, yMid - y1);
      ctx.fillStyle = getQuadrantConfig('Accelerating Collapse').bg;
      ctx.fillRect(xMid, y1, x1 - xMid, yMid - y1);

      // Grid lines
      ctx.strokeStyle = '#e9ecef';
      ctx.lineWidth = 1;
      for (let i = 1; i < 5; i++) {
        const gx = x0 + (x1 - x0) * i / 5;
        const gy = y1 + (y0 - y1) * i / 5;
        ctx.beginPath(); ctx.moveTo(gx, y1); ctx.lineTo(gx, y0); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x0, gy); ctx.lineTo(x1, gy); ctx.stroke();
      }

      // Threshold lines
      ctx.strokeStyle = '#6c757d';
      ctx.setLineDash([5, 5]);
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(xMid, y1); ctx.lineTo(xMid, y0); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x0, yMid); ctx.lineTo(x1, yMid); ctx.stroke();
      ctx.setLineDash([]);

      // Threshold labels
      ctx.fillStyle = '#6c757d';
      ctx.font = '10px ' + DEFAULTS.fontFamily;
      ctx.fillText(`PSIₕ=${psiHigh.toFixed(2)}`, xMid + 4, y0 - 4);
      ctx.fillText(`SPIₕ=${spiHigh.toFixed(2)}`, x0 + 4, yMid - 4);

      // Trajectory line
      if (visible.length > 1) {
        ctx.strokeStyle = 'rgba(0,0,0,0.15)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        visible.forEach((pt, i) => {
          const px = mapRange(pt.psi, psiMin, psiMax, x0, x1);
          const py = mapRange(pt.spi, spiMin, spiMax, y0, y1);
          if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        });
        ctx.stroke();
      }

      // Points
      const nTotal = records.length;
      visible.forEach((pt, i) => {
        const px = mapRange(pt.psi, psiMin, psiMax, x0, x1);
        const py = mapRange(pt.spi, spiMin, spiMax, y0, y1);
        const size = DEFAULTS.pointBaseSize + (i / (nTotal - 1)) * (DEFAULTS.pointMaxSize - DEFAULTS.pointBaseSize);
        const cfg = getQuadrantConfig(pt.quadrant);

        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fillStyle = cfg.color;
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Highlight hovered
        if (hoveredPoint && hoveredPoint.idx === i) {
          ctx.beginPath();
          ctx.arc(px, py, size + 4, 0, Math.PI * 2);
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      });

      // Start / End annotations
      if (visible.length > 0) {
        const first = visible[0];
        const last = visible[visible.length - 1];
        const fx = mapRange(first.psi, psiMin, psiMax, x0, x1);
        const fy = mapRange(first.spi, spiMin, spiMax, y0, y1);
        const lx = mapRange(last.psi, psiMin, psiMax, x0, x1);
        const ly = mapRange(last.spi, spiMin, spiMax, y0, y1);

        ctx.fillStyle = '#198754';
        ctx.font = 'bold 11px ' + DEFAULTS.fontFamily;
        ctx.fillText('▶ Start', fx + 8, fy - 8);
        ctx.fillStyle = '#dc3545';
        ctx.fillText('■ End', lx + 8, ly - 8);
      }

      // Axes
      ctx.strokeStyle = '#343a40';
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y0); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0, y1); ctx.stroke();

      // Axis labels
      ctx.fillStyle = '#343a40';
      ctx.font = '12px ' + DEFAULTS.fontFamily;
      ctx.textAlign = 'center';
      ctx.fillText('PSI (Level)', (x0 + x1) / 2, chartH - 10);
      ctx.save();
      ctx.translate(14, (y0 + y1) / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText('SPI (Velocity)', 0, 0);
      ctx.restore();

      // Ticks
      ctx.font = '10px ' + DEFAULTS.fontFamily;
      ctx.textAlign = 'center';
      for (let i = 0; i <= 4; i++) {
        const t = i / 4;
        const valX = psiMin + t * (psiMax - psiMin);
        const tx = x0 + t * (x1 - x0);
        ctx.fillText(valX.toFixed(2), tx, y0 + 14);
        const valY = spiMin + t * (spiMax - spiMin);
        const ty = y0 - t * (y0 - y1);
        ctx.textAlign = 'right';
        ctx.fillText(valY.toFixed(2), x0 - 6, ty + 3);
        ctx.textAlign = 'center';
      }

      // Title
      ctx.fillStyle = '#212529';
      ctx.font = 'bold 14px ' + DEFAULTS.fontFamily;
      ctx.textAlign = 'center';
      ctx.fillText(`Phase Portrait — ${assetName}`, (x0 + x1) / 2, 20);
    }

    // Hover interaction
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const pad = DEFAULTS.padding;
      const chartW = canvas.width;
      const chartH = canvas.height;
      const x0 = pad, x1 = chartW - pad;
      const y0 = chartH - pad, y1 = pad;

      const allPsi = records.map(r => r.psi);
      const allSpi = records.map(r => r.spi);
      let psiMin = Math.min(...allPsi) * 0.95;
      let psiMax = Math.max(...allPsi) * 1.05;
      let spiMin = Math.min(...allSpi) * 0.95;
      let spiMax = Math.max(...allSpi) * 1.05;
      if (data.thresholds) {
        psiMin = Math.min(psiMin, data.thresholds.psi_high * 0.9);
        psiMax = Math.max(psiMax, data.thresholds.psi_high * 1.1);
        spiMin = Math.min(spiMin, data.thresholds.spi_high * 0.9);
        spiMax = Math.max(spiMax, data.thresholds.spi_high * 1.1);
      }

      const maxPoints = parseInt(slider.value, 10);
      const visible = records.slice(0, maxPoints);
      let found = null;
      visible.forEach((pt, i) => {
        const px = mapRange(pt.psi, psiMin, psiMax, x0, x1);
        const py = mapRange(pt.spi, spiMin, spiMax, y0, y1);
        const size = DEFAULTS.pointBaseSize + (i / (records.length - 1)) * (DEFAULTS.pointMaxSize - DEFAULTS.pointBaseSize);
        const dx = mx - px, dy = my - py;
        if (dx * dx + dy * dy < (size + 6) * (size + 6)) {
          found = { pt, idx: i, px, py };
        }
      });

      hoveredPoint = found;
      draw();

      if (found) {
        const cfg = getQuadrantConfig(found.pt.quadrant);
        tooltip.innerHTML = `
          <strong>${formatDate(found.pt.date)}</strong><br>
          Asset: ${assetName}<br>
          PSI: ${found.pt.psi.toFixed(3)}<br>
          SPI: ${found.pt.spi.toFixed(3)}<br>
          <span style="color:${cfg.color}">${cfg.emoji} ${found.pt.quadrant}</span>
        `;
        tooltip.style.display = 'block';
        tooltip.style.left = (found.px + 12) + 'px';
        tooltip.style.top = (found.py - 12) + 'px';
      } else {
        tooltip.style.display = 'none';
      }
    });

    canvas.addEventListener('mouseleave', () => {
      hoveredPoint = null;
      tooltip.style.display = 'none';
      draw();
    });

    slider.addEventListener('input', () => {
      const idx = parseInt(slider.value, 10) - 1;
      dateLabel.textContent = formatDate(records[Math.min(idx, records.length - 1)].date);
      draw();
    });

    window.addEventListener('resize', draw);
    draw();
  }

  // ---------------------------------------------------------------------------
  // 2. Quadrant Timeline
  // ---------------------------------------------------------------------------

  function renderTimeline(data, containerId, options) {
    options = options || {};
    const records = data.data || data;
    if (!records || records.length === 0) {
      document.getElementById(containerId).innerHTML = '<p style="padding:20px;text-align:center;color:#888">No data available</p>';
      return;
    }

    const container = document.getElementById(containerId);
    container.innerHTML = '';

    // Group contiguous same-quadrant segments
    const segments = [];
    let current = { quadrant: records[0].quadrant, start: 0, end: 0, startDate: records[0].date, endDate: records[0].date };
    for (let i = 1; i < records.length; i++) {
      if (records[i].quadrant === current.quadrant) {
        current.end = i;
        current.endDate = records[i].date;
      } else {
        segments.push(current);
        current = { quadrant: records[i].quadrant, start: i, end: i, startDate: records[i].date, endDate: records[i].date };
      }
    }
    segments.push(current);

    const totalDays = records.length;

    const wrapper = document.createElement('div');
    wrapper.style.padding = '15px';
    wrapper.style.background = '#fff';
    wrapper.style.borderRadius = '8px';
    wrapper.style.border = '1px solid #dee2e6';

    const title = document.createElement('div');
    title.textContent = options.title || 'Quadrant Timeline';
    title.style.fontWeight = 'bold';
    title.style.fontSize = '14px';
    title.style.marginBottom = '12px';
    title.style.color = '#212529';
    wrapper.appendChild(title);

    const bar = document.createElement('div');
    bar.style.display = 'flex';
    bar.style.height = '36px';
    bar.style.borderRadius = '6px';
    bar.style.overflow = 'hidden';
    bar.style.cursor = 'pointer';
    bar.style.border = '1px solid #dee2e6';

    segments.forEach(seg => {
      const duration = seg.end - seg.start + 1;
      const pct = (duration / totalDays) * 100;
      const cfg = getQuadrantConfig(seg.quadrant);
      const cell = document.createElement('div');
      cell.style.flex = `0 0 ${pct}%`;
      cell.style.background = cfg.color;
      cell.style.display = 'flex';
      cell.style.alignItems = 'center';
      cell.style.justifyContent = 'center';
      cell.style.color = '#fff';
      cell.style.fontSize = '11px';
      cell.style.fontWeight = '600';
      cell.style.textShadow = '0 1px 2px rgba(0,0,0,0.4)';
      cell.style.transition = 'transform 0.15s';
      cell.title = `${cfg.emoji} ${seg.quadrant}\n${formatDate(seg.startDate)} – ${formatDate(seg.endDate)} (${duration} days)`;
      if (pct > 8) cell.textContent = cfg.emoji;

      cell.addEventListener('mouseenter', () => { cell.style.transform = 'scaleY(1.15)'; cell.style.zIndex = '10'; });
      cell.addEventListener('mouseleave', () => { cell.style.transform = 'scaleY(1)'; cell.style.zIndex = '1'; });
      cell.addEventListener('click', () => {
        // Zoom: highlight this segment
        document.querySelectorAll('.upsi-timeline-seg-active').forEach(el => el.classList.remove('upsi-timeline-seg-active'));
        cell.style.boxShadow = 'inset 0 0 0 3px #000';
        setTimeout(() => { cell.style.boxShadow = 'none'; }, 1500);
      });

      bar.appendChild(cell);
    });

    wrapper.appendChild(bar);

    // Legend row
    const legend = document.createElement('div');
    legend.style.display = 'flex';
    legend.style.flexWrap = 'wrap';
    legend.style.gap = '12px';
    legend.style.marginTop = '12px';
    Object.keys(QUADRANT_CONFIG).forEach(q => {
      const cfg = QUADRANT_CONFIG[q];
      const item = document.createElement('div');
      item.style.display = 'flex';
      item.style.alignItems = 'center';
      item.style.gap = '4px';
      item.style.fontSize = '11px';
      item.style.color = '#495057';
      item.innerHTML = `<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:${cfg.color}"></span> ${cfg.label}`;
      legend.appendChild(item);
    });
    wrapper.appendChild(legend);

    container.appendChild(wrapper);
  }

  // ---------------------------------------------------------------------------
  // 3. Alert Table
  // ---------------------------------------------------------------------------

  function renderAlertTable(data, containerId, options) {
    options = options || {};
    const alerts = data.alerts || data;
    if (!alerts || alerts.length === 0) {
      document.getElementById(containerId).innerHTML = '<p style="padding:20px;text-align:center;color:#888">No alerts recorded</p>';
      return;
    }

    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.style.background = '#fff';
    wrapper.style.borderRadius = '8px';
    wrapper.style.border = '1px solid #dee2e6';
    wrapper.style.overflow = 'auto';

    const title = document.createElement('div');
    title.textContent = options.title || 'Alert History';
    title.style.fontWeight = 'bold';
    title.style.fontSize = '14px';
    title.style.padding = '12px 15px';
    title.style.borderBottom = '1px solid #dee2e6';
    title.style.color = '#212529';
    wrapper.appendChild(title);

    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.fontSize = '13px';

    const thead = document.createElement('thead');
    thead.style.background = '#f8f9fa';
    const headers = ['Date/Time', 'Asset', 'From', 'To', 'Alert Level', 'Duration'];
    const sortState = { col: null, asc: true };

    function renderRows(rows) {
      const tbody = table.querySelector('tbody') || document.createElement('tbody');
      tbody.innerHTML = '';
      rows.forEach(a => {
        const fromCfg = getQuadrantConfig(a.from);
        const toCfg = getQuadrantConfig(a.to);
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #f1f3f5';
        tr.innerHTML = `
          <td style="padding:10px 12px;white-space:nowrap">${formatDate(a.date)}</td>
          <td style="padding:10px 12px;font-weight:600">${a.asset}</td>
          <td style="padding:10px 12px"><span style="color:${fromCfg.color}">${fromCfg.emoji} ${a.from}</span></td>
          <td style="padding:10px 12px"><span style="color:${toCfg.color}">${toCfg.emoji} ${a.to}</span></td>
          <td style="padding:10px 12px">${a.level}</td>
          <td style="padding:10px 12px;text-align:center">${a.duration}d</td>
        `;
        tbody.appendChild(tr);
      });
      if (!table.querySelector('tbody')) table.appendChild(tbody);
    }

    const headerRow = document.createElement('tr');
    headers.forEach((h, idx) => {
      const th = document.createElement('th');
      th.textContent = h;
      th.style.padding = '10px 12px';
      th.style.textAlign = idx === 5 ? 'center' : 'left';
      th.style.fontWeight = '600';
      th.style.color = '#495057';
      th.style.fontSize = '12px';
      th.style.textTransform = 'uppercase';
      th.style.letterSpacing = '0.3px';
      th.style.cursor = 'pointer';
      th.style.userSelect = 'none';
      th.addEventListener('click', () => {
        const keyMap = ['date', 'asset', 'from', 'to', 'level', 'duration'];
        const key = keyMap[idx];
        if (sortState.col === key) sortState.asc = !sortState.asc;
        else { sortState.col = key; sortState.asc = true; }
        const sorted = [...alerts].sort((a, b) => {
          let av = a[key], bv = b[key];
          if (typeof av === 'string') av = av.toLowerCase();
          if (typeof bv === 'string') bv = bv.toLowerCase();
          if (av < bv) return sortState.asc ? -1 : 1;
          if (av > bv) return sortState.asc ? 1 : -1;
          return 0;
        });
        renderRows(sorted);
      });
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    wrapper.appendChild(table);

    renderRows(alerts);
    container.appendChild(wrapper);
  }

  // ---------------------------------------------------------------------------
  // 4. Asset Grid
  // ---------------------------------------------------------------------------

  function renderAssetGrid(data, containerId, options) {
    options = options || {};
    const assets = data.assets || data;
    if (!assets || assets.length === 0) {
      document.getElementById(containerId).innerHTML = '<p style="padding:20px;text-align:center;color:#888">No assets available</p>';
      return;
    }

    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const grid = document.createElement('div');
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(220px, 1fr))';
    grid.style.gap = '16px';

    assets.forEach(asset => {
      const cur = asset.current || (asset.data ? asset.data[asset.data.length - 1] : {});
      const cfg = getQuadrantConfig(cur.quadrant || 'Stable');

      const card = document.createElement('div');
      card.style.background = '#fff';
      card.style.borderRadius = '10px';
      card.style.border = `3px solid ${cfg.color}`;
      card.style.padding = '16px';
      card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
      card.style.transition = 'transform 0.15s, box-shadow 0.15s';
      card.style.cursor = 'pointer';

      card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-3px)';
        card.style.boxShadow = '0 6px 16px rgba(0,0,0,0.1)';
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
      });

      const daysSince = cur.days_since_alert !== undefined ? cur.days_since_alert : (cur.last_alert_date ? daysBetween(cur.last_alert_date, new Date().toISOString().slice(0, 10)) : '-');

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <span style="font-weight:bold;font-size:15px;color:#212529">${asset.name}</span>
          <span style="font-size:20px">${cfg.emoji}</span>
        </div>
        <div style="font-size:12px;color:#fff;background:${cfg.color};display:inline-block;padding:3px 10px;border-radius:12px;margin-bottom:12px;font-weight:600">
          ${cur.quadrant || 'Stable'}
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px;color:#495057">
          <div>
            <div style="font-size:11px;color:#868e96;text-transform:uppercase;letter-spacing:0.5px">PSI</div>
            <div style="font-weight:600;font-size:16px;color:#212529">${(cur.psi !== undefined ? cur.psi : '-').toFixed ? cur.psi.toFixed(3) : cur.psi}</div>
          </div>
          <div>
            <div style="font-size:11px;color:#868e96;text-transform:uppercase;letter-spacing:0.5px">SPI</div>
            <div style="font-weight:600;font-size:16px;color:#212529">${(cur.spi !== undefined ? cur.spi : '-').toFixed ? cur.spi.toFixed(3) : cur.spi}</div>
          </div>
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px solid #f1f3f5;font-size:11px;color:#868e96;display:flex;justify-content:space-between">
          <span>Last alert: ${cur.last_alert_date ? formatDate(cur.last_alert_date) : 'None'}</span>
          <span>${daysSince !== '-' ? daysSince + 'd ago' : 'No alerts'}</span>
        </div>
      `;

      grid.appendChild(card);
    });

    container.appendChild(grid);
  }

  // ---------------------------------------------------------------------------
  // Export
  // ---------------------------------------------------------------------------

  const UPSIv2Viz = {
    renderPhasePortrait,
    renderTimeline,
    renderAlertTable,
    renderAssetGrid,
    QUADRANT_CONFIG,
    _helpers: { getQuadrantConfig, formatDate, daysBetween }
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = UPSIv2Viz;
  }
  global.UPSIv2Viz = UPSIv2Viz;

})(typeof window !== 'undefined' ? window : this);
