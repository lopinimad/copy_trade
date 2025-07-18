import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Callable
from functools import wraps
import threading # Added import
import re
import pandas as pd



from pyquotex.expiration import (
    timestamp_to_date,
    get_timestamp_days_ago
)
from pyquotex.utils.processor import (
    process_candles,
    get_color,
    aggregate_candle
)
from pyquotex.config import credentials
from pyquotex.stable_api import Quotex

__author__ = "Cleiton Leonel Creton"
__version__ = "1.0.3"

#USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pyquotex/pyquotex.log')
    ]
)
logger = logging.getLogger(__name__)

def read_trades_from_log(file_path: str = "orders.log") -> List[Dict[str, Any]]:
    """Reads trade orders from the log file."""
    trades = []
    log_file = Path(file_path)
    if not log_file.is_file():
        logger.warning(f"Log file not found: {file_path}")
        return trades

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(
                r"Stamp: (\d+\.?\d*)\s+ID: (\d+\.?\d*)\s+Asset: ([\w-]+)\s+Amount: (\d+\.?\d*)\s+Direction: (\w+)\s+Duration: (\d+\.?\d*)",
                line,
            )
            #print(match)
            if match:
                stamp, id, asset, amount, direction, duration = match.groups()
                trades.append({
                    'stamp': int(stamp),
                    'trade_id': int(id),
                    'amount': float(amount),
                    'asset': asset,
                    'direction': direction.lower(),
                    'duration': int(float(duration))
                })
    #print(trades)
    return trades

def ensure_connection(max_attempts: int = 5):
    """Decorator to ensure connection before executing function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.client:
                logger.error("Quotex API client not initialized.")
                raise RuntimeError("Quotex API client not initialized.")
 
            # Connect if not already connected
            if not await self.client.check_connect():
                logger.info("Establishing connection...")
                check, reason = await self._connect_with_retry(max_attempts)
 
                if not check:
                    logger.error(f"Failed to connect after multiple attempts: {reason}")
                    raise ConnectionError(f"Failed to connect: {reason}")
 
            logger.debug("Connection is active. Proceeding with operation.")
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


class PyQuotexCLI:
    """PyQuotex CLI application for trading operations."""

    def __init__(self):
        self.client: Optional[Quotex] = None
        self.setup_client()

    def setup_client(self):
        """Initializes the Quotex API client with credentials."""
        try:
            email, password = credentials()
            self.client = Quotex(
                email=email,
                password=password,
                lang="en"
            )
            logger.info("Quotex client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Quotex client: {e}")
            raise

    async def _connect_with_retry(self, attempts: int = 5) -> Tuple[bool, str]:
        """Internal method to attempt connection with retry logic."""
        
        logger.info("Attempting to connect to Quotex API...")
        check, reason = await self.client.connect()

        if not check:
            for attempt_num in range(1, attempts + 1):
                logger.warning(f"Connection failed. Attempt {attempt_num} of {attempts}.")

                session_file = Path("settings/session.json")
                if session_file.exists():
                    session_file.unlink()
                    logger.debug("Obsolete session file removed.")

                await asyncio.sleep(2)
                check, reason = await self.client.connect()

                if check:
                    logger.info("Reconnected successfully!")
                    break

            if not check:
                logger.error(f"Failed to connect after {attempts} attempts: {reason}")
                return False, reason

        logger.info(f"Connected successfully: {reason}")
        return check, reason

    

    @ensure_connection()
    async def test_connection(self) -> None:
        """Tests the connection to the Quotex API."""
        logger.info("Running connection test.")
        is_connected = await self.client.check_connect()

        if is_connected:
            logger.info("Connection test successful.")
            print("✅ Connection successful!")
        else:
            logger.error("Connection test failed.")
            print("❌ Connection failed!")

    @ensure_connection()
    async def get_balance(self) -> None:
        """Gets the current account balance (practice by default)."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info("Getting account balance.")
        #self.client.change_account("PRACTICE")
        balance = await self.client.get_balance()
        logger.info(f"Current balance: {balance}")
        return str(Timen)+ f" 💰 Current Balance: R$ {balance:.2f}"

    @ensure_connection()
    async def change_account(self,account_type: str = "PRACTICE") -> None:
        """Gets the current account balance (practice by default)."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        #logger.info("Getting account balance.")
        self.client.change_account(account_type)
        #logger.info(f"Current balance: {balance}")
        print(str(Timen)+ f" 💰 Account Changed To {account_type}")

    @ensure_connection()
    async def get_profile(self) -> None:
        """Gets user profile information."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info("Getting user profile.")

        profile = await self.client.get_profile()

        description = (
            "\n" + str(Timen) + f" 👤 User Profile:\n"
            + str(Timen) + f" Name: {profile.nick_name}\n"
            + str(Timen) + f" Email: {profile.email}\n"
            + str(Timen) + f" Country: {profile.country_name}\n"
            + str(Timen) + f" Avatar: {profile.avatar}\n"
            + str(Timen) + f" ID: {profile.profile_id}\n"
            + str(Timen) + f" Demo Balance: R$ {profile.demo_balance:.2f}\n"
            + str(Timen) + f" Live Balance: R$ {profile.live_balance:.2f}\n"
            + str(Timen) + f" Time Zone: {profile.offset}\n"
        )
        logger.info("Profile retrieved successfully.")
        print(description)

    @ensure_connection()
    async def buy_simple(self, stamp: int = 0, trade_id: int = 0, amount: float = 50, asset: str = None,
                         direction: str = "call", duration: int = 60) -> None:
        """Executes a simple buy operation."""
        logger.info(f"Executing simple buy: {amount} on {asset} in {direction} direction for {duration}s.")
        """
        self.client.change_account("PRACTICE")
        asset_name, asset_data = await self.client.get_available_asset(asset, force_open=True)
        
        if not asset_data or len(asset_data) < 3 or not asset_data[2]:
            logger.error(f"Asset {asset} is closed or invalid.")
            print(f"❌ ERROR: Asset {asset} is closed or invalid.")
            return

        logger.info(f"Asset {asset} is open.")
        """
        status, buy_info = await self.client.buy(
            amount, asset, direction, duration, time_mode="TIMER"
        )
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        if status:
            logger.info(f"Buy successful: {buy_info}")
            print(str(Timen)+ f" ✅ Buy executed successfully!")
            print(str(Timen)+ f" Amount: R$ {amount:.2f}")
            print(str(Timen)+ f" Asset: {asset}")
            print(str(Timen)+ f" Direction: {direction.upper()}")
            print(str(Timen)+ f" Duration: {duration}s")
            print(str(Timen)+ f" Order ID: {buy_info.get('id', 'N/A')}")
        else:
            logger.error(f"Buy failed: {buy_info}")
            print(str(Timen)+ f" ❌ Buy failed: {buy_info}")

        balance = await self.client.get_balance()
        logger.info(f"Current balance: {balance}")
        #print(f"💰 Current Balance: R$ {balance:.2f}")

    @ensure_connection()
    async def buy_and_check_win(self, amount: float = 50, asset: str = "EURUSD_otc",
                                direction: str = "put", duration: int = 60) -> None:
        """Executes a buy operation and checks if it was a win or loss."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info(
            f"Executing buy and checking result: {amount} on {asset} in {direction} direction for {duration}s.")

        await self.client.change_account("PRACTICE")
        balance_before = await self.client.get_balance()
        logger.info(f"Balance before trade: {balance_before}")
        print(str(Timen)+ f" 💰 Balance Before: R$ {balance_before:.2f}")

        asset_name, asset_data = await self.client.get_available_asset(asset, force_open=True)

        if not asset_data or len(asset_data) < 3 or not asset_data[2]:
            logger.error(f"Asset {asset} is closed or invalid.")
            print(str(Timen)+ f" ❌ ERROR: Asset {asset} is closed or invalid.")
            return

        logger.info(f"Asset {asset} is open.")
        status, buy_info = await self.client.buy(amount, asset_name, direction, duration,
                                                 time_mode="TIMER")

        if not status:
            logger.error(f"Buy operation failed: {buy_info}")
            print(str(Timen)+ f" ❌ Buy operation failed! Details: {buy_info}")
            return

        print(f"📊 Trade executed (ID: {buy_info.get('id', 'N/A')}), waiting for result...")
        logger.info(f"Waiting for trade result ID: {buy_info.get('id', 'N/A')}...")

        if await self.client.check_win(buy_info["id"]):
            profit = self.client.get_profit()
            logger.info(f"WIN! Profit: {profit}")
            print(str(Timen)+ f" 🎉 WIN! Profit: R$ {profit:.2f}")
        else:
            loss = self.client.get_profit()
            logger.info(f"LOSS! Loss: {loss}")
            print(str(Timen)+ f" 💔 LOSS! Loss: R$ {loss:.2f}")

        balance_after = await self.client.get_balance()
        logger.info(f"Balance after trade: {balance_after}")
        print(str(Timen)+ f" 💰 Current Balance: R$ {balance_after:.2f}")

    @ensure_connection()
    async def get_candles(self, asset: str = "CHFJPY_otc", period: int = 60,
                          offset: int = 3600) -> None:
        """Gets historical candle data (candlesticks)."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info(f"Getting candles for {asset} with period of {period}s.")

        end_from_time = time.time()
        candles = await self.client.get_candles(asset, end_from_time, offset, period)

        if not candles:
            logger.warning("No candles found for the specified asset.")
            print(str(Timen)+ " ⚠️ No candles found for the specified asset.")
            return

        if not candles[0].get("open"):
            candles = process_candles(candles, period)

        candles_color = []
        if len(candles) > 0:
            candles_color = [get_color(candle) for candle in candles if 'open' in candle and 'close' in candle]
        else:
            logger.warning("Not enough candle data to determine colors.")

        logger.info(f"Retrieved {len(candles)} candles.")

        print(str(Timen)+ f" 📈 Candles (Candlesticks) for {asset} (Period: {period}s):")
        print(str(Timen)+ f" Total candles: {len(candles)}")
        if candles_color:
            print(str(Timen)+ f" Colors of last 10 candles: {' '.join(candles_color[-10:])}")
        else:
            print(str(Timen)+ "   Candle colors not available.")

        print(str(Timen)+ f"   Last 5 candles:")
        for i, candle in enumerate(candles[-5:]):
            color = candles_color[-(5 - i)] if candles_color and (5 - i) <= len(candles_color) else "N/A"
            emoji = "🟢" if color == "green" else ("🔴" if color == "red" else "⚪")
            print(
                str(Timen)+ f" {emoji} Open: {candle.get('open', 'N/A'):.4f} → Close: {candle.get('close', 'N/A'):.4f} (Time: {time.strftime('%H:%M:%S', time.localtime(candle.get('time', 0)))})")

    @ensure_connection()
    async def get_assets_status(self) -> None:
        """Gets the status of all available assets (open/closed)."""
        logger.info("Getting assets status.")
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")

        print("\n📊 Assets Status:")
        open_count = 0
        closed_count = 0

        all_assets = self.client.get_all_asset_name()
        if not all_assets:
            logger.warning("Could not retrieve assets list.")
            print(str(Timen)+ " ⚠️ Could not retrieve assets list.")
            return

        for asset_info in all_assets:
            asset_symbol = asset_info[0]
            asset_display_name = asset_info[1]

            _, asset_open_data = await self.client.check_asset_open(asset_symbol)

            is_open = False
            if asset_open_data and len(asset_open_data) > 2:
                is_open = asset_open_data[2]

            status_text = "OPEN" if is_open else "CLOSED"
            emoji = "🟢" if is_open else "🔴"

            print(f"{emoji} {asset_display_name} ({asset_symbol}): {status_text}")

            if is_open:
                open_count += 1
            else:
                closed_count += 1

            logger.debug(f"Asset {asset_symbol}: {status_text}")

        print(str(Timen)+ f" 📈 Summary: {open_count} open assets, {closed_count} closed assets.")

    @ensure_connection()
    async def get_payment_info(self) -> None:
        """Gets payment information (payout) for all assets."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info("Getting payment information.")

        all_data = self.client.get_payment()
        if not all_data:
            logger.warning("No payment information found.")
            print(str(Timen)+ " ⚠️ No payment information found.")
            return

        print(str(Timen)+ " 💰 Payment Information (Payout):")
        print("-" * 50)

        for asset_name, asset_data in list(all_data.items())[:10]:
            profit_1m = asset_data.get("profit", {}).get("1M", "N/A")
            profit_5m = asset_data.get("profit", {}).get("5M", "N/A")
            is_open = asset_data.get("open", False)

            status_text = "OPEN" if is_open else "CLOSED"
            emoji = "🟢" if is_open else "🔴"

            print(str(Timen)+ f" {emoji} {asset_name} - {status_text}")
            print(str(Timen)+ f" 1M Profit: {profit_1m}% | 5M Profit: {profit_5m}%")
            print("-" * 50)

    @ensure_connection()
    async def balance_refill(self, amount: float = 5000) -> None:
        """Refills the practice account balance."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info(f"Refilling practice account balance with R$ {amount:.2f}.")

        await self.client.change_account("PRACTICE")
        result = await self.client.edit_practice_balance(amount)

        if result:
            logger.info(f"Balance refill successful: {result}")
            print(str(Timen)+ f" ✅ Practice account balance refilled to R$ {amount:.2f} successfully!")
        else:
            logger.error("Balance refill failed.")
            print(str(Timen)+ " ❌ Practice account balance refill failed.")

        new_balance = await self.client.get_balance()
        print(str(Timen)+ f" 💰 New Balance: R$ {new_balance:.2f}")

    @ensure_connection()
    async def get_realtime_price(self, asset: str = "EURJPY_otc") -> None:
        """Monitors the real-time price of an asset."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info(f"Getting real-time price for {asset}.")

        asset_name, asset_data = await self.client.get_available_asset(asset, force_open=True)

        if not asset_data or len(asset_data) < 3 or not asset_data[2]:
            logger.error(f"Asset {asset} is closed or invalid for real-time monitoring.")
            print(str(Timen)+ f" ❌ ERROR: Asset {asset} is closed or invalid for monitoring.")
            return

        logger.info(f"Asset {asset} is open. Starting real-time price monitoring.")
        await self.client.start_realtime_price(asset, 60)

        print(str(Timen)+ f" 📊 Monitoring real-time price for {asset}")
        print(str(Timen)+ " Press Ctrl+C to stop monitoring...")
        print("-" * 60)

        try:
            while True:
                candle_price_data = await self.client.get_realtime_price(asset_name)
                if candle_price_data:
                    latest_data = candle_price_data[-1]
                    timestamp = latest_data['time']
                    price = latest_data['price']
                    formatted_time = time.strftime('%H:%M:%S', time.localtime(timestamp))

                    print(str(Timen)+ f" 📈 {asset} | {formatted_time} | Price: {price:.5f}", end="\r")
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Real-time price monitoring interrupted by user.")
            print(str(Timen)+ " ✅ Real-time monitoring stopped.")
        finally:
            await self.client.stop_realtime_price(asset_name)
            logger.info(f"Real-time price subscription for {asset_name} stopped.")

    @ensure_connection()
    async def get_signal_data(self) -> None:
        """Gets and monitors trading signal data."""
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        logger.info("Getting trading signal data.")

        self.client.start_signals_data()
        print(str(Timen)+ " 📡 Monitoring trading signals...")
        print(str(Timen)+ " Press Ctrl+C to stop monitoring...")
        print("-" * 60)

        try:
            while True:
                signals = self.client.get_signal_data()
                if signals:
                    print(str(Timen)+ f" 🔔 New Signal Received:")
                    print(json.dumps(signals, indent=2,
                                     ensure_ascii=False))
                    print("-" * 60)
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Signal monitoring interrupted by user.")
            print(str(Timen)+ " ✅ Signal monitoring stopped.")
        finally:
            pass

# This synchronous function will be the target for each thread.
# It safely schedules the asynchronous 'buy_simple' coroutine on the main event loop.
def thread_target(loop, cli_instance, **trade_params):
        try:
            future = asyncio.run_coroutine_threadsafe(
                cli_instance.buy_simple(**trade_params),
                loop
            )
            # You can optionally wait for the result within the thread
            future.result(timeout=0.1)  # Wait for up to 120 seconds for the trade to execute
            #logger.info(f"Trade successfully submitted from thread for asset: {trade_params['asset']}")
        except Exception as e:
            logger.error("")


async def main():
    """
    Main function to run trades concurrently using threading.
    """
    logging.getLogger().setLevel(logging.CRITICAL)
    cli = PyQuotexCLI()
    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
    
        
    print(str(Timen) + " Connected to Quotex API successfully!")
    print(str(Timen) + " 📊 Getting account balance...")
    Balance = await cli.get_balance()
    print(Balance)
    await cli.change_account("PRACTICE")
    ListTrade = []
    cnt = 0
    #await asyncio.sleep(30)

    
    # --- Start of Modified Section ---
    try:
        while True:
            #Timens = pd.to_datetime(await cli.client.get_server_time(), utc=False, unit='s')
            # Get the running asyncio event loop to pass it to the threads
            Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
            main_event_loop = asyncio.get_running_loop()
            print("" + str(Timen) + " 📊 Checking active orders to Read...")
    
            # Read trades from the log file
            trades_to_run = read_trades_from_log("orders.log")
    
            if not trades_to_run:
                logger.warning("No trades found in orders.log. Exiting.")
                print(str(Timen) + " ⚠️No trades to execute from orders.log.")
                #return

            #test connection every 30 and 31 seconds
            cnt += 1
            if cnt >= 30:
                cnt = 0
            #if datetime.now().second in [45,46,15,16]:
                print(str(Timen) + " Checking connection status...")
                #print(api.check_connect())
                is_connected = await cli.client.test_connect()
                if is_connected == False:
                    print(str(Timen) + " Reconnecting...")
                    while is_connected == False:
                        print(str(Timen) + " Reconnection failed. Retrying...")
                        try:
                            await cli._connect_with_retry()
                        except Exception as e:
                            pass
                        is_connected = await cli.client.test_connect()
                        await asyncio.sleep(0.5)  # Wait for a short time before retrying
                    print(str(Timen) + " Reconnected successfully!")
                print(str(Timen) + " You Are Still connected !")
                #time.sleep(0.5)  # Wait for a second to ensure reconnection is established
    
            threads = []
            now = datetime.now().timestamp()
            for trade in trades_to_run:
                #print(now - int(trade["stamp"]))
                if (trade['trade_id'] not in ListTrade) and ((now - int(trade["stamp"])) < 15 ):
                    # Create a thread for each trade
                    t = threading.Thread(
                        target=thread_target,
                        args=(main_event_loop, cli),
                        kwargs=trade
                    )
                    threads.append(t)
                    t.start() # Start the thread
                    logger.info(f"Thread started for trade: {trade['trade_id']}")
                    print(str(Timen)+ f"Thread started for trade: {trade['trade_id']}")
                    ListTrade.append(trade['trade_id'])
                else:
                    continue
    
            # Wait for all threads to complete their execution
            #for t in threads:
                #t.join()
    
            #logger.info("All trade threads have completed.")
            #print(str(Timen)+" All trade threads have completed,  Waiting For new Trades ...")
    
            # Clear the list of threads
            threads = []
    
            # You can now perform other operations sequentially after the threads are done
            #Balance = await cli.get_balance()
            #print(str(Timen)+Balance)
            await asyncio.sleep(0.3)

    finally:
        if cli.client and await cli.client.check_connect():
            logger.info("Closing connection.")
            await cli.client.close()
    # --- End of Modified Section ---


if __name__ == "__main__":
    try:
        # The parser is defined but not used in this specific execution.
        # To use command-line arguments, you would need to parse them here.
        # parser = create_parser()
        # args = parser.parse_args()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Program terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {e}", exc_info=True)
        print(f"❌ FATAL ERROR: {e}")
        sys.exit(1)