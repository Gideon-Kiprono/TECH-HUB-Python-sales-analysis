# Tech Hub Kenya: September 2026 Sales Analysis

Standard-library analysis of the September 2026 till export, checked against pandas.

## How to run
    python -m venv my_env
    my_env\Scripts\Activate.ps1        # Mac/Linux: source my_env/bin/activate
    python -m pip install -r requirements.txt
    python sales_analysis.py
The report prints to the screen and is saved to `output/sales_report.txt`.
Tasks 1-7 use only the standard library; pandas is used only in `verify_with_pandas`.

## Approach
- Read the CSV with `csv.DictReader`, then clean each row (`parse_number`, `convert_rows`).
- Revenue per row = quantity x unit price. All aggregates use plain dicts, `sorted()` with a key, list/dict comprehensions, and my own mean/median/min-max functions.
- `verify_with_pandas` repeats the same cleaning rules in pandas and compares results with a tolerance of KES 0.01.

## Cleaning rules
| Raw value | Decision | Why |
|---|---|---|
| `"38,999"` (S-3017) | Repaired to 38999 | The comma is a thousands separator; the meaning is certain |
| `KES 18999` (S-3029) | Repaired to 18999 | `KES` is only the currency label |
| `two` (S-3006) | Skipped | Only digits are trusted; supporting number words would need an open-ended list of rules |
| `N/A` (S-3030) | Skipped | No price is given |
| Blank quantity (S-3035) | Skipped | A quantity cannot be guessed |
| Blank price (S-3039) | Skipped | Inventing a price (zero or an average) would make the revenue misleading |

Result: 46 of 50 rows used, 4 skipped, each with its reason in the report.

## Tie-breaking
Products with equal revenue are ranked alphabetically by name (sort key `(-revenue, name)`). There were no ties in this data.

## Findings
- Total revenue is KES 1,310,812.00.
- The top three products (HP 15 Laptop, Hisense 43in Smart TV, Lenovo Tab M10) make up about 67% of revenue. [check: (389,994 + 272,993 + 199,992) / 1,310,812]
- The median sale (KES 11,097) is far below the mean (KES 28,496) because a few large laptop and TV sales pull the average up.
- Five sales reached KES 50,000; Kisumu Mega Plaza had two of them. Mombasa City Mall had none.

## Assumptions
- Revenue is quantity x unit price; no discounts or taxes are in the data.
- The 50,000 threshold is inclusive (`>=`); S-3003 at KES 49,998 just misses it.
- Stores with no high-value sales are listed with a count of 0.
- Skipped rows are excluded from every total, so the totals are a lower bound of September revenue.

## pandas verification
All four checks (total, revenue by product, top 3, mean/median) report MATCH.