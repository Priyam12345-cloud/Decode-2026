# EDA summary: Track A 2026 renewal pricing

## Profitability

FY2025 mean MLR is 83.5%; median MLR is 54.5%; 21.2% of accounts are loss-making. Accounts at or above the median FY2025 risk score generate 77.6% of paid claims.

Finding -> FY2025 profitability is heterogeneous and concentrated in higher-risk accounts. Business implication -> use account-level claims and risk information for 2026 pricing. Modelling implication -> retain latest MLR, frequency, severity, exposure and current risk candidates.

## Renewal and price response

For each quote year, renewal analysis uses only `risk_score_at_quote`, `quoted_rate_change_pct`, `renewed_flag`, stable B1 account attributes, and matching-year B4 regional values. The observed renewal drop from the lowest to highest populated rate band is approximately 2023: 28%, 2024: 28%, 2025: 28%. The four-panel analysis compares quote-time risk band, industry, account size and quote-year regional economic tier with sample counts.

Finding -> Price increases have an observable retention trade-off and curves differ across segments. Business implication -> broad increases can create adverse selection. Modelling implication -> preserve quote-year response evidence and interactions for later validation; do not interpret descriptive curves causally.

Retrospective-only note -> FY2025 MLR/loss-making is used for the 2026 profitability analysis only. It is not used to explain 2023 or 2024 renewal behaviour.

## Temporal stability

B2 renewal rate, offered rate change, quoted premium and `risk_score_at_quote` are compared using each quote year's data. Matching-year B4 benchmarks are used for regional response analysis. B3 is FY2025-only, so claims/MLR/frequency/severity stability across years cannot be assessed.

Finding -> B2 supports historical validation, but claims trends need additional years. Business implication -> do not claim a multi-year claims trend from this release. Modelling implication -> use FY2025 claims as latest experience only.

## Regional context

The regional response analysis uses B4 benchmarks matched to each B2 quote year. B4 medical inflation and utilization trend are excluded from the primary case because FY2025 paid claims are carried into 2026 without either uplift.

## Redundancy and leakage

MLR is deterministically paid claims divided by premium; `risk_band` is derived from the current B1 risk score and is reserved for 2026 interpretation, while historical renewal uses quote-year `risk_score_at_quote`; IDs are excluded as predictors; future outcomes and post-renewal information are excluded. No coefficients were used for selection.

## Candidate 2026 features entering model validation

latest_mlr, latest_claim_frequency, latest_claim_severity, latest_claim_count, covered_lives_2025, latest_risk_score, rating_region, renewal_rate_3yr, rate_change_mean_3yr, historical_loss_making_indicator

## Dropped features

three_year_average_mlr, claims_trend, medical_cost_inflation_pct, utilization_trend_pct, renewed_2026, account_id, account_status

No ML model or optimization was run.