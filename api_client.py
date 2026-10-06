"""Client for the DummyJSON products API."""

import requests


class InventoryAPIClient:
    """Handles communications with the DummyJSON Products API."""

    def __init__(self, base_url: str = "https://dummyjson.com/products"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def fetch_page(self, limit: int = 30, skip: int = 0) -> dict:
        """Fetch a single page of product data using query parameters."""
        if limit < 0 or skip < 0:
            raise ValueError("limit and skip must be zero or greater")

        response = self.session.get(
            self.base_url,
            params={"limit": limit, "skip": skip},
            timeout=30,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise requests.HTTPError(
                f"Product request failed with status {response.status_code}: {response.reason}"
            ) from exc

        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Product API response must be a JSON object")
        return payload

    def fetch_all_products(self, batch_size: int = 30) -> list[dict]:
        """Paginate through all endpoints until all inventory items are retrieved."""
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        products: list[dict] = []
        skip = 0

        while True:
            page = self.fetch_page(limit=batch_size, skip=skip)
            batch = page.get("products", [])
            if not isinstance(batch, list):
                raise ValueError("Product API response is missing a products list")
            if not batch:
                break

            products.extend(item for item in batch if isinstance(item, dict))

            total = page.get("total")
            skip += batch_size
            if isinstance(total, int) and skip >= total:
                break
            if len(batch) < batch_size:
                break

        return products

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> "InventoryAPIClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
