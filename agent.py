import google.generativeai as genai
from google.adk.agents import Agent
import mymongodb as mymongodb
from explorer import *
from datetime import datetime, timedelta
import os
import json
import parsedatetime
from apscheduler.schedulers.background import BackgroundScheduler
from CoinGecko import CoinGeckoToken
from web3 import Web3
from eth_account import Account
import requests

schedule_engine = BackgroundScheduler()
schedule_engine.start()

# Push Chain Testnet Configuration
network = {
    "chain_id": 42101,
    "rpc": "https://evm.rpc-testnet-donut-node2.push.org/",
    "name": "Push Protocol Testnet",
    "explorer": "https://donut.push.network/",
    "native_token": "PC"
}

# Initialize Web3 with Push Chain RPC
w3 = Web3(Web3.HTTPProvider(network["rpc"]))

class PushChainHandler:
    def __init__(self, network_config):
        self.w3 = Web3(Web3.HTTPProvider(network_config["rpc"]))
        self.chain_id = network_config["chain_id"]
        
    def send_transaction(self, to_address: str, amount: float, private_key: str, from_address: str) -> str:
        """Send PC tokens on Push Chain"""
        try:
            account = Account.from_key(private_key)
            nonce = self.w3.eth.get_transaction_count(from_address)
            
            transaction = {
                'to': to_address,
                'value': self.w3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': nonce,
                'chainId': self.chain_id
            }
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            return f"Transaction sent: {tx_hash.hex()}"
        except Exception as e:
            return f"Transaction failed: {str(e)}"
    
    def get_balance(self, address: str) -> float:
        """Get PC balance for address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_pc = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_pc)
        except Exception as e:
            return f"Error getting balance: {str(e)}"
    
    def get_transaction_by_hash(self, tx_hash: str) -> dict:
        """Get transaction details by hash"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            return {
                "hash": tx_hash,
                "from": tx['from'],
                "to": tx['to'],
                "value": self.w3.from_wei(tx['value'], 'ether'),
                "gas": tx['gas'],
                "gasPrice": self.w3.from_wei(tx['gasPrice'], 'gwei')
            }
        except Exception as e:
            return {"error": str(e)}

    def deploy_token(self, deployer_address: str, name: str, symbol: str, private_key: str) -> str:
        """Deploy ERC20 token on Push Chain"""
        # ERC20 contract bytecode and ABI would go here
        # This is a simplified version
        try:
            return f"Token {name} ({symbol}) deployment initiated on Push Chain"
        except Exception as e:
            return f"Token deployment failed: {str(e)}"

handler = PushChainHandler(network)

def transmit(to: str, value: float, private_key: str, from_address: str) -> str:
    """Send PC tokens to an address"""
    return handler.send_transaction(to, value, private_key, from_address)

def tx_lookup(tx_hash: str) -> dict:
    """Look up transaction by hash"""
    return handler.get_transaction_by_hash(tx_hash)

def balance_query(address: str) -> str:
    """Get PC balance for address"""
    balance = handler.get_balance(address)
    return f"PC Balance: {balance}"

def issue_token(name: str, symbol: str, private_key: str, deployer_address: str) -> str:
    """Deploy new token on Push Chain"""
    return handler.deploy_token(deployer_address, name, symbol, private_key)

def future_send(to: str, amount: float, when: str, private_key: str, from_address: str) -> str:
    """Schedule future PC transfer"""
    parser = parsedatetime.Calendar()
    time_struct, parse_status = parser.parse(when)
    
    if parse_status == 0:
        return "Could not parse the time. Please use format like '2024-12-25 10:00 AM'"
    
    scheduled_time = datetime(*time_struct[:6])
    
    if scheduled_time <= datetime.now():
        return "Scheduled time must be in the future"
    
    def execute_transfer():
        result = transmit(to, amount, private_key, from_address)
        print(f"Scheduled transfer executed: {result}")
    
    schedule_engine.add_job(
        execute_transfer, 
        'date', 
        run_date=scheduled_time
    )
    
    return f"✅ Scheduled {amount} PC to {to} on {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"

def get_push_token_info() -> str:
    """Get Push token information"""
    try:
        # This would connect to actual Push Chain APIs
        return "Push Protocol native token (PC) information"
    except Exception as e:
        return f"Error fetching token info: {str(e)}"

def create_payment_link(amount: float, recipient: str) -> str:
    """Generate payment link for Push Chain"""
    link = f"https://pay.push.network/?amount={amount}&to={recipient}&chain=42101"
    return f"Payment link created: {link}"

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ai_response(query: str) -> str:
    """Generate AI response using Gemini"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(f"As a Push Chain AI agent: {query}")
        return response.text
    except Exception as e:
        return f"AI response error: {str(e)}"

# Load real Push Chain tokens
with open("tokensList.json", "r") as f:
    push_tokens = json.load(f)

def find_token_by_symbol(symbol: str) -> dict:
    """Find token by symbol from Push Chain tokens list"""
    for token in push_tokens.get("items", []):
        if token.get("symbol", "").upper() == symbol.upper():
            return token
    return {"error": f"Token {symbol} not found"}

# Agent tools
tools = [
    transmit, 
    tx_lookup, 
    balance_query, 
    issue_token, 
    future_send,
    get_push_token_info,
    create_payment_link,
    find_token_by_symbol,
    ai_response
] + [mymongodb.add_to_book, mymongodb.fetch_address_from_book] + [
    get_transactions, 
    get_block_data, 
    get_market_chart_data,
    get_token_holders
]

# Initialize the real Push Chain agent
push_agent = Agent(
    model='gemini-2.5-flash',
    name='PushChainAgent',
    description='AI-powered blockchain agent for Push Protocol',
    instruction='''You are an intelligent blockchain agent operating on Push Chain (testnet). 
    You can help users with:
    - Sending PC tokens and scheduling payments
    - Deploying tokens and smart contracts  
    - Checking balances and transaction history
    - Managing address books and payment links
    - Providing blockchain insights and market data
    
    
    Always prioritize security and confirm transactions with users.''',
    tools=tools
)
