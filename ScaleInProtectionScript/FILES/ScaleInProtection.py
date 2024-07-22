import json
import logging
import redis
import boto3

ElasticacheRedisClient = redis.Redis(host="",port=, decode_responses=True)

IdSet = "KillMe"


log = logging.getLogger()

def GetLen(client, IdSet):
    try:
        length = client.llen(IdSet)
        return length
    except Exception as e:
        log.error("Error Getting list length "+ str(e))
        return None

def RemoveIDs(client, IdSet, Capacity):
    try:
        IDs = client.rpop(IdSet,Capacity)

        if not IDs:
            return [0]
        return IDs

    except Exception as e:
        log.error("Error RPOPing from Regis " + str(e))
        return []

def GetTotalCapacity(event):
    Caps = event["CapacityToTerminate"]

    total = 0
    for cps in Caps:
        total += cps["Capacity"]

    return total

def Ping(event):
    try:
        ping = event["Ping"]
        return ping
    except:
        return 0


def Setup(event, context):

    Length = GetLen(client=ElasticacheRedisClient, IdSet=IdSet)

    log.error("Length : " + str(Length))

    if Ping(event):
        log.error("Pinging ")
        return{
            "statusCode": 500
        }

    Capacity = GetTotalCapacity(event=event)
    log.error("Capacity : " + str(Capacity))

    IDs = []

    if Capacity >= Length:
        IDs = RemoveIDs(client=ElasticacheRedisClient, IdSet=IdSet, Capacity=Length)

    else:
        IDs = RemoveIDs(client=ElasticacheRedisClient, IdSet=IdSet, Capacity=Capacity)

    log.error("IDs : "+str(IDs))
    log.error("Json IDs : "+ json.dumps(IDs))
    
    #Default jsn converting ID fucks it up
    return {
        'InstanceIDs': IDs
    }

# if __name__=="__main__":
#     client = redis.Redis()
#     client.lpush(IdSet, "i-1290fefr98")
#     len = GetLen(client=client, IdSet=IdSet)
#     print(str(len))
#     bIDs = RemoveIDs(client=client, IdSet=IdSet, Capacity=4)
#     IDs = []
#     for id in bIDs:
#         print(id.decode("ASCII"))
#         IDs.append(id.decode("ASCII"))
#     print(str(IDs))
