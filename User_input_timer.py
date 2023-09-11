import time

def shutdown_system_specified_time():
    
        
        User_input_time = input("Please enter the time you want the system to shutdown for in minutes: ")
        
        User_input_time_integer = int(User_input_time)
        
        for i in range(User_input_time_integer, 0, -1):
            print(f"The system is off for {i} minute(s)", end='\r')
            time.sleep(60)  # Wait for 1 second

        print("The system is back on")


shutdown_system_specified_time()