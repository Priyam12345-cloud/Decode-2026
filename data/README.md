# Decode 2026 Round 2 — aligned synthetic data release v4

This release is synthetic and intentionally aligned to the figures shown in the Round 2 brief.

## Portfolio control totals

- 7,300 active large-group employer accounts
- 2,200,000 covered lives
- $15.000bn annual premium
- 1,650,000 paid claim episodes
- $13.305bn paid claims and 88.7% case medical loss ratio
- 48 rating regions

## Track A case assumptions

- For the primary 2026 case MLR, carry FY2025 paid claims forward without additional medical inflation or utilization trend.
- Do not apply the B4 trend fields to the primary case MLR. Teams may show alternative trend scenarios separately.
- B2 covers FY2023–FY2025 only. These are the three years used for the renewal curve in the brief.
- The 80–85% range is the internal case pricing corridor. Regulatory MLR is measured separately.

## Track B case assumptions

- A row in B3 is a paid claim episode, not a raw claim line.
- member_token is a fictional, non-identifying member reference that is unique only within an account.
- Current B3 outcomes are withheld. Use a 1.8% current issue-prevalence assumption when calibrating probabilities.
- fraud_audit_sample is a historical case-control sample with confirmed fraud intentionally over-represented. It does not join to the FY2025 claim universe.
- Some current patterns resemble the historical sample. Other patterns are intentionally absent from the labelled sample and must be identified from the current claims population.
- Use $1,500 as the cost of each completed review. Estimate recoverable value from the historical recovery outcomes.
- The economic audit queue has 33,000 slots. Rank it by expected recoverable value.
- A separate anomaly-discovery queue has 7,000 additional slots. Use it for credible patterns that the historical labels may not capture.
- eligible_watchlist_2026 identifies a candidate pool of 1,800 providers. Submit exactly 250 providers from that pool.
- All identifiers and values are fictional and provided only for the case exercise.

## Join keys

- Join B1 to B2 and B3 using account_id.
- Join B3 to provider_reference using provider_id.
- Join B1 and provider_reference to B4 using rating_region.
- fraud_audit_sample contains historical snapshot identifiers and should not be joined to B3.

## File schemas

### B1_account_master.csv.gz

- account_id: unique employer account identifier
- rating_region: one of 48 synthetic rating regions
- industry: employer industry
- covered_lives_2025: covered lives in FY2025
- annual_premium_2025: FY2025 gross written premium, USD
- risk_score_2025: continuous account risk score
- risk_band: risk-score band used in the brief
- renewal_month: calendar month of annual renewal
- account_status: account status at the data cut

### B2_renewal_quote_history.csv.gz

- quote_id: unique historical quote identifier
- account_id: employer account identifier
- quote_year: quote year, FY2023–FY2025
- quoted_rate_change_pct: offered premium change in percentage points
- renewed_flag: 1 if the account renewed, otherwise 0
- quoted_annual_premium: quoted annual premium, USD
- risk_score_at_quote: account risk score at quote time

### B3_claims_experience_details.csv.gz

- claim_episode_id: unique FY2025 paid claim episode identifier
- account_id: employer account identifier
- member_token: fictional member reference scoped to the account
- provider_id: provider identifier
- service_date: service date in YYYY-MM-DD format
- care_setting: care setting known before review
- diagnosis_group: synthetic diagnosis group
- procedure_group: synthetic procedure group
- billed_amount: provider billed amount, USD
- allowed_amount: plan allowed amount, USD
- paid_amount: insurer paid amount, USD
- member_cost_share: allowed amount less paid amount, USD
- episode_status: processing status

### B4_regional_macro_benchmarks.csv.gz

- rating_region: synthetic rating region
- calendar_year: calendar year, 2023–2026
- medical_cost_inflation_pct: annual medical cost inflation, percentage points
- utilization_trend_pct: annual utilization trend, percentage points
- unemployment_rate_pct: unemployment rate, percentage points

### B5_claims_integrity_trend.csv.gz

- calendar_year: calendar year, 2022–2025
- paid_claims_billion: total paid claims, USD billions
- anomalous_paid_share_pct: estimated anomalous share of paid claim dollars
- recovery_share_of_paid_pct: confirmed recovery as a share of paid claims
- estimated_anomalous_paid_billion: estimated anomalous paid claims, USD billions
- estimated_recovery_billion: estimated recovery, USD billions

### fraud_audit_sample.csv.gz

- audit_case_id: unique historical audit case identifier
- historical_claim_episode_id: synthetic historical claim identifier
- audit_year: audit year
- audit_method: audit method
- account_risk_score_snapshot: account risk score available at audit selection
- provider_risk_score_snapshot: provider risk score available at audit selection
- paid_amount_snapshot: paid amount available at audit selection, USD
- care_setting_snapshot: care setting available at audit selection
- confirmed_fraud_flag: 1 for confirmed fraud, otherwise 0
- recovery_amount: confirmed recovery, USD

### provider_reference.csv.gz

- provider_id: unique provider identifier
- rating_region: synthetic rating region
- specialty: provider specialty
- network_tier: network tier
- provider_risk_score: continuous provider risk score available before audit
- eligible_watchlist_2026: eligibility flag for the 1,800-provider candidate pool

### Submission templates

- submission_account_rates.csv: account rate recommendations and projected outcomes
- submission_claim_scores.csv: fraud risk, anomaly scores and both review-queue ranks
- submission_provider_watchlist.csv: ranked provider watchlist and rationale
