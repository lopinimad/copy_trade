# run it like PYTHONPATH=. python3 examples/simple_bot1.py
import sys
import asyncio
import os
from deriv_api import DerivAPI
from deriv_api import APIError
import time
from datetime import datetime
import socket

def test_connection(host="8.8.8.8", port=53, timeout=3):
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True, None
  except Exception as ex:
    #print ex.message
    return False, ex

# Check connection to Deriv server
destination_host = "app.deriv.com"
destination_port = 443  # Default port for HTTPS
timeout = 0.5

# Read raw ssids from ssid.txt
try:
    with open("settings/accounts.json", "r", encoding="utf-8") as f:
        lines = f.readlines()
    # First line is demo ssid, second line is live ssid
    token = lines[22].strip()
except FileNotFoundError:
    print("Error: ssid.txt not found. Please create it.")
except IndexError:
    print("Error: ssid.txt must contain two lines: one for the demo SSID and one for the live SSID.")



app_id = 1089
#token = os.getenv('DERIV_TOKEN', token)

if len(token) == 0:
    sys.exit("DERIV_TOKEN environment variable is not set")


async def main():
    api = DerivAPI(app_id=app_id)
    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]Deriv: ")
    print(str(Timen) + " Connecting to Deriv API...")
    # Authorize
    authorize = await api.authorize(token)
    #print(authorize)
    if authorize["authorize"]["account_list"]:
        print(str(Timen) + " Connected successfully to Deriv API!")
    else:
        print(str(Timen) + " ❌ Authorization failed. Please check your API token.")
        exit()


    # Get Balance
    response = await api.balance()
    response = response['balance']
    currency = response['currency']
    print(str(Timen) + " Your current balance is " + str(currency) + " " + str( response['balance']) )
    
    # Get assets
    #assets = await api.cache.asset_index({"asset_index": 1})
    #print(assets)
    #await buy(api, symbol= "R_100",amount = 1, duration = 60)
    #await buy(api, symbol= "R_100",amount = 1, duration = 60)
    lt = []  # list of open contracts
    ListTrade =  []
    cnt = 0  # Counter for connection checks
    while True:
        try:
            cnt += 1
            if cnt >= 30:
                Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]Deriv: ")
                cnt = 0
            #if datetime.now().second in [45,46,15,16]:
                test_result, ex = test_connection(destination_host, destination_port, timeout)
                if test_result == True:
                    print(str(Timen) + " Checking connection status...")
                    api = DerivAPI(app_id=app_id)
                    # Authorize
                    authorize = await api.authorize(token)
                
                    if authorize["authorize"]["account_list"]:
                        print(str(Timen) + " ✅ Reconnected successfully !")
                        response = await api.ping({'ping': 1})
                    else:
                        print(str(Timen) + " ❌ Reconnection failed. Retrying...")
                        cnt = 31
            test_result, ex = test_connection(destination_host, destination_port, timeout)
            if test_result == True:
                Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]Deriv: ")
                print("" + str(Timen) + " 📊 Checking active orders to Write...")

            
                trades = await api.proposal_open_contract(
                    {"proposal_open_contract": 1 })
                #print(trades)
                #print(trades['proposal_open_contract']['contract_id'], trades['proposal_open_contract']['status'])
                #for trade in lt:
                if bool(trades['proposal_open_contract']) == True:
                    if str(trades['proposal_open_contract']['contract_id'])[-8:] not in lt:
                        #lt.append(str(trades['proposal_open_contract']['contract_id'])[-8:])  # Store only the last 8 characters of the contract ID
                        ListTrade.append(trades['proposal_open_contract'])
            
                    #print("Open Contracts: ", len(ListTrade))
                if ListTrade:
                    for trade in ListTrade:
                        idt = str(trade['contract_id'])[-8:] 
                        if (idt not in lt) and ((int(time.time()) - int(trade['date_start'])) < 15) :
                            duration = trade['date_expiry'] - trade['date_start']      
                            trade['underlying'] = str(trade['underlying']).replace("frx", "")
                            #print(trade)
                            print(str(Timen) + " New trade detected:"+ str(idt)+ " Asset: " + trade['display_name'] + " Direction: " + str(trade['contract_type']).lower() + " Duration: " + str(duration) + " seconds")
                            log_entry = f"- Time: {datetime.now()} Stamp: {int(datetime.now().timestamp())} ID: {int(idt)} Asset: {trade['underlying']} Amount: {trade['buy_price']} Direction: {str(trade['contract_type']).lower()} Duration: {duration}\n"  #trade['underlying'] + "\n"
                            with open("orders.log", "a", encoding="utf-8") as f:
                                f.write(log_entry)
                            print(str(Timen) + f"   -> Logged new order {idt} to orders.log")
                            lt.append(idt)
                            
                        else:
                            continue
            else:
                Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]Deriv: ")
                print(str(Timen) + " ❌ Reconnection failed. Retrying...")
                cnt = 31 
            await asyncio.sleep(0.5)
        except APIError as e:
            print(str(Timen) + " API Error: " + str(e))
            await asyncio.sleep(0.5)
    

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

