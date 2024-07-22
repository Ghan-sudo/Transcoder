import boto3
import Lifecycle as lf
from Log import log
import json

QueClient = None
GetMessageQueUrl = ""
DeadLetterQueUrl = ""
MessageGroupId=""

def QueSetup():

    global QueClient
    try:
        QueClient = boto3.client("sqs", region_name="eu-central-1")
        return 1

    except Exception as e:
        log.error("Error Setting up SQS client " + str(e))
        return 0

def DeleteMessage(message):
    try:
        QueClient.delete_message(QueueUrl=GetMessageQueUrl,ReceiptHandle=message["ReceiptHandle"])

    except Exception as e:
        log.error("Error While Deleting Message "+ str(e))
        return 0
    return 1



def ReleaseMessage(message):
    try:
        if not DeleteMessage(message=message):
            return 0

        QueClient.send_message(QueueUrl=DeadLetterQueUrl, MessageBody=json.dumps(message), MessageGroupId=MessageGroupId)

    except Exception as e:
        log.error("Error While Releasing Message "+ str(e))
        return 0
    return 1


def GetTask():
    message = None

    while True:
        try:
            message = QueClient.receive_message(QueueUrl=GetMessageQueUrl,MaxNumberOfMessages=1,WaitTimeSeconds=20)
            print(message)
            
            if not message:
                return 0

        except Exception as e:
            log.error("ERROR while receiving message " + str(e))
            lf.RegisterKillMe()
            return 0

        response = {}
        try:
            MessageId = message["Messages"][0]["ReceiptHandle"]
            response["ReceiptHandle"] = MessageId

        except Exception as e:
            log.error("ERROR while parsing message " + str(e))
            lf.RegisterKillMe()
            continue

        try:
            body = json.loads(message["Messages"][0]["Body"])
            ID = body["ID"]
            response["ID"] = ID

            Resolution = body["Resolution"]
            response["Resolution"] = Resolution
            return response

        except Exception as e:
            log.error("ERROR while parsing body " + str(e))
            ReleaseMessage(message=response)
            continue

    






if __name__ == "__main__":

    QueSetup()
    message = GetTask()
    print(str(message))
    ReleaseMessage(message=message)
