from __future__ import annotations

from typing import Any

import httpx

from src.core.settings import get_settings, get_yaml_config


class DeFiTools:
    """DeFi data tools with live-source support and stable fallbacks."""

    def __init__(self) -> None:
        settings = get_settings()
        cfg = get_yaml_config()
        tools_cfg = cfg.get("tools", {})
        self._use_mock_data = bool(tools_cfg.get("use_mock_data", settings.use_mock_data))
        self._coingecko_base_url = str(
            tools_cfg.get("coingecko_base_url", settings.coingecko_base_url)
        ).rstrip("/")
        self._defillama_base_url = str(
            tools_cfg.get("defillama_base_url", settings.defillama_base_url)
        ).rstrip("/")
        self._timeout = settings.api_timeout_seconds

        self._symbol_to_coingecko_id: dict[str, str] = {
            "ETH": "ethereum",
            "BTC": "bitcoin",
            "UNI": "uniswap",
            "AAVE": "aave",
            "LDO": "lido-dao",
        }

    def get_token_price(self, symbol: str) -> dict[str, Any]:
        mock_prices = {
            "ETH": 3620.5,
            "BTC": 84200.0,
            "UNI": 10.8,
            "AAVE": 131.2,
            "LDO": 2.1,
        }
        symbol_upper = symbol.upper()

        if not self._use_mock_data:
            coin_id = self._symbol_to_coingecko_id.get(symbol_upper)
            if coin_id:
                try:
                    with httpx.Client(timeout=self._timeout) as client:
                        resp = client.get(
                            f"{self._coingecko_base_url}/simple/price",
                            params={"ids": coin_id, "vs_currencies": "usd"},
                        )
                        resp.raise_for_status()
                        payload = resp.json()
                    price = float(payload.get(coin_id, {}).get("usd", 0.0))
                    return {
                        "symbol": symbol_upper,
                        "price_usd": price,
                        "source": "coingecko",
                    }
                except Exception:
                    pass

        return {
            "symbol": symbol_upper,
            "price_usd": mock_prices.get(symbol_upper, 0.0),
            "source": "mock-price-feed",
        }

    def get_protocol_tvl(self, protocol: str) -> dict[str, Any]:
        mock_tvl = {
            "uniswap": 5200000000,
            "aave": 11000000000,
            "lido": 26500000000,
        }
        key = protocol.lower()

        if not self._use_mock_data:
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.get(f"{self._defillama_base_url}/protocols")
                    resp.raise_for_status()
                    payload = resp.json()

                matched = next(
                    (item for item in payload if str(item.get("slug", "")).lower() == key),
                    None,
                )
                if matched:
                    return {
                        "protocol": protocol,
                        "tvl_usd": float(matched.get("tvl") or 0),
                        "source": "defillama",
                    }
            except Exception:
                pass

        return {
            "protocol": protocol,
            "tvl_usd": mock_tvl.get(key, 0),
            "source": "mock-defillama",
        }

    def risk_analysis(self, protocol: str) -> dict[str, Any]:
        key = protocol.lower()
        risk_map = {
            "uniswap": "medium",
            "aave": "medium",
            "lido": "medium-high",
        }
        level = risk_map.get(key, "unknown")
        factors = [
            "smart contract risk",
            "oracle risk",
            "liquidity risk",
            "governance risk",
        ]
        return {
            "protocol": protocol,
            "risk_level": level,
            "factors": factors,
            "source": "mock-risk-engine",
        }
