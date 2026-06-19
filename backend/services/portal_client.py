from typing import Optional
import httpx
import asyncio
from config import settings
from services.auth import auth_service

# Confirmed working endpoints (via reverse engineering):
# POST /workorders/buscador           → list orders (with lazyEvent pagination)
# GET  /workorders/masters            → master data (statuses, workgroups, etc.)
# GET  /workorders/item/boletin/{id}  → order detail + task fields + photos (base64)
# GET  /workorders/item/history/{id}  → order change history
# GET  /workorders/buscador/columns   → available column definitions


async def _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    headers = await auth_service.get_headers()
    kwargs.setdefault("headers", {}).update(headers)

    last_exc = None
    for attempt in range(settings.request_retries):
        try:
            async with httpx.AsyncClient(verify=False, timeout=settings.request_timeout) as client:
                resp = await client.request(method, url, **kwargs)
                if resp.status_code == 401:
                    await auth_service.authenticate()
                    new_headers = await auth_service.get_headers()
                    kwargs["headers"].update(new_headers)
                    continue
                return resp
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_exc = e
            if attempt < settings.request_retries - 1:
                await asyncio.sleep(2 ** attempt)

    raise last_exc or Exception("Max retries exceeded")


class PortalClient:
    BASE = settings.portal_api_url

    async def get_masters(self) -> dict:
        resp = await _request_with_retry("GET", f"{self.BASE}/workorders/masters")
        return resp.json() or {} if resp.status_code == 200 else {}

    async def get_orders(self, first: int = 0, rows: int = 100, filters: dict = None) -> dict:
        """POST /workorders/buscador — returns {items, totalRecords, totales}"""
        payload = {
            "params": {
                "lazyEvent": {
                    "first": first,
                    "rows": rows,
                    "sortField": None,
                    "sortOrder": None,
                    "filters": filters or {},
                }
            },
            "selectedColumns": [],
            "globalFilterFields": [],
            "zonaHoraria": "Europe/Berlin",
        }
        resp = await _request_with_retry("POST", f"{self.BASE}/workorders/buscador", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                return {
                    "items": data.get("items", []),
                    "total": data.get("totalRecords", 0),
                    "totales": data.get("totales"),
                }
        return {"items": [], "total": 0, "totales": None}

    async def get_order_boletin(self, order_id: int) -> dict:
        """GET /workorders/item/boletin/{id} — returns detail + photos as base64"""
        resp = await _request_with_retry("GET", f"{self.BASE}/workorders/item/boletin/{order_id}")
        return resp.json() if resp.status_code == 200 else {}

    async def get_order_history(self, order_id: int) -> list:
        """GET /workorders/item/history/{id} — returns list of history records"""
        resp = await _request_with_retry("GET", f"{self.BASE}/workorders/item/history/{order_id}")
        if resp.status_code == 200:
            data = resp.json()
            return data if isinstance(data, list) else []
        return []

    async def get_columns(self) -> dict:
        """GET /workorders/buscador/columns — returns column definitions"""
        resp = await _request_with_retry("GET", f"{self.BASE}/workorders/buscador/columns")
        return resp.json() if resp.status_code == 200 else {}

    async def get_custom_filters(self) -> list:
        """GET /workorders/buscador/customFilters"""
        resp = await _request_with_retry("GET", f"{self.BASE}/workorders/buscador/customFilters")
        if resp.status_code == 200:
            data = resp.json()
            return data if isinstance(data, list) else []
        return []


portal_client = PortalClient()
