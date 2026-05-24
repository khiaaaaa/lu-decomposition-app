# LU Decomposition (Doolittle Method) — PIT Finals 2026

A Flask web application implementing the **Doolittle LU decomposition**
method for solving systems of linear equations $A\mathbf{x} = \mathbf{b}$.

This is **Topic #8** from the PIT Finals 2026 Numerical Methods project.

## Features

- **Theory section** — full mathematical discussion of the Doolittle method,
  with formulas for constructing $L$ and $U$, forward/backward substitution,
  and a discussion of partial pivoting.
- **Two fully worked examples** — a 3×3 and a 4×4 system, both with every
  intermediate step shown.
- **Interactive calculator** — supports 2×2 through 6×6 systems, with an
  optional **partial pivoting** mode ($PA = LU$). Returns a complete
  step-by-step trace of every entry computed.
- **Safe input parsing** — all user input goes through a whitelist-based
  parser that rejects anything except numeric characters and separators.
  `eval()` is never used.
- **Manual implementation** — the core algorithm is written from scratch
  in pure Python (NumPy is **not** used for the decomposition itself).

## Project structure

```
lu-decomp-app/
├── app.py              # Flask application; routes + safe input parsing
├── lu_solver.py        # Core numerical algorithm (Doolittle + pivoting)
├── requirements.txt    # Flask dependency
├── vercel.json         # Vercel deployment config
├── templates/
│   └── index.html      # Main page (theory, examples, calculator)
└── static/
    ├── css/style.css   # Editorial / academic styling
    └── js/main.js      # Calculator UI logic
```

## Running locally

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

## Deploying to Vercel

```bash
npm install -g vercel
vercel
```

The included `vercel.json` routes all requests through `app.py` and serves
static files from `/static`.

## Algorithm overview

For an $n \times n$ matrix $A$, the Doolittle factors $A = LU$ are
constructed row-by-row using:

$$
u_{kj} = a_{kj} - \sum_{p=1}^{k-1} \ell_{kp} u_{pj}
\qquad\text{for } j=k,\ldots,n
$$

$$
\ell_{ik} = \frac{1}{u_{kk}}\!\left(a_{ik} - \sum_{p=1}^{k-1} \ell_{ip} u_{pk}\right)
\qquad\text{for } i=k+1,\ldots,n
$$

Once the factors are known, $A\mathbf{x}=\mathbf{b}$ is solved as
$L\mathbf{y}=\mathbf{b}$ (forward) then $U\mathbf{x}=\mathbf{y}$ (backward).

## API

`POST /api/solve` — JSON body:

```json
{
  "matrix": "2 -1 -2\n-4 6 3\n-4 -2 8",
  "vector": "-1 9 -2",
  "pivot":  false
}
```

Returns the full decomposition, both substitution traces, and the
solution vector. Steps are returned as LaTeX strings ready for MathJax.

## Author

PIT Finals 2026 — Numerical Methods Online Calculator
Topic 08: LU Decomposition (Doolittle)
