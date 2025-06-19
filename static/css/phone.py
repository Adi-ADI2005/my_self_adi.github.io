import pywhatkit as pwk
import time

phone_number = "+917853988633"
message = "hello muthi mama"
hour = 18
minute = 55

for i in range(500):  
    pwk.sendwhatmsg(phone_number, message, hour, minute + i)  
    

