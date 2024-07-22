import redis
from Log import log


ElasticacheRedisClient = None
UpdateStatus = None
UpdateStatusFunc = None
AmILast = None
AmILastFunc = None

def ElasticacheRedisSetup( Host, Port):
    global ElasticacheRedisClient
    global UpdateStatus
    global UpdateStatusFunc
    global AmILast
    global AmILastFunc

    try:
        ElasticacheRedisClient = redis.Redis(host=Host,port=Port, decode_responses=True)
        
        UpdateStatusLua = """ redis.call("HSET", KEYS[1], KEYS[2] , 1)
        redis.call("SET", KEYS[3], 1)
        return 0 """
        
        UpdateStatus = ElasticacheRedisClient.register_script(UpdateStatusLua)
        
        AmILastLua = """
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
            
        AmILast = ElasticacheRedisClient.register_script(AmILastLua)
            
    except Exception as e:
        log.error("Error while Setting Up redis " + str(e))
        return 0

    return 1

def UpdateStatusFunc(Keys):
    try:
        UpdateStatus(Keys)
            
    except Exception as e:
        log.error("Error Updating Status " + str(e))
        return 0

    return 1
        
    
def AmILastFunc(Keys):
    try:
        Result = AmILast(Keys)
        return Result

    except Exception as e:
        log.error("Error AmILast " + str(e))
        return 0



def RedisCleanup(ID, Resolutions):
    try:
        pipe = ElasticacheRedisClient.pipeline()

        for val in Resolutions:
            pipe.hdel(ID, val)
            pipe.getdel(str(ID + "-Last"))
            pipe.execute()
    except Exception as e:
        log.error("Error Cleaning up Redis "+ str(e))
        return 0

    return 1








if __name__ == "__main__":

    from multiprocessing import Process
    from random import randrange
    from random import randint
    import time

    def RedisSetUp(client, ID , Resolutions):
        try:
            pipe = client.pipeline()
            for val in Resolutions:
                pipe.hset(ID , val, 0)

            pipe.set(str(ID+"-Last"), 1)

            pipe.execute()

        except Exception as e:
            print("Caught" + str(e))
            return 0

    Resolutions = ("1920x1080" , "100x720" , "650x360")
    ID = str(randrange(0 , 9999999999999, 1))
    print(ID)

    ElasticacheRedisSetup(Host="", Port=6379)

    RedisSetUp(ElasticacheRedisClient, ID , Resolutions)




    def test(i):
        time.sleep(randint(0, 5))
        r = Resolutions[int(i)]
        count = UpdateStatusFunc(Keys=[ID, str(r) , str(ID+"-Last")])
        print("From " + str(i) + " " + ID + "-" + r + " : 1")
        time.sleep(randint(0,10))
        res = AmILastFunc(Keys=[ID, str(ID + "-Last")])
        print("From " + str(i) + " Res : " + str(res.pop(0)) + "  " + str(res))


    k = 0
    while k < 1:

        m = 0
        lst = list()
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
        
    #RedisCleanup(ID , Resolutions)
