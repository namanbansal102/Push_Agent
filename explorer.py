import requests
from typing import List, Dict, Optional
from datetime import datetime
import json

PUSH_CHAIN_API_BASE = "https://donut.push.network/api/v2"

def get_transactions(address: str, limit: int = 10) -> List[Dict]:
    """Get real transactions for an address on Push Chain"""
    try:
        url = f"{PUSH_CHAIN_API_BASE}/addresses/{address}/transactions"
        params = {"limit": limit}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            return [{"error": f"API error: {response.status_code}"}]
    except Exception as e:
        return [{"error": str(e)}]

def get_block_data(block_number: Optional[int] = None) -> Dict:
    """Get block information from Push Chain"""
    try:
        if block_number:
            url = f"{PUSH_CHAIN_API_BASE}/blocks/{block_number}"
        else:
            url = f"{PUSH_CHAIN_API_BASE}/blocks"
            
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_latest_blocks(limit: int = 10) -> List[Dict]:
    """Get latest blocks from Push Chain"""
    try:
        url = f"{PUSH_CHAIN_API_BASE}/blocks"
        params = {"limit": limit}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            return [{"error": f"API error: {response.status_code}"}]
    except Exception as e:
        return [{"error": str(e)}]

def get_token_transfers(token_address: str, limit: int = 20) -> List[Dict]:
    """Get token transfer events"""
    try:
        url = f"{PUSH_CHAIN_API_BASE}/tokens/{token_address}/transfers"
        params = {"limit": limit}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            return [{"error": f"API error: {response.status_code}"}]
    except Exception as e:
        return [{"error": str(e)}]

def get_token_holders(token_address: str, limit: int = 50) -> List[Dict]:
    """Get token holders for a specific token"""
    try:
        url = f"{PUSH_CHAIN_API_BASE}/tokens/{token_address}/holders"
        params = {"limit": limit}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            return [{"error": f"API error: {response.status_code}"}]
    except Exception as e:
        return [{"error": str(e)}]

def get_address_balance(address: str) -> Dict:
    """Get PC balance and token balances for address"""
    try:
        url = f"{PUSH_CHAIN_API_BASE}/addresses/{address}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_market_chart_data(days: int = 7) -> Dict:
    """Get Push Chain market data"""
    try:
        # This would integrate with Push Chain's market data API
        url = f"{PUSH_CHAIN_API_BASE}/stats/charts/transactions"
        params = {"period": f"{days}d"}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def search_transactions(query: str) -> List[Dict]:
    """Search for transactions by hash, address, or block"""
    try:
        url = f"{PUSH_CHAIN_API_BASE}/search"
        params = {"q": query}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            return [{"error": f"API error: {response.status_code}"}]
    except Exception as e:
        return [{"error": str(e)}]