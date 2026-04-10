from __future__ import annotations

from typing import Any

import httpx

from src.tools.defi_tools import DeFiTools


class _FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


class _FakeClient:
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN003
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
        return False

    def get(self, url: str, params: dict[str, Any] | None = None):
        if "simple/price" in url:
            coin_id = params["ids"] if params else "ethereum"
            return _FakeResponse({coin_id: {"usd": 123.45}})
        if "/protocols" in url:
            return _FakeResponse([{"slug": "uniswap", "tvl": 987654321.0}])
        return _FakeResponse({})


def test_live_price_and_tvl_when_available(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "Client", _FakeClient)

    tools = DeFiTools()
    tools._use_mock_data = False

    price = tools.get_token_price("ETH")
    tvl = tools.get_protocol_tvl("uniswap")

    assert price["source"] == "coingecko"
    assert price["price_usd"] == 123.45
    assert tvl["source"] == "defillama"
    assert tvl["tvl_usd"] == 987654321.0


def test_live_source_failure_falls_back_to_mock(monkeypatch) -> None:
    class _ErrorClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN003
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
            return False

        def get(self, url: str, params: dict[str, Any] | None = None):
            raise httpx.ConnectError("boom")

    monkeypatch.setattr(httpx, "Client", _ErrorClient)

    tools = DeFiTools()
    tools._use_mock_data = False

    price = tools.get_token_price("ETH")
    tvl = tools.get_protocol_tvl("uniswap")

    assert price["source"] == "mock-price-feed"
    assert tvl["source"] == "mock-defillama"
