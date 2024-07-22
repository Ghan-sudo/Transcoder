import boto3
from Log import log

DynamoClient = None
VidsTable = None

def DynamoSetup():

    global DynamoClient
    global VidsTable

    try:
        DynamoClient = boto3.resource("dynamodb", region_name="")

        VidsTable = DynamoClient.Table("")
        return 1
        
    except Exception as e:
        log.error("Error while Setting Up DynamoDB "+ str(e))
        return 0

def UpdateStatus(ID):
    
    try:
        VidsTable.update_item(
            Key={
                'VID': ID
            },
            UpdateExpression="SET #st = :ans",
            ExpressionAttributeNames={
                "#st": "status"
                },
            ExpressionAttributeValues={
                ':ans': "done"
                }
            )
        
        return 1

    except Exception as e:
        log.error("Can't Update Dynamo DB for ID : " + ID + " "+ str(e))
        return 0

if __name__ == "__main__":
    DynamoSetup()
