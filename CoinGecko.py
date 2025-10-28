import requests
from typing import Dict, Any, Optional

class CoinGeckoToken:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, token_id: str = "push-protocol"):
        self.token_id = token_id

    def get_token_data(self) -> Dict[str, Any]:
        """Get real token data from CoinGecko API"""
        try:
            url = f"{self.BASE_URL}/coins/{self.token_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "symbol": data.get("symbol"),
                    "name": data.get("name"),
                    "current_price": data.get("market_data", {}).get("current_price", {}).get("usd", 0),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd", 0),
                    "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd", 0),
                    "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h", 0),
                    "market_cap_rank": data.get("market_cap_rank"),
                    "description": data.get("description", {}).get("en", "")
                }
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_token_tickers(self) -> Dict[str, Any]:
        """Get real ticker data from CoinGecko"""
        try:
            url = f"{self.BASE_URL}/coins/{self.token_id}/tickers"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                tickers = []
                
                for ticker in data.get("tickers", [])[:10]:  # Limit to top 10
                    tickers.append({
                        "base": ticker.get("base"),
                        "target": ticker.get("target"),
                        "market": ticker.get("market", {}).get("name"),
                        "last": ticker.get("last"),
                        "volume": ticker.get("volume"),
                        "trust_score": ticker.get("trust_score")
                    })
                
                return {"tickers": tickers}
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_price_history(self, days: int = 7) -> Dict[str, Any]:
        """Get price history for the token"""
        try:
            url = f"{self.BASE_URL}/coins/{self.token_id}/market_chart"
            params = {"vs_currency": "usd", "days": days}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "prices": data.get("prices", []),
                    "market_caps": data.get("market_caps", []),
                    "total_volumes": data.get("total_volumes", [])
                }
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
