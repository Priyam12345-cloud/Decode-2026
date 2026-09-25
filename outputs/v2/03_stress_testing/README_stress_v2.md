# v2 stress-test summary

Primary case: FY2025 paid claims carried forward, no trend. B4 trend reported separately.

## Scenarios meeting both limits (retention >= 80%, MLR <= 85%)
                                primary-case scenarios meeting retention>=80% and MLR<=85%  scenarios
solution                                                                                             
v1 nb06                                                                                  2         11
v1 nb07                                                                                  3         11
v2 FINAL (robust + guardrails)                                                           7         11
v2 nominal                                                                               5         11
v2 robust                                                                                7         11

## Breakpoints
                      solution  base_retention  base_mlr  max_claims_increase_before_85pct  max_claims_decrease_before_80pct  retention_headroom_pts  max_price_sensitivity_multiple
                    v2 nominal          0.8071    0.8087                            0.0511                            0.0108                  0.7133                            1.02
                     v2 robust          0.8375    0.8126                            0.0461                            0.0154                  3.7517                            1.24
v2 FINAL (robust + guardrails)          0.8375    0.8145                            0.0436                            0.0178                  3.7467                            1.24
                       v1 nb06          0.7989    0.8087                            0.0510                            0.0108                 -0.1071                             NaN
                       v1 nb07          0.8013    0.8258                            0.0293                            0.0313                  0.1338                            1.00

## Monte Carlo
                      solution  sims  retention_mean  retention_p05  mlr_mean  mlr_p05  mlr_p95  contribution_mean  contribution_p05  prob_retention_ok  prob_mlr_ok  prob_all_limits_ok
                    v2 nominal  3000          0.8056         0.7949    0.8085   0.8004   0.8163       2.632765e+09      2.513558e+09             0.8050       0.9560              0.7747
                     v2 robust  3000          0.8361         0.8262    0.8124   0.8044   0.8200       2.609508e+09      2.493641e+09             1.0000       0.9923              0.9923
v2 FINAL (robust + guardrails)  3000          0.8360         0.8263    0.8144   0.8065   0.8218       2.582625e+09      2.467432e+09             1.0000       0.9977              0.9977
                       v1 nb06  3000          0.7973         0.7864    0.8086   0.8002   0.8165       2.603064e+09      2.480358e+09             0.3563       0.9543              0.3450
                       v1 nb07  3000          0.7999         0.7900    0.8260   0.8189   0.8332       2.370554e+09      2.254452e+09             0.5000       1.0000              0.5000

## B4 trend alternative
                                                                                        view  account_retention  case_mlr  expected_contribution  avg_rate_premium_weighted  accounts_at_cap
                                 FINAL no-trend rates, B4 trend arrives (monitoring trigger)             0.8375    0.8698           1.815124e+09                    12.0398             1211
B4 trend: corridor NOT reachable within +25% cap; best plan with retention>=80% + guardrails             0.8006    0.8650           1.852689e+09                    13.8393             1448
