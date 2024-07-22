import boto3
from Log import *

S3Client = None
DownloadBucketName = ""
UploadBucketName = ""

def S3Setup():
    global S3Client

    try:
        S3Client = boto3.client("s3", region_name="eu-central-1")
        return 1
    except Exception as e:
        log.error("Error While Seting Up S3 "+ str(e))
        return 0


def DownloadFile(ID,Location):
    try:
        S3Client.download_file(DownloadBucketName, ID, Location)
        return Location
    except Exception as e:
        log.error("Error DownloadFile " + str(e))
        return 0
    return 1

def DownloadProcessedFile(ID,Location):
    try:
        S3Client.download_file(UploadBucketName, ID, Location)
        return Location
    except Exception as e:
        log.error("Error DownloadFile " + str(e))
        return 0
    return 1


def UploadFile(ID,Location):
    try:
        S3Client.upload_file(Filename = Location, Bucket=UploadBucketName, Key=ID)
    except Exception as e:
        log.error("Error UploadFile " + str(e))
        return 0
    return 1

def DeleteFile(ID):
    try:
        S3Client.delete_object(Bucket=DownloadBucketName, Key=ID)
        return 1
    except Exception as e:
        log.error("Error Deleting File : " + str(e))
        return 0
    return

if __name__ == "__main__":

    file = input("File Name : ")

    S3Setup()
    DownloadFile(ID=file, Location=file)
    UploadFile(ID=file, Location=file)
