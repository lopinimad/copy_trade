import sys
import asyncio
import os
from deriv_api import DerivAPI
from deriv_api import APIError
import time
from datetime import datetime
import re
import threading


async def buy(api , symbol:str = "R_100",amount:int  = 1,direction:str = "CALL", duration:int = 60):
    # Get proposal
    proposal = await api.proposal({"proposal": 1, "amount": amount, "basis": "stake",
                                   "contract_type": direction, "currency": "USD", "duration": duration, "duration_unit": "s",
                                   "symbol": symbol
                                   })
    #print(proposal)
   

    # Buy
    response = await api.buy({"buy": proposal.get('proposal').get('id'), "price": amount})
    #print(response)

    if response.get('buy').get('contract_id') :
        return response.get('buy').get('contract_id'),True
    else:
        return None,False

    #await asyncio.sleep(300)

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
                    "direction": "CALL" if direction.lower() == "call" else "PUT",
                    "duration": int(float(duration))
                })
    return orders

async def execute_order(client, order):
    """Executes a single order using the provided client."""
    apip = DerivAPI(app_id=client[0])
    authorize = await apip.authorize(client[1])

    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Deriv: ")
    assets = await apip.cache.asset_index({"asset_index": 1})
    for asset in assets['asset_index']:
        #print(f"Asset: {asset[1]} - {asset[0]}")
        if str(order["asset"]) in str(asset[0]):
            print(f"Found {order['asset']} asset: {asset[0]}")
            nw_asset = str(asset[0])
            pk = True
            break
        else:
            pk = False
    if pk == False:
            print(f"Asset {order['asset']} not found in asset index, skipping order execution.")
            return

    try:
        print(str(Timen) + f" New Order Placing: {order['ID']}")
        order_result = await buy(apip,
            symbol=nw_asset,
            amount=order["amount"],
            direction=str(order["direction"]).upper(),
            duration=order["duration"],
        )
        #print(str(Timen) + f" Order result: {order_result.order_id}")

        # Optionally, check the order result
        if order_result[0] and order_result[1] == True:  # Replace "error" with the actual error status if different
            print(str(Timen) + f" Order placed successfully: {order_result[0]}")
        else:
            print(str(Timen) + f" Failed to place order")

    except Exception as e:
        print(str(Timen) + f" Error executing order: {e}")

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
        token = lines[26].strip()
    except FileNotFoundError:
        print("Error: ssid.txt not found. Please create it.")
        return
    except IndexError:
        print("Error: ssid.txt must contain two lines: one for the demo SSID and one for the live SSID.")
        return

    app_id = 1089
    paka = [app_id,token]

    if len(token) == 0:
        sys.exit("DERIV_TOKEN environment variable is not set")

    api = DerivAPI(app_id=app_id)

    try:
        #logger.info("Connecting to Deriv...")
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Deriv: ")
        print(str(Timen) + " Connecting to Client Deriv...")
        authorize = await api.authorize(token)
        #print(authorize)
        if authorize["authorize"]["account_list"]:
            print(str(Timen) + " Connected successfully to Deriv API!")

            # Wait for authentication and balance
            await asyncio.sleep(1)

            active_symbols = await api.active_symbols({"active_symbols": "brief", "product_type": "basic"})
    
            # Get Balance
            response = await api.balance()
            response = response['balance']
            currency = response['currency']
            print(str(Timen) + " Your current balance is " + str(currency) + " " + str( response['balance']) )
            
            # Get the current event loop to pass to threads
            main_event_loop = asyncio.get_running_loop()

            ListOrder = []
            cnt = 0
            while True:
                Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Deriv: ")
                print("" + str(Timen) + " 📊 Checking active orders to Read...")
                # Read orders from file
                orders = read_orders_from_file("orders.log")
                #print(f"Orders from file: {orders}")
                #await asyncio.sleep(20)

                # Execute orders as threads
                threads = []
                now = datetime.now().timestamp()
                
                for order in orders:
                    if (order["ID"] not in ListOrder) and ((now - int(order["Stamp"])) < 15 ):
                        ListOrder.append(order["ID"])
                        thread = threading.Thread(
                            target=execute_order_thread_target,
                            args=(main_event_loop, paka, order)
                        )
                        threads.append(thread)
                        thread.start()
                    else:
                        continue
    
                # Wait for all tasks to complete
                #for thread in threads:
                    #thread.join()
                
                await asyncio.sleep( 0.5 )  # Use asyncio.sleep in an async function
        else:
            print(str(Timen) + " ❌ Authorization failed. Please check your API token.")
            exit()
            
            
                
    except Exception as e:
        #logger.error(f"Connection error: {e}")
        print(f"Connection error: {e}")

    finally:
        await api.clear()
        print("Disconnected")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n✅ Program terminated by user.")
        sys.exit(0)
    except APIError as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        #logger.critical(f"Fatal error in main execution: {e}", exc_info=True)
        print(f"❌ FATAL ERROR: {e}")
        sys.exit(1)
