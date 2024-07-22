import json
import traceback
import redis
from random import randrange

client = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)


def RedisSetUp(Client, ID , Resolutions):
    try:
        pipe = client.pipeline()
        for val in Resolutions:
            pipe.hset(ID , val, 0)

        pipe.set(str(ID+"-Last"), 1)

        pipe.execute()

    except Exception as e:
        #print("Caught" + str(e))
        print(traceback.format_exc())
        return 0

Resolutions = ("1920x1080" , "100x720" , "650x360")
ID = str(randrange(0 , 9999999999999, 1))
print(ID)
RedisSetUp(client, ID , Resolutions)

UpdateStatusLua = """ redis.call("HSET", KEYS[1], KEYS[2] , 1)
 redis.call("SET", KEYS[3], 1)
return 0
"""

Setter = client.register_script(UpdateStatusLua)

amILast = """
local mem = redis.call("HKEYS" , KEYS[1])
local vals = redis.call("HMGET", KEYS[1], unpack(mem))

local res = tonumber(1)
for k , v in ipairs(vals) do
    res = res * v
end

local last = redis.call("GET", KEYS[2])

res = res*last

local ret = {}
table.insert(ret , res)


if res >= 1 then
redis.call("SET" , KEYS[2] , 0)
for x,y in ipairs(mem) do
table.insert(ret ,y )
end
end


return ret
 """
AmILast = client.register_script(amILast)

if __name__ == "__main__":

    from random import randint
    import time


    def test(i):

        time.sleep(randint(0, 5))

        r = Resolutions[int(i)]
        count = Setter(keys=[ID, str(r) , str(ID+"-Last")], )
        print("From " + str(i) + " Count : " + str(count) + " " + ID + "-" + r + " : 1")

        
        time.sleep(randint(0,10))

        res = AmILast(keys=[ID, str(ID + "-Last")])


        print("From " + str(i) + " Res : " + str(res.pop(0)) + "  " + str(res))


    def RedisCleanup( ID, Resolutions):

        pipe = client.pipeline()

        for val in Resolutions:
            pipe.hdel(ID, val)

        pipe.getdel(str(ID + "-Last"))

        pipe.execute()
        print("Finished CLeaning")
        return 0


    from multiprocessing import Process

    k = 0

    while k < 1:

        m = 0
        lst = list()
        client.set("counter" , 0)
        while m < 10:
            lst.append(Process(target=test, args=(str(m % 3))))
            m += 1

        for prc in lst:
            prc.start()

        for prc in lst:
            prc.join()

        for prc in lst:
            prc.kill()
        
        
        k += 1
        
    RedisCleanup(ID , Resolutions)