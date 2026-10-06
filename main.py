"""Fetch DummyJSON inventory and write the business reports."""

from pathlib import Path

from api_client import InventoryAPIClient
from report_generator import InventoryReportGenerator


def main() -> None:
    output_dir = Path("reports")

    with InventoryAPIClient() as client:
        products = client.fetch_all_products(batch_size=30)

    generator = InventoryReportGenerator(products)
    report = generator.process_inventory(low_stock_threshold=10)
    csv_path = output_dir / "inventory_report.csv"
    summary_path = output_dir / "inventory_summary.json"
    generator.export_csv(csv_path)
    generator.export_summary_metrics(summary_path)

    low_stock = int(report["low_stock_warning"].sum())
    print(f"Retrieved {len(products)} products.")
    print(f"Low-stock items: {low_stock}.")
    print(f"Wrote {csv_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
