"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
from pathlib import Path
import pandas as pd
from contextlib import redirect_stdout
import io
import math


DATA_PATH = Path("data") / "electronics_sales.csv"


def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    """Read the CSV with the csv module and return the raw rows."""
    with open(path, newline = "", encoding = "utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def parse_number(value: str) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted."""
    if  value is None or not value.strip():
        return None
    cleaned_text = value.strip()  # remove unnecessary whitespace
    cleaned_text = cleaned_text.replace(",", "") #remove commas
    cleaned_tect =cleaned_text.upper

    if cleaned_text.startswith("KES"):
        cleaned_text = cleaned_text[3:]  #remove KES prefix

    try:
        return float(cleaned_text)  #convert to float
    except ValueError:
        return None


def convert_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (clean_rows, skipped_rows). Clean rows have numeric quantity, unit price and revenue."""
    clean,skipped = [], []
    for row in rows:
        qty = parse_number(row["quantity"])
        price = parse_number(row["unit_price_kes"])

        if qty is None:
            skipped.append({"sale_id": row["sale_id"], "reason": f"Invalid or missing quantity"})
            continue

        if price is None:
            skipped.append({"sale_id": row["sale_id"], "reason": f"Invalid or missing unit price"})
            continue

        clean.append({**row, "quantity": qty, "unit_price_kes": price,"revenue": qty * price})

    return clean, skipped


def total_revenue(rows: list[dict]) -> float:
    return sum(row["revenue"] for row in rows)


def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals = {}
    for row in rows:
        key = row[field]
        totals[key] = totals.get(key, 0) + row["revenue"]
    return totals


def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first."""
    return sorted(totals.items(), key=lambda x: (-x[1], x[0]))[:n]


def high_value(rows: list[dict], threshold: float) -> list[dict]:
    """Transactions whose revenue is at or above threshold (use a comprehension)."""
    return [row for row in rows if row["revenue"] >= threshold]


# Reusable statistics - implement these yourself, no statistics module.
def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute mean of empty list")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute median of empty list")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    else:
        return (ordered[mid - 1] + ordered[mid]) / 2


def minimum_maximum(values: list[float]) -> tuple[float, float]:
    if not values:
        raise ValueError("Cannot compute min/max of empty list")
    smallest = largest = values[0]
    for value in values[1:]:
        if value < smallest:
            smallest = value
        elif value > largest:
            largest = value
    return smallest, largest       


def verify_with_pandas(path: Path, my_results: dict) -> None:
    """Recompute the headline numbers with pandas and print whether each one matches."""
    df = pd.read_csv(path,dtype=str)

    price = (df["unit_price_kes"].str.upper()
             .str.replace("KES", "", regex=False)
             .str.replace(",", "", regex=False))

    df["price"] = pd.to_numeric(price, errors="coerce")
    df["qty"] = pd.to_numeric(df["quantity"], errors="coerce")

    df = df.dropna(subset=["price", "qty"])
    df["revenue"] = df["price"] * df["qty"]

    pd_total = df["revenue"].sum()
    pd_by_product = df.groupby("product")["revenue"].sum()

    pd_top3 = sorted(pd_by_product.items(), key=lambda x: (-x[1], x[0]))[:3]
    pd_mean = df["revenue"].mean()
    pd_median = df["revenue"].median()  

    def close(a, b):
        return math.isclose(a, b, abs_tol=0.01)

    def status(ok, mine, theirs):
        return "MATCH" if ok else f"MISMATCH (pure={mine}, pandas={theirs})"

    total_ok = close(my_results["total"], pd_total)

    product_ok = (set(my_results["by_product"]) == set(pd_by_product.index)
                  and all(close(v, pd_by_product[k]) for k, v in my_results["by_product"].items()))
    top3_ok = (len(my_results["top3"]) == len(pd_top3)
               and all(a[0] == b[0] and close(a[1], b[1])
                       for a, b in zip(my_results["top3"], pd_top3)))
    stats_ok = close(my_results["mean"], pd_mean) and close(my_results["median"], pd_median)

    print("\n=== pandas verification ===")
    print(f"Total revenue      : {status(total_ok, my_results['total'], pd_total)}")
    print(f"Revenue by product : {status(product_ok, 'see breakdown', 'see groupby')}")
    print(f"Top 3              : {status(top3_ok, my_results['top3'], pd_top3)}")
    print(f"Mean / median      : {status(stats_ok, (my_results['mean'], my_results['median']), (pd_mean, pd_median))}")

    return{"revenue": total_ok, "top3": top3_ok, "mean": stats_ok, "median": stats_ok}


def main():
    rows = read_sales()
    clean, skipped = convert_rows(rows)

    print("=== Sales report: September 2026 ===")
    print(f"Rows read          : {len(rows)}")
    print(f"Rows used          : {len(clean)}")
    skipped_text = ", ".join(f"{s['sale_id']}: {s['reason']}" for s in skipped)
    print(f"Rows skipped       : {len(skipped)}   ({skipped_text})")

    total = total_revenue(clean)
    print(f"\nTotal revenue (KES): {total:,.2f}")

    by_product = revenue_by(clean, "product")
    assert round(sum(by_product.values()), 2) == round(total, 2), "breakdown doesn't add up"
    print("\nRevenue by product (KES)")
    for product, amount in sorted(by_product.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {product:<24} {amount:>12,.2f}")

    print("\nTop 3 products")
    for rank, (product, revenue) in enumerate(top_n(by_product, 3), start=1):
        print(f"  {rank}. {product} - KES {revenue:,.2f}")

    big = high_value(clean, 50_000)
    print(f"\nHigh-value transactions (>= KES 50,000): {len(big)}")
    for r in big:
        print(f"  {r['sale_id']}  {r['sale_date']}  {r['store']}  {r['product']}  KES {r['revenue']:,.2f}")

    per_store = {store: sum(1 for r in big if r["store"] == store)
                 for store in {r["store"] for r in clean}}
    print("\nHigh-value sales per store")
    for store, count in sorted(per_store.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {store:<20} {count}")

    revenues = [r["revenue"] for r in clean]
    low, high = minimum_maximum(revenues)
    print("\nTransaction revenue statistics")
    print(f"  mean   : {mean(revenues):,.2f}")
    print(f"  median : {median(revenues):,.2f}")
    print(f"  min    : {low:,.2f}")
    print(f"  max    : {high:,.2f}")

    my_results = {"total": total, "by_product": by_product, "top3": top_n(by_product, 3),
                  "mean": mean(revenues), "median": median(revenues)}
    verify_with_pandas(DATA_PATH, my_results)


if __name__ == "__main__":
    buffer = io.StringIO()
    with redirect_stdout(buffer):     # capture everything main() prints
        main()
    report = buffer.getvalue()
    print(report, end="")             # show it on screen
    Path("output").mkdir(exist_ok=True)
    Path("output/sales_report.txt").write_text(report, encoding="utf-8")