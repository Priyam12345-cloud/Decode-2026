# FINAL Track A recommendation - v2 robust MILP + refined business rules

## Portfolio (primary case: FY2025 claims carried forward, no trend)
                Unnamed: 0        value
         account_retention 8.374670e-01
premium_weighted_retention 8.303815e-01
          expected_premium 1.394059e+10
           expected_claims 1.135465e+10
                  case_mlr 8.145027e-01
     expected_contribution 2.585942e+09
 avg_rate_premium_weighted 1.203985e+01
           accounts_at_cap 1.211000e+03
         accounts_with_cut 0.000000e+00
   retained_risk_mix_drift 2.213105e-02
   covered_lives_retention 8.278453e-01
           fy2025_case_mlr 8.870000e-01
    mlr_points_improvement 7.249735e+00

## Solver
                        run solver_status    objective  runtime_seconds  fractional_accounts
LP relaxation (upper bound)       Optimal 2.572242e+09        76.061212                    1
            MILP (decision)       Optimal 2.572242e+09       178.819918                    0

## Constraint report
                          check     value         limit  pass
 Accounts with exactly one rate      7300       = 7,300  True
                     Rate range 0% to 25%  -15% to +25%  True
              Account retention  0.837467        >= 80%  True
                       Case MLR  0.814503        80-85%  True
     Premium-weighted retention  0.830382        >= 80%  True
        Retained risk-mix drift  0.022131 within +/-15%  True
     Top-50 accounts above +15%         0           = 0  True
    Retention under lapse_shock  0.810785        >= 80%  True
          MLR under lapse_shock  0.819288        <= 85%  True
Retention under price_sensitive       0.8        >= 80%  True
      MLR under price_sensitive   0.80753        <= 85%  True
       MLR under claims_up_4pct  0.847083        <= 85%  True

## Comparison (all on the v2 renewal curve)
                 solution  expected_contribution  account_retention  premium_weighted_retention  case_mlr  risk_mix_drift
        v1 nb06 heuristic           2.607244e+09             0.7989                      0.7974    0.8087          0.0315
v1 nb07 refined heuristic           2.377788e+09             0.8013                      0.8045    0.8258          0.0438
          v2 nominal MILP           2.636389e+09             0.8071                      0.8100    0.8087          0.0308
           v2 robust MILP           2.612325e+09             0.8375                      0.8292    0.8126          0.0215
FINAL v2 robust + refined           2.585942e+09             0.8375                      0.8304    0.8145          0.0221

## Stress: primary scenarios meeting both limits
                           primary scenarios meeting retention>=80% & MLR<=85%  of
solution                                                                          
v1 nb06 heuristic                                                            2  11
v1 nb07 refined heuristic                                                    3  11
v2 nominal MILP                                                              5  11
v2 robust MILP                                                               7  11
FINAL v2 robust + refined                                                    7  11

## Final solution stress table
                                           family  account_retention  premium_weighted_retention  case_mlr  expected_contribution  retention_pass  mlr_corridor_pass  mlr_ceiling_pass
scenario                                                                                                                                                                              
Favorable                                combined             0.8550                      0.8485    0.7710           3.262927e+09            True              False              True
Mild favorable                           combined             0.8550                      0.8485    0.8115           2.684878e+09            True               True              True
Base                                         base             0.8375                      0.8304    0.8145           2.585942e+09            True               True              True
Mild adverse                             combined             0.8198                      0.8121    0.8585           1.928845e+09            True              False             False
Moderate adverse                         combined             0.8109                      0.8030    0.8602           1.883896e+09            True              False             False
Severe adverse                           combined             0.7929                      0.7845    0.9049           1.251776e+09           False              False             False
Lapse shock only (-3 pts)                 renewal             0.8109                      0.8030    0.8193           2.436059e+09            True               True              True
Price response +25%                       renewal             0.8000                      0.7884    0.8075           2.539264e+09            True               True              True
Adverse selection (risk<1.0 lapse)        renewal             0.8022                      0.7954    0.8304           2.268791e+09            True               True              True
Claims +4% only                            claims             0.8375                      0.8304    0.8471           2.131756e+09            True               True              True
Claims +5% only                            claims             0.8375                      0.8304    0.8552           2.018210e+09            True              False             False
B4 trend, rates not reloaded        B4 (separate)             0.8375                      0.8304    0.8698           1.815124e+09            True              False             False
Combined severe (B4 + -5 pts)       B4 (separate)             0.7929                      0.7845    0.8785           1.599678e+09           False              False             False

## Breakpoints
                 solution  base_retention  base_mlr  max_claims_increase_before_85pct  retention_headroom_pts  max_logit_lapse_shock  max_price_sensitivity_multiple
        v1 nb06 heuristic          0.7989    0.8087                            0.0510                 -0.1071                    NaN                             NaN
v1 nb07 refined heuristic          0.8013    0.8258                            0.0293                  0.1338                   0.00                            1.00
          v2 nominal MILP          0.8071    0.8087                            0.0511                  0.7133                   0.04                            1.02
           v2 robust MILP          0.8375    0.8126                            0.0461                  3.7517                   0.26                            1.24
FINAL v2 robust + refined          0.8375    0.8145                            0.0436                  3.7467                   0.26                            1.24

## Monte Carlo
                 solution  sims  retention_mean  retention_p05  mlr_mean  mlr_p05  mlr_p95  contribution_mean  contribution_p05  prob_retention_ok  prob_mlr_ok  prob_all_limits_ok
        v1 nb06 heuristic  3000          0.7973         0.7864    0.8086   0.8002   0.8165       2.603064e+09      2.480358e+09             0.3563       0.9543              0.3450
v1 nb07 refined heuristic  3000          0.7999         0.7900    0.8260   0.8189   0.8332       2.370554e+09      2.254452e+09             0.5000       1.0000              0.5000
          v2 nominal MILP  3000          0.8056         0.7949    0.8085   0.8004   0.8163       2.632765e+09      2.513558e+09             0.8050       0.9560              0.7747
           v2 robust MILP  3000          0.8361         0.8262    0.8124   0.8044   0.8200       2.609508e+09      2.493641e+09             1.0000       0.9923              0.9923
FINAL v2 robust + refined  3000          0.8360         0.8263    0.8144   0.8065   0.8218       2.582625e+09      2.467432e+09             1.0000       0.9977              0.9977

Note: the +10% claims 'Severe adverse' and B4-trend scenarios cannot be met by any rate set inside a 5-pt corridor while holding the 80% floor at base; they are re-pricing triggers, not pricing failures.
