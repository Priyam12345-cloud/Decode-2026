"""
Track A v2 helper functions (shared by notebooks 10, 11 and 12).

Design notes
------------
* Renewal model  : logistic regression with a HINGE in the offered rate
                   (separate slopes for cuts and increases, a curvature term on increases,
                   and an increase x risk interaction). The historical curve is flat for
                   cuts (~92%) and falls only for increases - a single linear rate slope
                   cannot reproduce that and over-states the retention that cuts can buy.
* Economics      : for account i and action r
                       premium_ir = P0_i * (1 + r) * p_ir
                       claims_ir  = C_i  * p_ir        (FY2025 paid claims carried forward, no trend)
                   Both sides are ALWAYS multiplied by the same renewal probability.
* Optimiser      : one-rate-per-account multiple-choice MILP solved with HiGHS (highspy).
                   The LP relaxation is solved as the upper bound; with only a handful of
                   coupling constraints at most that many accounts can be fractional,
                   so the LP bound is (near-)tight and the MILP proves optimality quickly.
"""
import numpy as np
import pandas as pd
import time
from scipy import sparse

RATES = np.arange(-15, 26)          # 41 permitted actions, 1pt steps
RATE0_COL = int(np.where(RATES == 0)[0][0])
RATE_FEATURES = ['rate_pos', 'rate_neg', 'rate_pos2', 'rate_pos_x_risk']


# ----------------------------------------------------------------------------------------
# Renewal-model features
# ----------------------------------------------------------------------------------------
def add_history_features(b2):
    """Lagged quote history strictly BEFORE each quote year (no look-ahead)."""
    b2 = b2.sort_values(['account_id', 'quote_year']).copy()
    g = b2.groupby('account_id')
    b2['n_prior'] = g.cumcount()
    denom = b2['n_prior'].replace(0, np.nan)
    b2['prior_renewal_rate'] = (g['renewed_flag'].cumsum() - b2['renewed_flag']) / denom
    b2['prior_rate_mean'] = (g['quoted_rate_change_pct'].cumsum() - b2['quoted_rate_change_pct']) / denom
    b2['prior_rate_last'] = g['quoted_rate_change_pct'].shift(1)
    # premium BEFORE the offered change, so the premium feature does not move with the action
    b2['base_premium'] = b2['quoted_annual_premium'] / (1 + b2['quoted_rate_change_pct'] / 100)
    return b2


def make_features(d, spec, prior_renewal_fill):
    r = d['quoted_rate_change_pct'].to_numpy(float)
    k = d['risk_score_at_quote'].to_numpy(float)
    F = pd.DataFrame(index=d.index)
    if spec == 'linear':                       # the v1 specification (single rate slope)
        F['rate'] = r
    else:                                      # hinge specification
        F['rate_pos'] = np.maximum(r, 0)
        F['rate_neg'] = np.minimum(r, 0)
        F['rate_pos2'] = np.maximum(r, 0) ** 2 / 25
        F['rate_pos_x_risk'] = np.maximum(r, 0) * k
    F['risk'] = k
    F['log_premium'] = np.log(d['base_premium'].to_numpy(float))
    F['prior_renewal_rate'] = d['prior_renewal_rate'].fillna(prior_renewal_fill).to_numpy()
    F['prior_rate_mean'] = d['prior_rate_mean'].fillna(0).to_numpy()
    F['prior_rate_last'] = d['prior_rate_last'].fillna(0).to_numpy()
    F['no_history'] = d['prior_rate_last'].isna().astype(float).to_numpy()
    dummies = pd.get_dummies(d[['industry', 'rating_region']], drop_first=True).astype(float)
    return pd.concat([F, dummies.set_index(d.index)], axis=1)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


# ----------------------------------------------------------------------------------------
# Account economics on the 7,300 x 41 grid
# ----------------------------------------------------------------------------------------
def grid_economics(P, prem0, claims0, claim_mult=1.0):
    premium = prem0[:, None] * (1 + RATES[None, :] / 100) * P
    claims = (claims0 * claim_mult)[:, None] * P if np.ndim(claim_mult) else claims0[:, None] * claim_mult * P
    return premium, claims


def portfolio_metrics(choice, P, prem0, claims0, claim_mult=1.0):
    i = np.arange(len(prem0))
    p = P[i, choice]
    r = RATES[choice]
    cl = claims0 * claim_mult
    premium = prem0 * (1 + r / 100) * p
    claims = cl * p
    return dict(account_retention=p.mean(),
                premium_weighted_retention=(prem0 * p).sum() / prem0.sum(),
                expected_premium=premium.sum(), expected_claims=claims.sum(),
                case_mlr=claims.sum() / premium.sum(),
                expected_contribution=premium.sum() - claims.sum(),
                avg_rate_premium_weighted=np.average(r, weights=prem0),
                accounts_at_cap=int((r == RATES.max()).sum()),
                accounts_with_cut=int((r < 0).sum()))


# ----------------------------------------------------------------------------------------
# Multiple-choice MILP / LP (HiGHS)
# ----------------------------------------------------------------------------------------
def solve_rate_mip(P, prem0, claims0, R=0.80, U=0.85, L=0.80, robust_scenarios=(),
                   integer=True, time_limit=1800, mip_gap=1e-6, verbose=False,
                   allowed=None, extra_rows=(), objective_penalty=None):
    """
    allowed        : optional N x K boolean mask (hard per-account rate restrictions).
    extra_rows     : optional iterable of (name, N x K coefficient array, lo, hi) portfolio rows.
    objective_penalty: optional N x K $ penalty subtracted from contribution (soft rules).
    max  sum_ir (premium_ir - claims_ir) x_ir
    s.t. sum_r x_ir = 1                               (one action per account)
         sum_ir p_ir x_ir >= R * N                    (account retention)
         sum_ir (claims_ir - U premium_ir) x_ir <= 0  (MLR ceiling, linearised)
         sum_ir (claims_ir - L premium_ir) x_ir >= 0  (MLR floor, linearised)
    robust_scenarios: iterable of dicts {name, P, claim_mult, R, U}; each adds the same
         retention / MLR-ceiling constraints evaluated under a stressed scenario, so the
         client's limits must still hold if that scenario materialises.
    """
    import highspy
    N, K = P.shape
    nv = N * K
    premium, claims = grid_economics(P, prem0, claims0)
    contrib = (premium - claims).ravel()
    if objective_penalty is not None:
        contrib = contrib - objective_penalty.ravel()
    rows = [('retention', P.ravel(), R * N, np.inf),
            ('mlr_ceiling', (claims - U * premium).ravel(), -np.inf, 0.0),
            ('mlr_floor', (claims - L * premium).ravel(), 0.0, np.inf)]
    for name, coef, lo, hi in extra_rows:
        rows.append((name, np.asarray(coef).ravel(), lo, hi))
    for s in robust_scenarios:
        pr_s, cl_s = grid_economics(s['P'], prem0, claims0, s.get('claim_mult', 1.0))
        if s.get('R') is not None:
            rows.append((f"{s['name']}_retention", s['P'].ravel(), s['R'] * N, np.inf))
        if s.get('U') is not None:
            rows.append((f"{s['name']}_mlr_ceiling", (cl_s - s['U'] * pr_s).ravel(), -np.inf, 0.0))

    h = highspy.Highs()
    h.setOptionValue('output_flag', verbose)
    h.setOptionValue('time_limit', float(time_limit))
    h.setOptionValue('mip_rel_gap', mip_gap)
    idx = np.arange(nv, dtype=np.int32)
    h.addVars(nv, np.zeros(nv), np.ones(nv) if allowed is None else allowed.ravel().astype(float))
    h.changeColsCost(nv, idx, -contrib / 1e6)                 # objective in $m for numerics
    A = sparse.csr_matrix((np.ones(nv), (np.repeat(np.arange(N), K), idx)), shape=(N, nv))
    h.addRows(N, np.ones(N), np.ones(N), A.nnz, A.indptr[:-1].astype(np.int32),
              A.indices.astype(np.int32), A.data)
    INF = highspy.kHighsInf
    for _, coef, lo, hi in rows:
        s = 1e6 if np.abs(coef).max() > 10 else 1.0        # $ rows scaled to $m
        h.addRow(lo / s if np.isfinite(lo) else -INF, hi / s if np.isfinite(hi) else INF, nv, idx, coef / s)
    if integer:
        h.changeColsIntegrality(nv, idx, np.full(nv, highspy.HighsVarType.kInteger))
    t0 = time.perf_counter()
    h.run()
    runtime = time.perf_counter() - t0
    x = np.asarray(h.getSolution().col_value).reshape(N, K)
    info = h.getInfo()
    out = dict(solver_status=h.modelStatusToString(h.getModelStatus()), runtime_seconds=runtime,
               objective=-info.objective_function_value * 1e6,
               fractional_accounts=int(((x > 1e-6) & (x < 1 - 1e-6)).any(1).sum()),
               n_coupling_constraints=len(rows))
    if integer:
        out.update(best_bound=-info.mip_dual_bound * 1e6, mip_gap=info.mip_gap)
    # row activities / slacks for reporting
    choice = x.argmax(1)
    out['constraint_names'] = [r[0] for r in rows]
    return x, choice, out


# ----------------------------------------------------------------------------------------
# Stressed renewal grids (logit space)
# ----------------------------------------------------------------------------------------
class RenewalStress:
    """Build stressed probability grids from the fitted hinge model.

    shift(delta)     : market-wide lapse shock, logit(p) - delta. Because it is applied in
                       logit space it removes more renewals from price-sensitive, healthier
                       accounts (p around 0.6-0.8) than from high-risk accounts (p ~ 0.99),
                       i.e. it reproduces the adverse-selection mechanism in the brief.
    elastic(k)       : the market becomes k-times as price sensitive to increases
                       (all rate terms scaled by k, relative to a flat quote).
    """
    def __init__(self, Zg, beta, rate_idx):
        self.L = Zg @ beta                                            # N x K logits
        lrate = (Zg[:, :, rate_idx] * beta[rate_idx]).sum(-1)
        self.lrate_rel = lrate - lrate[:, [RATE0_COL]]
        self.P = sigmoid(self.L)

    def shift(self, delta):
        return sigmoid(self.L - delta)

    def elastic(self, k):
        return sigmoid(self.L + (k - 1) * self.lrate_rel)

    def delta_for_drop(self, choice, drop):
        from scipy.optimize import brentq
        i = np.arange(self.L.shape[0])
        l = self.L[i, choice]
        base = sigmoid(l).mean()
        return brentq(lambda d: base - sigmoid(l - d).mean() - drop, -3, 3)


# ----------------------------------------------------------------------------------------
# Monte Carlo: renewal outcomes (Bernoulli) x model-parameter uncertainty x claims noise
# ----------------------------------------------------------------------------------------
def monte_carlo(choice, Zg, beta_draws, prem0, claims0, acct_claims_cv, n_bern=10, seed=11,
                claim_mult=1.0, systematic_claims_sd=0.0):
    rng = np.random.default_rng(seed)
    N = len(prem0)
    i = np.arange(N)
    Zc = Zg[i, choice, :].astype(float)
    prem = prem0 * (1 + RATES[choice] / 100)
    out = []
    for b in beta_draws:
        p = sigmoid(Zc @ b)
        for _ in range(n_bern):
            renew = rng.random(N) < p
            cl = claims0 * claim_mult * np.maximum(0, 1 + acct_claims_cv * rng.standard_normal(N))
            cl = cl * (1 + systematic_claims_sd * rng.standard_normal())
            pr, c = (prem * renew).sum(), (cl * renew).sum()
            out.append((renew.mean(), c / pr, pr - c))
    return pd.DataFrame(out, columns=['account_retention', 'case_mlr', 'contribution'])


def summarise_mc(r, R=0.80, L=0.80, U=0.85):
    ok_r = r['account_retention'] >= R
    ok_m = r['case_mlr'].between(L, U)
    return dict(sims=len(r),
                retention_mean=r['account_retention'].mean(), retention_p05=r['account_retention'].quantile(.05),
                mlr_mean=r['case_mlr'].mean(), mlr_p05=r['case_mlr'].quantile(.05), mlr_p95=r['case_mlr'].quantile(.95),
                contribution_mean=r['contribution'].mean(), contribution_p05=r['contribution'].quantile(.05),
                prob_retention_ok=ok_r.mean(), prob_mlr_ok=ok_m.mean(), prob_all_limits_ok=(ok_r & ok_m).mean())
