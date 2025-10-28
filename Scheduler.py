from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import os
from web3 import Web3
from eth_account import Account
import json

# Configure job store and scheduler
jobstores = {
    'default': MongoDBJobStore(host=os.getenv("MONGO_URI", "localhost"), port=27017)
}
executors = {
    'default': ThreadPoolExecutor(20)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(
    jobstores=jobstores, 
    executors=executors, 
    job_defaults=job_defaults
)
scheduler.start()

# Push Chain configuration
PUSH_RPC = "https://evm.rpc-testnet-donut-node2.push.org/"
w3 = Web3(Web3.HTTPProvider(PUSH_RPC))

execution_log = []

def execute_pc_transfer(to_address: str, amount: float, private_key: str, from_address: str):
    """Execute PC token transfer on Push Chain"""
    try:
        account = Account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(from_address)
        
        transaction = {
            'to': to_address,
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
            'chainId': 42101  # Push Chain testnet
        }
        
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        log_entry = {
            "type": "pc_transfer",
            "to": to_address,
            "amount": amount,
            "tx_hash": tx_hash.hex(),
            "executed_at": datetime.now().isoformat(),
            "status": "success"
        }
        execution_log.append(log_entry)
        
        print(f"✅ Executed: {amount} PC to {to_address} | TX: {tx_hash.hex()}")
        return tx_hash.hex()
        
    except Exception as e:
        log_entry = {
            "type": "pc_transfer",
            "to": to_address,
            "amount": amount,
            "error": str(e),
            "executed_at": datetime.now().isoformat(),
            "status": "failed"
        }
        execution_log.append(log_entry)
        print(f"❌ Transfer failed: {str(e)}")
        return None

def schedule_pc_transfer(to_address: str, amount: float, run_at: datetime, private_key: str, from_address: str) -> str:
    """Schedule a PC transfer at specified datetime"""
    try:
        if run_at <= datetime.now():
            return "❌ Scheduled time must be in the future"
        
        job = scheduler.add_job(
            execute_pc_transfer,
            'date',
            run_date=run_at,
            args=[to_address, amount, private_key, from_address],
            id=f"pc_transfer_{datetime.now().timestamp()}",
            replace_existing=True
        )
        
        return f"✅ Scheduled {amount} PC to {to_address} on {run_at.strftime('%Y-%m-%d %H:%M:%S')}"
        
    except Exception as e:
        return f"❌ Scheduling failed: {str(e)}"

def schedule_recurring_payment(to_address: str, amount: float, interval: str, private_key: str, from_address: str) -> str:
    """Schedule recurring PC payments"""
    try:
        # Parse interval (daily, weekly, monthly)
        if interval.lower() == "daily":
            job = scheduler.add_job(
                execute_pc_transfer,
                'interval',
                days=1,
                args=[to_address, amount, private_key, from_address],
                id=f"recurring_daily_{to_address}_{datetime.now().timestamp()}"
            )
        elif interval.lower() == "weekly":
            job = scheduler.add_job(
                execute_pc_transfer,
                'interval',
                weeks=1,
                args=[to_address, amount, private_key, from_address],
                id=f"recurring_weekly_{to_address}_{datetime.now().timestamp()}"
            )
        elif interval.lower() == "monthly":
            job = scheduler.add_job(
                execute_pc_transfer,
                'cron',
                day=1,  # First day of each month
                hour=9,
                args=[to_address, amount, private_key, from_address],
                id=f"recurring_monthly_{to_address}_{datetime.now().timestamp()}"
            )
        else:
            return f"❌ Invalid interval. Use: daily, weekly, or monthly"
        
        return f"✅ Set up {interval} payment of {amount} PC to {to_address}"
        
    except Exception as e:
        return f"❌ Recurring payment setup failed: {str(e)}"

def list_scheduled_jobs() -> list:
    """List all active scheduled jobs"""
    jobs = scheduler.get_jobs()
    job_list = []
    
    for job in jobs:
        job_info = {
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else "N/A",
            "trigger": str(job.trigger),
            "function": job.func.__name__
        }
        job_list.append(job_info)
    
    return job_list

def cancel_job(job_id: str) -> str:
    """Cancel a scheduled job"""
    try:
        scheduler.remove_job(job_id)
        return f"✅ Cancelled job: {job_id}"
    except Exception as e:
        return f"❌ Failed to cancel job: {str(e)}"

def get_execution_log() -> list:
    """Get history of executed payments"""
    return execution_log