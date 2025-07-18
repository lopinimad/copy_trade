"""
Test script to verify the place_order fix
"""
import re
import asyncio
from loguru import logger
from pocketoptionapi_async import AsyncPocketOptionClient, OrderDirection
from datetime import datetime
import sys



def keep_dgt(text, replacement_char='_'):
    """
    Keeps only numeric characters in a string and replaces all other characters
    with a specified replacement character.

    Args:
        text (str): The input string.
        replacement_char (str): The character to replace non-numeric characters with.

    Returns:
        str: The modified string with only numbers and replacement characters.
    """
    # Define a regex pattern that matches any character that is NOT a digit (0-9)
    pattern = r'[^0-9]'
    # Replace all non-digit characters with the specified replacement_char
    cleaned_text = re.sub(pattern, replacement_char, text)
    return cleaned_text

async def main():
    """Test placing an order to verify the fix"""
     
    # Read raw ssids from ssid.txt
    try:
        with open("settings/accounts.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
        # First line is demo ssid, second line is live ssid
        ssid = lines[2].strip()
        ssid_live = lines[3].strip()
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
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]PocketOption: ")
        print(str(Timen) + " Connecting to Master PocketOption...")
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
            ListOrder = []
            cnt = 0
            while True:
                try:
                    # Check active orders
                    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]PocketOption: ")
                    print("" + str(Timen) + " 📊 Checking active orders to Write...")
                    active_orders = await client.get_active_orders()
                    #print(f"Active orders count: {len(active_orders)}")
                    
                    #test connection every 30 and 31 seconds
                    cnt += 1
                    if cnt >= 30 and not active_orders:
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
                            print(str(Timen) + " Reconnected successfully!")
                        print(str(Timen) + " You Are Still connected !")
                        #time.sleep(0.5)  # Wait for a second to ensure reconnection is established
                    
                    #print(f"   -> Deleted order from {active_orders}")
                    for order in active_orders:
                        duration = order.expires_at - order.placed_at
                        order_id = keep_dgt(str(order.order_id), '')   # Replace colons with underscores
                        order_id = order_id[-8:] # Keep only the last 8 characters
                        print(str(Timen) + f"   - ID: {order_id}: Asset: ({order.asset}) Direc: {order.direction} Time: {duration} Mn ")
                        # Check immediate order result
                        
                        if order_id not in ListOrder:
                            # The order object has an 'open_time' attribute which is a datetime object.
                            log_entry = f"- Time: {datetime.now()} Stamp: {int(datetime.now().timestamp())} ID: {order_id} Asset: {order.asset} Amount: {order.amount} Direction: {order.direction} Duration: {order.duration}\n"
                            with open("orders.log", "a", encoding="utf-8") as f:
                                f.write(log_entry)
                            print(str(Timen) + f"   -> Logged new order {order_id} to orders.log")
                            ListOrder.append(order_id)
                            await client.delete_order_result(order.order_id)  # Delete the order after logging

                            
                    await asyncio.sleep(0.5)  # Use asyncio.sleep in an async function
                except Exception as e:
                    #logger.error(f"An error occurred: {e}")
                    print(str(Timen) + f" An error occurred: {e}")
                    await client._reconnection_monitor()  # Attempt to reconnect if an error occurs
        else:
            #logger.warning("Connection failed (expected with demo SSID)")
            print(str(Timen) + " Connection failed (expected with demo SSID)")

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
