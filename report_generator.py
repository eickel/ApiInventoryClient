"""Turn DummyJSON product payloads into inventory reports."""

import json
from pathlib import Path

import pandas as pd


REPORT_COLUMNS = [
    "id",
    "title",
    "brand",
    "category",
    "price",
    "discountPercentage",
    "discounted_price",
    "stock",
    "low_stock_warning",
]


class InventoryReportGenerator:
    """Transforms raw product API data into structured business reports."""

    def __init__(self, raw_data: list[dict]):
        self.raw_data = pd.DataFrame(raw_data)
        self.report: pd.DataFrame | None = None

    def process_inventory(self, low_stock_threshold: int = 10) -> pd.DataFrame:
        """Calculate discounted prices and identify low-stock items."""
        frame = self.raw_data.copy()
        required = ["price", "discountPercentage", "stock"]
        missing = [column for column in required if column not in frame.columns]
        if missing and not frame.empty:
            raise ValueError(
                "Product data is missing required fields: " + ", ".join(missing)
            )

        if frame.empty:
            self.report = pd.DataFrame(columns=REPORT_COLUMNS)
            return self.report.copy()

        if "brand" not in frame.columns:
            frame["brand"] = pd.NA

        frame["discounted_price"] = (
            frame["price"] * (1 - frame["discountPercentage"] / 100)
        ).round(2)
        frame["low_stock_warning"] = frame["stock"] < low_stock_threshold

        self.report = frame.loc[:, REPORT_COLUMNS].reset_index(drop=True)
        return self.report.copy()

    def export_csv(self, destination: str | Path) -> None:
        """Export the processed DataFrame to CSV format."""
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._processed_report().to_csv(path, index=False)

    def export_summary_metrics(self, destination: str | Path) -> None:
        """Export high-level metrics (total inventory value, item count) as JSON."""
        report = self._processed_report()
        inventory_value = (report["discounted_price"] * report["stock"]).sum()
        summary = {
            "item_count": int(len(report)),
            "total_inventory_value": round(float(inventory_value), 2),
            "low_stock_item_count": int(report["low_stock_warning"].sum()),
        }

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    def _processed_report(self) -> pd.DataFrame:
        if self.report is None:
            raise RuntimeError("Call process_inventory() before exporting a report")
        return self.report
