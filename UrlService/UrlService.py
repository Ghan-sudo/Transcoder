import boto3 as boto
import json
import logging
from botocore.exceptions import ClientError
from random import randrange

s3_client = boto.client("s3")

DynamoClient = boto.resource("dynamodb")
UploadTable = DynamoClient.Table("")

logger = logging.getLogger()
logger.setLevel("INFO")


BucketName = ""

def GenerateUrl(FileSize , BucketName , FileName , Fields={} , Conditions=[] , expiry=60):

    if(FileSize >  200000000 ):
        url = {}
        url["error"] = "File too large"
        return url

    if(FileSize <  200 ):
        url = {}
        url["error"] = "File too Small"
        return url
    
    Conditions.append(['content-length-range', 200,200000000])

    try:
        url = s3_client.generate_presigned_post(BucketName , Key=FileName, Fields=Fields, Conditions=Conditions, ExpiresIn=expiry)

        logger.info("S3 url generated")

    except ClientError as e:
        logging.error(e)
        return None

    return url

def GetFileSize(event):
    try:
        FileSize = int(event["FileSize"])
        return FileSize
    except Exception as e :
        logger.error("Error Getting FileSize "+ str(e))
        return 0

def GetRealFileName(event):
    try:
        FileName = str(event["FileName"])
        return FileName
    except Exception as e :
        logger.error("Error Getting FileName "+ str(e))
        return 0

def GetResolutions(event):
    try:
        Resolutions = event["Resolutions"]
        return Resolutions
    except Exception as e :
        logger.error("Error Getting Resolutions "+ str(e))
        return 0

def PutDetails(RealFileName, FileName, Resolutions):
    try:
        res = UploadTable.put_item(Item={
            "VID":str(FileName),
            "Title":RealFileName,
            "Resolutions":json.dumps(Resolutions)
        }
        )
        return 1
    except Exception as e:
        logger.error("Error Putting details to DynaoDB "+str(e))


def lambda_handler(event , context):
    FileSize = GetFileSize(event=event)
    if not FileSize:
        return {"StatusCode":500}

    RealFileName = GetRealFileName(event=event)
    if not RealFileName:
        return {"StatusCode":500}

    Resolutions = GetResolutions(event=event)
    if not Resolutions:
        return {"StatusCode":500}


    FileName = str(randrange(1,99999999,1))

    if not PutDetails(RealFileName=RealFileName, FileName=FileName, Resolutions=Resolutions):
        return {"StatusCode":500}

    url = GenerateUrl(FileSize=FileSize , BucketName=BucketName , FileName=FileName)

    if not url:
        return {"StatusCode":500}
    
    
    return url

