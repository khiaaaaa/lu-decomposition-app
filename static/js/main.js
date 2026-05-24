/* =========================================================
   LU Decomposition Calculator — Frontend Logic
========================================================== */

const sizeSelect = document.getElementById('size-select');
const pivotCheck = document.getElementById('pivot-check');
const matrixGrid = document.getElementById('matrix-grid');
const vectorGrid = document.getElementById('vector-grid');
const solveBtn   = document.getElementById('solve-btn');
const clearBtn   = document.getElementById('clear-btn');
const exampleBtn = document.getElementById('example-btn');
const errorBox   = document.getElementById('error-box');
const resultsBox = document.getElementById('results');
const resultEl   = document.getElementById('result-content');

/* ---------- Build input grids ---------- */
function buildGrids(n) {
  matrixGrid.style.gridTemplateColumns = `repeat(${n}, max-content)`;
  matrixGrid.innerHTML = '';
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const inp = document.createElement('input');
      inp.type = 'text';
      inp.inputMode = 'decimal';
      inp.dataset.row = i;
      inp.dataset.col = j;
      inp.placeholder = '0';
      inp.setAttribute('aria-label', `A row ${i + 1} col ${j + 1}`);
      matrixGrid.appendChild(inp);
    }
  }
  vectorGrid.style.gridTemplateColumns = `max-content`;
  vectorGrid.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const inp = document.createElement('input');
    inp.type = 'text';
    inp.inputMode = 'decimal';
    inp.dataset.idx = i;
    inp.placeholder = '0';
    inp.setAttribute('aria-label', `b row ${i + 1}`);
    vectorGrid.appendChild(inp);
  }
}

/* ---------- Collect values ---------- */
function readMatrix(n) {
  const rows = [];
  for (let i = 0; i < n; i++) {
    const row = [];
    for (let j = 0; j < n; j++) {
      const inp = matrixGrid.querySelector(
        `input[data-row="${i}"][data-col="${j}"]`
      );
      row.push(inp.value.trim());
    }
    rows.push(row.join(' '));
  }
  return rows.join('\n');
}

function readVector(n) {
  const vals = [];
  for (let i = 0; i < n; i++) {
    const inp = vectorGrid.querySelector(`input[data-idx="${i}"]`);
    vals.push(inp.value.trim());
  }
  return vals.join(' ');
}

/* ---------- Examples per size ---------- */
const EXAMPLES = {
  2: { A: [[4, 3], [6, 3]], b: [10, 12] },
  3: { A: [[2, -1, -2], [-4, 6, 3], [-4, -2, 8]], b: [-1, 9, -2] },
  4: {
    A: [[1, 1, 0, 3], [2, 1, -1, 1], [3, -1, -1, 2], [-1, 2, 3, -1]],
    b: [4, 1, -3, 4],
  },
  5: {
    A: [
      [4, -1, 0, 0, 1],
      [-1, 4, -1, 0, 0],
      [0, -1, 4, -1, 0],
      [0, 0, -1, 4, -1],
      [1, 0, 0, -1, 4],
    ],
    b: [12, 0, 0, 0, 12],
  },
  6: {
    A: [
      [10, -1, 2, 0, 0, 0],
      [-1, 11, -1, 3, 0, 0],
      [2, -1, 10, -1, 0, 0],
      [0, 3, -1, 8, -1, 0],
      [0, 0, 0, -1, 7, -1],
      [0, 0, 0, 0, -1, 5],
    ],
    b: [6, 25, -11, 15, 8, 10],
  },
};

function loadExample() {
  const n = +sizeSelect.value;
  const ex = EXAMPLES[n];
  if (!ex) return;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const inp = matrixGrid.querySelector(
        `input[data-row="${i}"][data-col="${j}"]`
      );
      inp.value = ex.A[i][j];
    }
    const v = vectorGrid.querySelector(`input[data-idx="${i}"]`);
    v.value = ex.b[i];
  }
}

function clearAll() {
  matrixGrid.querySelectorAll('input').forEach(i => (i.value = ''));
  vectorGrid.querySelectorAll('input').forEach(i => (i.value = ''));
  errorBox.hidden = true;
  resultsBox.hidden = true;
}

/* ---------- Error display ---------- */
function showError(msg) {
  errorBox.textContent = msg;
  errorBox.hidden = false;
  resultsBox.hidden = true;
}
function clearError() {
  errorBox.hidden = true;
  errorBox.textContent = '';
}

/* ---------- Render results ---------- */
function renderResults(data) {
  const tex = data.latex;
  const parts = [];

  // 1. Original system
  parts.push(`
    <div class="result-block">
      <div class="result-block__head">Input system</div>
      <div class="result-block__matrices">
        \\( A = ${tex.A} \\)
        \\( \\mathbf{b} = ${tex.b} \\)
      </div>
    </div>
  `);

  // 2. (Optional) Pivot info
  if (data.mode === 'pivot') {
    const swapText = data.swaps.length
      ? data.swaps.map(s => `R${s[0]} ↔ R${s[1]}`).join(', ')
      : 'no swaps required';
    parts.push(`
      <div class="result-block">
        <div class="result-block__head">Partial pivoting · PA = LU</div>
        <div class="result-block__matrices">
          \\( P = ${tex.P} \\)
          \\( P\\mathbf{b} = ${tex.Pb} \\)
        </div>
        <p class="swap-list">Row swaps: ${swapText}</p>
      </div>
    `);
  }

  // 3. Factorization
  parts.push(`
    <div class="result-block">
      <div class="result-block__head">LU factorization</div>
      <div class="result-block__matrices">
        \\( L = ${tex.L} \\)
        \\( U = ${tex.U} \\)
      </div>
      <p class="swap-list">Check: \\( LU = ${tex.LU} \\)</p>
    </div>
  `);

  // 4. Decomposition steps (only for Doolittle mode)
  if (data.decomposition_steps && data.decomposition_steps.length) {
    const stepsHtml = data.decomposition_steps
      .map(s => `<div class="step">\\( ${s.latex} \\)</div>`)
      .join('');
    parts.push(`
      <div class="result-block">
        <div class="result-block__head">Decomposition · step by step</div>
        <div class="result-block__steps">${stepsHtml}</div>
      </div>
    `);
  }

  // 5. Forward substitution
  const fwdHtml = data.forward_steps
    .map(s => `<div class="step">\\( ${s.latex} \\)</div>`)
    .join('');
  parts.push(`
    <div class="result-block">
      <div class="result-block__head">Forward substitution · solve L y = ${data.mode === 'pivot' ? 'Pb' : 'b'}</div>
      <div class="result-block__steps">${fwdHtml}</div>
      <p class="swap-list" style="margin-top: 0.75rem;">\\( \\mathbf{y} = ${tex.y} \\)</p>
    </div>
  `);

  // 6. Backward substitution
  const bwdHtml = data.backward_steps
    .map(s => `<div class="step">\\( ${s.latex} \\)</div>`)
    .join('');
  parts.push(`
    <div class="result-block">
      <div class="result-block__head">Backward substitution · solve U x = y</div>
      <div class="result-block__steps">${bwdHtml}</div>
    </div>
  `);

  // 7. Final solution
  parts.push(`
    <div class="result-block">
      <div class="result-block__head">Solution</div>
      <div class="result-block__solution">
        <strong>x =</strong> \\( ${tex.x} \\)
      </div>
    </div>
  `);

  resultEl.innerHTML = parts.join('');
  resultsBox.hidden = false;

  // Trigger MathJax re-typesetting
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise([resultEl]).catch(err =>
      console.error('MathJax error:', err)
    );
  }
}

/* ---------- Solve handler ---------- */
async function solve() {
  clearError();
  const n = +sizeSelect.value;
  const payload = {
    matrix: readMatrix(n),
    vector: readVector(n),
    pivot: pivotCheck.checked,
  };

  solveBtn.disabled = true;
  solveBtn.textContent = 'Solving…';

  try {
    const resp = await fetch('/api/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!data.ok) {
      showError(data.error || 'Could not solve the system.');
    } else {
      renderResults(data);
      resultsBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } catch (err) {
    showError('Network error: ' + err.message);
  } finally {
    solveBtn.disabled = false;
    solveBtn.textContent = 'Solve →';
  }
}

/* ---------- Event wiring ---------- */
sizeSelect.addEventListener('change', () => {
  buildGrids(+sizeSelect.value);
  clearError();
  resultsBox.hidden = true;
});
solveBtn.addEventListener('click', solve);
clearBtn.addEventListener('click', clearAll);
exampleBtn.addEventListener('click', loadExample);

/* ---------- Init ---------- */
buildGrids(+sizeSelect.value);
loadExample();   // start with example pre-filled so users see something useful
