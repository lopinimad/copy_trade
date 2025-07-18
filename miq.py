from iqoptionapi.stable_api import IQ_Option
from iqoptionapi import expiration
import time
from datetime import datetime
import sys


# Read raw ssids from ssid.txt
try:
    with open("settings/accounts.json", "r", encoding="utf-8") as f:
        lines = f.readlines()

    email = lines[12].strip()
    password = lines[13].strip()
except FileNotFoundError:
    print("Error: ssid.txt not found. Please create it.")
except IndexError:
    print("Error: ssid.txt must contain two lines: one for the demo SSID and one for the live SSID.")


api = IQ_Option(email, password)
stat, reas = api.connect()

Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]Iqoption: ")
print(str(Timen) + " Connecting to [Master]Iqoption...")

if stat:
    print(str(Timen) + " Connected successfully!")
else:
    print(str(Timen) + " Connection failed:", reas)
    exit()

api.change_balance("PRACTICE")
print(str(Timen) + " Balance:", api.get_balance())
print(str(Timen) + " Type of account:", api.get_balance_mode())

ListTrade = []
cnt = 0
while True:
    try:
        
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Master]Iqoption: ")
        print("" + str(Timen) + " 📊 Checking active orders to Write...")
        trades = api.get_option_open_by_other_pc()

        #test connection every 30 and 31 seconds
        cnt += 1
        if cnt >= 30 and not trades:
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
                    time.sleep(0.5)  # Wait for a short time before retrying
                print(str(Timen) + " Reconnected successfully!")
            print(str(Timen) + " You Are Still connected !")
            #time.sleep(0.5)  # Wait for a second to ensure reconnection is established
        
        if trades:
            #print("Trades:", trades)
            for id, trade in trades.items():
                idt = str(id)
                idt = idt[-8:] 
                if idt not in ListTrade:
                    duration = trade['msg']['expired'] - trade['msg']['created']
                    durations = expiration.get_remaning_time(datetime.now().timestamp())
                    #print(durations,duration)
                    for i in durations:
                        if duration >= i[1]:
                            continue
                        else:
                            duration_new = i[0] * 60
                            break     
                    #print("Duration:", duration, "New Duration:", duration_new)
                    #print(trade)
                    #time.sleep(700)  # Use time.sleep in a synchronous function
                    if trade['msg']['type_name'] == "blitz":
                        duration_new = duration
                    pktrade = str(trade['msg']['active']).replace("-OTC", "_otc")
                    pktrade = str(pktrade).replace("-op", "")
                    print(str(Timen) + " New trade detected:"+ str(idt)+ " Asset: " + trade['msg']['active'] + " Direction: " + trade['msg']['dir'] + " Duration: " + str(duration_new) + " seconds")
                    log_entry = f"- Time: {datetime.now()} Stamp: {int(datetime.now().timestamp())} ID: {idt} Asset: {pktrade} Amount: {trade['msg']['profit_amount']} Direction: {trade['msg']['dir']} Duration: {duration_new}\n"
                    #log_entry = f"ID: {id}, Active: {trade['msg']['active']}, Amount: {trade['msg']['profit_amount'] }, Direction: {trade['msg']['dir']} created: {trade['msg']['created']}, Expired: {trade['msg']['expired']} Type: {trade['msg']['type_name']} "
                    with open("orders.log", "a", encoding="utf-8") as f:
                        f.write(log_entry)
                    print(str(Timen) + f"   -> Logged new order {idt} to orders.log")
                    ListTrade.append(idt)
                    api.del_option_open_by_other_pc(id)
                else:
                    continue
        time.sleep(0.5)  # Use time.sleep in a synchronous function
    
    except Exception as e:
        print(str(Timen) + f" An error occurred: {e}")
        time.sleep(0.5)  # Wait for a short time before retrying
        #api.check_connect()

    except KeyboardInterrupt:
        print("\n✅ Program terminated by user.")
        sys.exit(0)
    