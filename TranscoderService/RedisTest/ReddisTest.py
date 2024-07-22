import json
import traceback
import redis
from random import randrange

client = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

def GenerateSet(Client ,ID , Resolutions):
    try:
        Values = list()
        for res in Resolutions:
            Values.append(ID+"-"+res)

        Values.append(ID+"-"+"Last")

        return Values
    except:
        return None

def RedisSetUp(Client, ID , Resolutions):
    try:
        Values = GenerateSet(Client ,ID , Resolutions)
        if not Values:
            print("empty")
            return 0
        for val in Values:
            Client.sadd(ID , val)

        for val in Values:
            Client.set(val , 0)

    except Exception as e:
        #print("Caught" + str(e))
        print(traceback.format_exc())
        return 0

Resolutions = ("1" , "2", "3", "4", "1080p" , "720p" , "360p")
ID = str(randrange(0 , 9999999999999, 1))
print(ID)
RedisSetUp(client, ID , Resolutions)

UpdateStatusLua = """ redis.call("SET", KEYS[1] , "1")
 redis.call("SET" , KEYS[2] .. "-Last" , 1)
return 1
"""

Setter = client.register_script(UpdateStatusLua)
#Setter(keys=[ID+"-720p" , ID])

amILast = """
local mem = redis.call("SMEMBERS" , KEYS[1])

local res = tonumber(1)
for k , y in ipairs(mem) do
    res = res * tonumber(redis.call("GET" , y))
end

if res >= tonumber(1) then
    redis.call("SET" , KEYS[1] .. "-Last" , 0)
end

return res
 """
AmILast = client.register_script(amILast)
#print(AmILast(keys=[ID]))

from random import randint
import time

def test(i):

    time.sleep(randint(0,2))

    r = Resolutions[int(i)]
    Setter(keys=[ID + "-" + r , ID])
    print("From " + str(i) + " " + ID + "-" + r + " : 1")

    
    time.sleep(randint(0,2))

    num = client.incrby("counter", 1)
    res = AmILast(keys=[ID])

    print("Num : " + str(num) + "From " + str(i) + " Res : " + str(res))

from multiprocessing import Process



k = 0

while k < 1:

    m = 0
    lst = list()
    client.set("counter" , 0)
    while m < 50:
        lst.append(Process(target=test, args=(str(m % 7))))
        m += 1

    for prc in lst:
        prc.start()

    for prc in lst:
        prc.join()

    for prc in lst:
        prc.kill()
    # Proc = Process(target=test, args=("0"))
    # Proc2 = Process(target=test, args=("1"))
    # Proc3 = Process(target=test, args=("2"))
    # Proc4 = Process(target=test, args=("1"))
    # Proc5 = Process(target=test, args=("2"))
    
    
    # Proc.start()
    # Proc2.start()
    # Proc3.start()
    # Proc4.start()
    # Proc5.start()
    
    

    # Proc.join()
    # Proc2.join()
    # Proc3.join()
    # Proc4.join()
    # Proc5.join()
    

    
    # Proc.kill()
    # Proc2.kill()
    # Proc3.kill()
    # Proc4.kill()
    # Proc5.kill()
    
    
    k += 1
