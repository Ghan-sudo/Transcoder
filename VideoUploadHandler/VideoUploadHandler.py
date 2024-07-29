import json
import boto3
import logging

log = logging.getLogger()


Lambda_Client = boto3.client("lambda")


DynamoClient = boto3.resource("dynamodb")
UploadTable = DynamoClient.Table("")


Sqs_Client = boto3.client("sqs")
QueueUrl=""

CloudwatchClient = boto3.client("cloudwatch", region_name="eu-central-1")
Namespace = ""
MetricName = ""
DimensionName = ""
DimensionValue = ""
Value = 1


def SendCloudwatchStartSignal():
    try:
        MetricData =[
            {
                'MetricName': MetricName,
                'Dimensions': 
                [
                    {
                        'Name': DimensionName,
                        'Value': DimensionValue
                    },
                ],
                'Value': Value
            },
        ]
    
        response = CloudwatchClient.put_metric_data(Namespace=Namespace, MetricData=MetricData)
        log.critical("CloudWatch Success : " + str(response))

        return 1

    except Exception as e:
        log.error("Error Sending Cloudwatch metrics "+ str(e))
        return 0



def GetKey(event):
        
    try:
        body = json.loads(event["Records"][0]["body"])
        Key = body["detail"]["object"]["key"]
        return str(Key)
        
    except Exception as e:
        log.error("ERROR KEY : "+str(e))
        return 0

def GetData(FileName):
    try:
        res = UploadTable.get_item(Key={"VID": FileName}, ConsistentRead=True)
        data = res["Item"]
        return data
    except Exception as e:
        log.error("Error Getting data from Dynamo "+str(e))
        return None

def GetResolutions(Item):
    try:
        Resolutions = json.loads(Item["Resolutions"])
        return Resolutions
    except Exception as e:
        log.error("Error Loading Resolution from Item "+str(e))
        return None

def GetTitle(Item):
    try:
        Title = Item["Title"]
        return Title
    except Exception as e:
        log.error("Error Loading Title from Item "+str(e))
        return None

def lambda_handler(event, context):
    
    
    ID = GetKey(event)
    if not ID:
        return {
        'statusCode': 500
        }
    

    data = GetData(FileName=ID)
    if not data:
        return {
        'statusCode': 500
        }

    
    Resolutions = GetResolutions(Item=data)

    log.error("RESOLUTIONS : " + str(Resolutions))
    
    if not Resolutions:
        return {
        'statusCode': 500
        }

    Title = GetTitle(Item=data)
    
    log.error("TITLE : "+ str(Title))

    if not Title:
        return {
        'statusCode': 500
        }
    
    payload = {
        "ID":ID,
        "Title":Title,
        "Resolutions": Resolutions
    }
    try:
        response = Lambda_Client.invoke(FunctionName="", Payload=json.dumps(payload))
        log.error(str(response))
        
    except Exception as e:
        log.error("LAMBDA ERROR "+ str(e))
        return {
            "statusCode": 500
        }
        
    
    
    for res in Resolutions:
        req = {
            "ID": ID,
            "Resolution": res
        }
        
        try:
            res = Sqs_Client.send_message(QueueUrl=QueueUrl, MessageBody=json.dumps(req),MessageGroupId=str(ID) + str(res))
            log.error(str(res))
        except Exception as e:
            log.error("ERROR SQS "+ str(e))
            return {
                "statusCode": 500
            }

        if not SendCloudwatchStartSignal():
            return {
                "statusCode": 500
            }

        

    
    log.error(str(res))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
