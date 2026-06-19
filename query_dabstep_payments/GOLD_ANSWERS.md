# Gold Answers

These are the deterministic answers for the current visible split:

- `payments_db`: `query_dataset/payments.duckdb`
- `context_db`: `query_dataset/context.db`

Each query still keeps its DAB-style answer in `queryN/ground_truth.csv`.
This file is only a dataset-level index for easier inspection.

| Query | Candidate | Question | Gold answer |
|---|---|---|---|
| query1 | C1 | Which merchant category had the highest payment refusal rate in 2023 among categories with at least 10,000 transactions? Return the MCC code and category description. | `7993,Video Amusement Game Supplies` |
| query2 | C8 | In 2023, which merchant had the most payments routed through an acquiring country that is not among its configured acquirer countries? Return the merchant name, acquiring country code, and number of such payments. | `Rafa_AI,NL,27696` |
| query3 | C3 | Which merchant had the largest fraudulent cross-border transaction volume in 2023? Return the merchant name and the volume rounded to two decimals. | `Crossfit_Hanna,324614.02` |
| query4 | C7 | For Crossfit_Hanna, if every 2023 payment were priced as though its MCC had been 5411 for the entire year, what would be the increase in total processing fees compared with its actual MCC? Return the merchant name and the increase in euros rounded to two decimals. | `Crossfit_Hanna,18657.35` |
| query5 | C5 | For Crossfit_Hanna in July 2023, which fee rule IDs apply to its transactions? Return all matching fee IDs in ascending order. | `29,36,51,64,65,89,107,123,150,163,276,304,381,384,428,454,473,477,536,572,595,626,631,678,680,704,709,741,792,813,861,871,884` |
| query6 | C6 | What total processing fee did Rafa_AI owe for March 2023? Return the amount in euros rounded to two decimals. | `1546.82` |

## Recompute

Ground-truth files are generated from the clean canonical database:

```bash
/home/ubuntu/benchmark-reproduction/.venv/bin/python \
  dab_new/query_dabstep_payments/manual_querycode/compute_ground_truth.py
```

Solvability against the visible split is checked with:

```bash
/home/ubuntu/benchmark-reproduction/.venv/bin/python \
  dab_new/query_dabstep_payments/manual_querycode/verify_visible_solve.py
```
