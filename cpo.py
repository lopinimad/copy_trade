import asyncio
from loguru import logger
from pocketoptionapi_async import AsyncPocketOptionClient, OrderDirection
from datetime import datetime
import re
import threading
import sys


def read_orders_from_file(file_path):
    """Reads orders from the log file and extracts relevant information."""
    orders = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(
                r"Stamp: (\d+\.?\d*) ID: (\d+\.?\d*) Asset: ([\w-]+) Amount: (\d+\.?\d*) Direction: (\w+) Duration: (\d+\.?\d*)",
                line,
            )
            if match:
                stamp, id, asset, amount, direction, duration = match.groups()
                orders.append({
                    "Stamp": float(stamp),
                    "ID": int(id),
                    "asset": asset,
                    "amount": float(amount),
                    "direction": OrderDirection.CALL if direction.lower() == "call" else OrderDirection.PUT,
                    "duration": int(float(duration))
                })
    return orders

async def execute_order(client, order):
    """Executes a single order using the provided client."""
    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]PocketOption: ")
    try:
        print(str(Timen) + f" New Order Placing: {order['ID']}")
        order_result = await client.place_order(
            asset=order["asset"],
            amount=order["amount"],
            direction=order["direction"],
            duration=order["duration"],
        )
        #print(str(Timen) + f" Order result: {order_result.order_id}")

        # Optionally, check the order result
        if order_result and order_result.status != "error":  # Replace "error" with the actual error status if different
            print(str(Timen) + f" Order placed successfully: {order_result.order_id}")
        else:
            print(str(Timen) + f" Failed to place order: {order_result.error_message if order_result else 'Unknown error'}")

    except Exception as e:
        print(f"Error executing order: {e}")

def execute_order_thread_target(loop, client, order):
    """Schedules execute_order to run on the main event loop from a separate thread."""
    try:
        # Schedule the coroutine to be executed in the event loop
        future = asyncio.run_coroutine_threadsafe(execute_order(client, order), loop)
        # Wait for the coroutine to finish. A timeout is a good idea.
        future.result(timeout=60)
    except Exception as e:
        print(f"Error in thread for order {order.get('ID', 'N/A')}: {e}")

async def main():
            
    """Test placing an order to verify the fix"""

    # Read raw ssids from ssid.txt
    try:
        with open("settings/accounts.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
        # First line is demo ssid, second line is live ssid
        ssid = lines[7].strip()
        ssid_live = lines[8].strip()
    except FileNotFoundError:
        print("Error: ssid.txt not found. Please create it.")
        return
    except IndexError:
        print("Error: ssid.txt must contain two lines: one for the demo SSID and one for the live SSID.")
        return

    
    client = AsyncPocketOptionClient(ssid=ssid, is_demo=True,  # Enable keep-alive like old API
            auto_reconnect=True,)

    try:
        #logger.info("Connecting to PocketOption...")
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]PocketOption: ")
        print(str(Timen) + " Connecting to Client PocketOption...")
        await client.connect()

        if client.is_connected:
            #logger.success(" Connected successfully!")
            print(str(Timen) + " Connected successfully!")

            # Wait for authentication and balance
            await asyncio.sleep(1)

            try:
                balance = await client.get_balance()
                if balance:
                    #logger.info(f"Balance: ${balance.balance:.2f}")
                    print(str(Timen) + f" Balance: ${balance.balance:.2f}")
                else:
                    #logger.warning("No balance data received")
                    print(str(Timen) + " No balance data received")
            except Exception as e:
                #logger.info(f"Balance error (expected with demo): {e}")
                print(str(Timen) + f" Balance error (expected with demo): {e}")

            # Test placing an order (this should now work without the order_id error)
            #logger.info("esting order placement...")

            # Get the current event loop to pass to threads
            main_event_loop = asyncio.get_running_loop()

            ListOrder = []
            cnt = 0
            while True:
                Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]PocketOption: ")
                print("" + str(Timen) + " 📊 Checking active orders to Read...")
                # Read orders from file
                orders = read_orders_from_file("orders.log")
                #print(f"Orders from file: {orders}")
                #await asyncio.sleep(20)

                #test connection every 30 and 31 seconds
                cnt += 1
                if cnt >= 30:
                    cnt = 0
                #if datetime.now().second in [45,46,15,16]:
                    print(str(Timen) + " Checking connection status...")
                    #print(api.check_connect())
                    if client.is_connected == False:
                        print(str(Timen) + " Reconnecting...")
                        try:
                            await client.connect()
                        except Exception as e:
                            pass
                        #print(api.connect())
                        while client.is_connected == False:
                            print(str(Timen) + " Reconnection failed. Retrying...")
                            try:
                                await client.connect()
                            except Exception as e:
                                pass
                            await asyncio.sleep(0.5)  # Wait for a short time before retrying
                        print(str(Timen) + " Reconnected successfully !")
                    print(str(Timen) + " You Are Still connected !")
                    #time.sleep(0.5)  # Wait for a second to ensure reconnection is established
            
                # Execute orders as threads
                threads = []
                now = datetime.now().timestamp()
                
                for order in orders:
                    if (order["ID"] not in ListOrder) and ((now - int(order["Stamp"])) < 15 ):
                        ListOrder.append(order["ID"])
                        thread = threading.Thread(
                            target=execute_order_thread_target,
                            args=(main_event_loop, client, order)
                        )
                        threads.append(thread)
                        thread.start()
                    else:
                        continue
    
                # Wait for all tasks to complete
                #for thread in threads:
                    #thread.join()
                
                await asyncio.sleep( 0.5 )  # Use asyncio.sleep in an async function
                
    except Exception as e:
        #logger.error(f"Connection error: {e}")
        print(f"Connection error: {e}")

    finally:
        await client.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n✅ Program terminated by user.")
        sys.exit(0)
    except Exception as e:
        #logger.critical(f"Fatal error in main execution: {e}", exc_info=True)
        print(f"❌ FATAL ERROR: {e}")
        sys.exit(1)
