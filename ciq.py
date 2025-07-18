from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import asyncio
from loguru import logger
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
                    "direction": direction.lower(),
                    "duration": int(float(duration))
                })
    return orders

def execute_order(client, order):
    """Executes a single order using the provided client."""
    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Iqoption: ")
    try:
        print(str(Timen) + f" New Order Placing: {order['ID']}")
        if order["duration"] > 300:
            order["duration"] = order["duration"] / 60  # Convert duration from seconds to minutes if needed
            order["asset"] = order["asset"].replace("_otc", "-OTC")
            order_result, order_id = client.buy(order["amount"],order["asset"], order["direction"], order["duration"])
        else:
            order["asset"] = order["asset"].replace("_otc", "-OTC")
            order_result, order_id = client.buy_blitz(order["asset"], order["amount"], order["direction"], order["duration"])

        # Optionally, check the order result
        if order_result != False:  # Replace "error" with the actual error status if different
            print(str(Timen) + f" Order placed successfully: {order_id}")
        else:
            print(str(Timen) + f" Failed to place order: {order_id if order_id else 'Unknown error'}")

    except Exception as e:
        print(str(Timen) + f"Error executing order: {e}")


async def main():
            
    """Test placing an order to verify the fix"""

    # Read raw ssids from ssid.txt
    try:
        with open("settings/accounts.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
        # First line is demo ssid, second line is live ssid
        email = lines[17].strip()
        password = lines[18].strip()
    except FileNotFoundError:
        print("Error: ssid.txt not found. Please create it.")
        return
    except IndexError:
        print("Error: ssid.txt must contain two lines: one for the demo SSID and one for the live SSID.")
        return

    
    api = IQ_Option(email, password)

    try:
        #logger.info("Connecting to PocketOption...")
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Iqoption: ")
        print(str(Timen) + " Connecting to Client Iqoption...")
        stat, reas = api.connect()

        if stat:
            #logger.success(" Connected successfully!")
            print(str(Timen) + " Connected successfully!")

            # Wait for authentication and balance
            await asyncio.sleep(1)

            try:
                api.change_balance("PRACTICE")
                print(str(Timen) + " Balance:", api.get_balance())
                print(str(Timen) + " Type of account:", api.get_balance_mode())
                
            except Exception as e:
                #logger.info(f"Balance error (expected with demo): {e}")
                print(str(Timen) + f" Balance error (expected with demo): {e}")

            # Test placing an order (this should now work without the order_id error)
            #logger.info("esting order placement...")

            ListOrder = []
            cnt = 0
            while True:
                Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Iqoption: ")
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
                    if api.check_connect() == False:
                        print(str(Timen) + " Reconnecting...")
                        try:
                            api.connect()
                        except Exception as e:
                            pass
                        #print(api.connect())
                        while api.check_connect() == False:
                            print(str(Timen) + " Reconnection failed. Retrying...")
                            try:
                                api.connect()
                            except Exception as e:
                                pass
                            await asyncio.sleep(0.5)  # Wait for a short time before retrying
                        print(str(Timen) + " Reconnected successfully!")
                    print(str(Timen) + " You Are Still connected !")
                    #time.sleep(0.5)  # Wait for a second to ensure reconnection is established
            
                # Execute orders as threads
                threads = []
                now = datetime.now().timestamp()
                
                for order in orders:
                    if (order["ID"] not in ListOrder) and ((now - int(order["Stamp"])) < 15 ):
                        ListOrder.append(order["ID"])
                        thread = threading.Thread(target=execute_order, args=(api, order))
                        threads.append(thread)
                        thread.start()
                    else:
                        continue
    
                # Wait for all tasks to complete
                #for thread in threads:
                    #thread.join()
                threads = []
                
                await asyncio.sleep( 0.5 )  # Use asyncio.sleep in an async function
                
    except Exception as e:
        #logger.error(f"Connection error: {e}")
        print(f"Connection error: {e}")

    finally:
        api.logout()
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
