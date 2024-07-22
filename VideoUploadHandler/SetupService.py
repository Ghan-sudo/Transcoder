import json
import logging
import redis
import boto3
import traceback

ElasticacheRedisClient = redis.Redis(host="",port=, decode_responses=True)

DynamoClient = boto3.resource("dynamodb")
VidsTable = DynamoClient.Table("")

logger = logging.getLogger()

def RedisSetUp(client, ID , Resolutions):
    try:
        pipe = client.pipeline()
        for val in Resolutions:
            pipe.hset(ID , val, 0)

        pipe.set(str(ID+"-Last"), 0)

        pipe.execute()

    except Exception as e:
        logger.error(str(traceback.format_exc()))
        return 1

    return 0

def DynamoSetUp(ID, title):
    try:
        
        logger.error("After Table")
        res = VidsTable.put_item(Item={
            "VID":str(ID),
            "src":str(ID+".mpd"),
            "img":str(ID + "-thumbnail.png"),
            "title":title,
            "status":str("proc")
        }
        )
        logger.error(str(res))

    except Exception as e:
        logger.error(str(e))
        return 1
    return 0




def GetID(event):
    try:
        ID = str(event["ID"])
        return ID

    except Exception as e:
        logger.error("ERROR GETID "+str(e))
        return 0

def GetResolutions(event):

    try:
        Resolutions = event["Resolutions"]
        return Resolutions

    except Exception as e:
        logger.error("ERROR GetResolutions "+str(e))
        return 0


def GetTitle(event):
    try:
        Title = str(event["Title"])
        return Title

    except Exception as e:
        logger.error("ERROR GETID "+str(e))
        return 0

def Setup(event, context):

    ID = GetID(event)

    if not ID:
        return {
            "statusCode": 500
        }

    Resolutions = GetResolutions(event)

    if not Resolutions:
        return {
            "statusCode": 500
        }

    title = GetTitle(event)

    if not title:
        return {
            "statusCode": 500
        }
    
    logger.error(str(event))

    if RedisSetUp(client=ElasticacheRedisClient, ID=ID, Resolutions=Resolutions):
        return {
            'statusCode': 500
        }
    
    logger.error("RedisDone")
      
    if DynamoSetUp(ID, title):
        return {
            'statusCode': 500
        }
    
    logger.error("DynamoDone")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
