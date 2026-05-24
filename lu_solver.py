"""
LU Decomposition (Doolittle Method) — Core Algorithm
=====================================================

This module implements the Doolittle variant of LU decomposition manually,
without relying on NumPy/SciPy's built-in factorization. It produces
step-by-step traces suitable for educational display.

Doolittle's method factors a square matrix A into:
        A = L * U
where L is lower-triangular with 1's on the diagonal and U is upper-triangular.

We also implement an optional partial-pivoting variant which produces:
        P * A = L * U
where P is a permutation matrix tracked as a row swap list.

Author: PIT Finals 2026
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _zeros(n: int) -> List[List[float]]:
    """Return an n x n zero matrix as a list of lists."""
    return [[0.0 for _ in range(n)] for _ in range(n)]


def _identity(n: int) -> List[List[float]]:
    """Return the n x n identity matrix."""
    I = _zeros(n)
    for i in range(n):
        I[i][i] = 1.0
    return I


def _copy_matrix(M: List[List[float]]) -> List[List[float]]:
    return [row[:] for row in M]


def _fmt(x: float, dp: int = 6) -> str:
    """Format a number for display: drop trailing zeros."""
    if abs(x) < 1e-12:
        x = 0.0
    s = f"{x:.{dp}f}"
    # Trim trailing zeros but keep at least one decimal digit
    if "." in s:
        s = s.rstrip("0").rstrip(".")
        if s in ("", "-"):
            s = "0"
    return s


def matrix_to_latex(M: List[List[float]], dp: int = 4) -> str:
    """Render a matrix as a LaTeX bmatrix string."""
    rows = []
    for row in M:
        rows.append(" & ".join(_fmt(v, dp) for v in row))
    return r"\begin{bmatrix}" + r" \\ ".join(rows) + r"\end{bmatrix}"


def vector_to_latex(v: List[float], dp: int = 4) -> str:
    return r"\begin{bmatrix}" + r" \\ ".join(_fmt(x, dp) for x in v) + r"\end{bmatrix}"


# ---------------------------------------------------------------------------
# Doolittle LU Decomposition (no pivoting)
# ---------------------------------------------------------------------------

def doolittle_lu(A: List[List[float]]) -> Dict[str, Any]:
    """
    Perform Doolittle LU decomposition of a square matrix A without pivoting.

    Doolittle convention: L has 1's on the diagonal.

    Returns a dict containing L, U, and a list of 'steps' describing each
    computation as it happens, for educational display.

    Raises ValueError if a zero pivot is encountered.
    """
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("Matrix must be square.")

    L = _identity(n)
    U = _zeros(n)
    steps: List[Dict[str, Any]] = []

    for k in range(n):
        # --- Compute row k of U ---------------------------------------------
        for j in range(k, n):
            s = sum(L[k][p] * U[p][j] for p in range(k))
            U[k][j] = A[k][j] - s

            # Build a LaTeX representation of the summation for display
            if k == 0:
                expr = f"U_{{{k+1}{j+1}}} = A_{{{k+1}{j+1}}} = {_fmt(A[k][j])}"
            else:
                terms = " + ".join(
                    f"L_{{{k+1}{p+1}}} \\cdot U_{{{p+1}{j+1}}}"
                    for p in range(k)
                )
                values = " + ".join(
                    f"({_fmt(L[k][p])})({_fmt(U[p][j])})" for p in range(k)
                )
                expr = (
                    f"U_{{{k+1}{j+1}}} = A_{{{k+1}{j+1}}} - ({terms}) "
                    f"= {_fmt(A[k][j])} - ({values}) = {_fmt(U[k][j])}"
                )
            steps.append({
                "type": "U",
                "i": k + 1,
                "j": j + 1,
                "latex": expr,
                "value": U[k][j],
            })

        # --- Compute column k of L ------------------------------------------
        for i in range(k + 1, n):
            if abs(U[k][k]) < 1e-14:
                raise ValueError(
                    f"Zero pivot encountered at U[{k+1}][{k+1}]. "
                    "Doolittle without pivoting fails for this matrix. "
                    "Try the partial-pivoting variant."
                )
            s = sum(L[i][p] * U[p][k] for p in range(k))
            L[i][k] = (A[i][k] - s) / U[k][k]

            if k == 0:
                expr = (
                    f"L_{{{i+1}{k+1}}} = \\frac{{A_{{{i+1}{k+1}}}}}{{U_{{{k+1}{k+1}}}}} "
                    f"= \\frac{{{_fmt(A[i][k])}}}{{{_fmt(U[k][k])}}} = {_fmt(L[i][k])}"
                )
            else:
                terms = " + ".join(
                    f"L_{{{i+1}{p+1}}} \\cdot U_{{{p+1}{k+1}}}"
                    for p in range(k)
                )
                values = " + ".join(
                    f"({_fmt(L[i][p])})({_fmt(U[p][k])})" for p in range(k)
                )
                expr = (
                    f"L_{{{i+1}{k+1}}} = \\frac{{A_{{{i+1}{k+1}}} - ({terms})}}{{U_{{{k+1}{k+1}}}}} "
                    f"= \\frac{{{_fmt(A[i][k])} - ({values})}}{{{_fmt(U[k][k])}}} = {_fmt(L[i][k])}"
                )
            steps.append({
                "type": "L",
                "i": i + 1,
                "j": k + 1,
                "latex": expr,
                "value": L[i][k],
            })

    return {"L": L, "U": U, "steps": steps}


# ---------------------------------------------------------------------------
# Forward / backward substitution
# ---------------------------------------------------------------------------

def forward_substitution(L: List[List[float]], b: List[float]) -> Tuple[List[float], List[Dict[str, Any]]]:
    """
    Solve L * y = b for y, where L is lower-triangular with 1's on the diagonal.
    Returns (y, steps).
    """
    n = len(L)
    y = [0.0] * n
    steps: List[Dict[str, Any]] = []

    for i in range(n):
        s = sum(L[i][j] * y[j] for j in range(i))
        y[i] = b[i] - s

        if i == 0:
            expr = f"y_{{{i+1}}} = b_{{{i+1}}} = {_fmt(b[i])}"
        else:
            terms = " + ".join(f"L_{{{i+1}{j+1}}} y_{{{j+1}}}" for j in range(i))
            values = " + ".join(f"({_fmt(L[i][j])})({_fmt(y[j])})" for j in range(i))
            expr = (
                f"y_{{{i+1}}} = b_{{{i+1}}} - ({terms}) "
                f"= {_fmt(b[i])} - ({values}) = {_fmt(y[i])}"
            )
        steps.append({"i": i + 1, "latex": expr, "value": y[i]})

    return y, steps


def backward_substitution(U: List[List[float]], y: List[float]) -> Tuple[List[float], List[Dict[str, Any]]]:
    """
    Solve U * x = y for x, where U is upper-triangular.
    Returns (x, steps).
    """
    n = len(U)
    x = [0.0] * n
    steps: List[Dict[str, Any]] = []

    for i in range(n - 1, -1, -1):
        if abs(U[i][i]) < 1e-14:
            raise ValueError(f"Singular U: U[{i+1}][{i+1}] = 0.")
        s = sum(U[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (y[i] - s) / U[i][i]

        if i == n - 1:
            expr = (
                f"x_{{{i+1}}} = \\frac{{y_{{{i+1}}}}}{{U_{{{i+1}{i+1}}}}} "
                f"= \\frac{{{_fmt(y[i])}}}{{{_fmt(U[i][i])}}} = {_fmt(x[i])}"
            )
        else:
            terms = " + ".join(
                f"U_{{{i+1}{j+1}}} x_{{{j+1}}}" for j in range(i + 1, n)
            )
            values = " + ".join(
                f"({_fmt(U[i][j])})({_fmt(x[j])})" for j in range(i + 1, n)
            )
            expr = (
                f"x_{{{i+1}}} = \\frac{{y_{{{i+1}}} - ({terms})}}{{U_{{{i+1}{i+1}}}}} "
                f"= \\frac{{{_fmt(y[i])} - ({values})}}{{{_fmt(U[i][i])}}} = {_fmt(x[i])}"
            )
        steps.append({"i": i + 1, "latex": expr, "value": x[i]})

    return x, steps


# ---------------------------------------------------------------------------
# Doolittle LU with Partial Pivoting (P * A = L * U)
# ---------------------------------------------------------------------------

def doolittle_lu_pivot(A: List[List[float]]) -> Dict[str, Any]:
    """
    Doolittle LU decomposition with partial pivoting.
    Returns P (as a list of row indices), L, U, and a list of row swaps.
    """
    n = len(A)
    U = _copy_matrix(A)
    L = _identity(n)
    perm = list(range(n))   # P represented as a permutation of row indices
    swaps: List[Tuple[int, int]] = []

    for k in range(n):
        # Find pivot row (largest |U[i][k]| for i >= k)
        pivot_row = max(range(k, n), key=lambda i: abs(U[i][k]))
        if abs(U[pivot_row][k]) < 1e-14:
            raise ValueError(f"Matrix is singular at column {k+1}.")

        if pivot_row != k:
            U[k], U[pivot_row] = U[pivot_row], U[k]
            perm[k], perm[pivot_row] = perm[pivot_row], perm[k]
            # Swap already-computed columns of L (first k entries)
            for col in range(k):
                L[k][col], L[pivot_row][col] = L[pivot_row][col], L[k][col]
            swaps.append((k + 1, pivot_row + 1))

        for i in range(k + 1, n):
            factor = U[i][k] / U[k][k]
            L[i][k] = factor
            for j in range(k, n):
                U[i][j] -= factor * U[k][j]

    # Build permutation matrix P from perm
    P = _zeros(n)
    for i, p in enumerate(perm):
        P[i][p] = 1.0

    return {"L": L, "U": U, "P": P, "perm": perm, "swaps": swaps}


# ---------------------------------------------------------------------------
# Full solver — combines decomposition + substitutions
# ---------------------------------------------------------------------------

def solve_system(
    A: List[List[float]],
    b: List[float],
    use_pivoting: bool = False,
) -> Dict[str, Any]:
    """
    Solve A * x = b using LU decomposition (Doolittle).
    Returns a comprehensive dict with all intermediate state.
    """
    n = len(A)
    if len(b) != n:
        raise ValueError("Length of b must match dimension of A.")

    if use_pivoting:
        res = doolittle_lu_pivot(A)
        L, U, perm = res["L"], res["U"], res["perm"]
        # Pb = b reordered by perm
        pb = [b[perm[i]] for i in range(n)]
        y, fwd_steps = forward_substitution(L, pb)
        x, bwd_steps = backward_substitution(U, y)
        return {
            "mode": "pivot",
            "A": A, "b": b,
            "L": L, "U": U,
            "P": res["P"],
            "perm": perm,
            "swaps": res["swaps"],
            "Pb": pb,
            "y": y, "x": x,
            "forward_steps": fwd_steps,
            "backward_steps": bwd_steps,
        }
    else:
        res = doolittle_lu(A)
        L, U, decomp_steps = res["L"], res["U"], res["steps"]
        y, fwd_steps = forward_substitution(L, b)
        x, bwd_steps = backward_substitution(U, y)
        return {
            "mode": "doolittle",
            "A": A, "b": b,
            "L": L, "U": U,
            "y": y, "x": x,
            "decomposition_steps": decomp_steps,
            "forward_steps": fwd_steps,
            "backward_steps": bwd_steps,
        }


# ---------------------------------------------------------------------------
# Verification helper (matrix multiply for showing L*U = A)
# ---------------------------------------------------------------------------

def mat_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    n, m, p = len(A), len(B), len(B[0])
    C = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            C[i][j] = sum(A[i][k] * B[k][j] for k in range(m))
    return C
