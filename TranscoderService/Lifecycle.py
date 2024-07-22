import time
import requests

from Log import log
import RedisUtils as ru
import CloudwatchUtils as cwu
import S3Utils as s3u
import QueUtils as qu
import DynamoUtils as du
from GenUtils import Storage_Directory
import subprocess as sp

InstanceID = 0


def shutdown():
    while True:
        log.error("Shutting Down")
        response = sp.run(["sudo","shutdown"])

        if response.returncode:
            log.critical("Error Shutting Down")

        time.sleep(60)


def GetInstanceID():
    global InstanceID

    try:
        resp = sp.run(["ec2-metadata","-i"], capture_output=True)
        out = resp.stdout
        resp = out.split()
        InstanceID = resp[1].decode("ASCII")
    except Exception as e:
        log.error("Error Getting Instance Id "+str(e))
        return 0

    return 1


def RegisterKillMe():

    KillMe = 0
    KillTries = 0

    while True:   
        try:
            if ru.ElasticacheRedisClient:
                ru.ElasticacheRedisClient.lpush("KillMe", InstanceID)
                if not cwu.SendCloudwatchKillSignal():
                    KillTries += 1

                else:
                    time.sleep(300)
                    KillTries += 3
            else:
                KillTries += 1

        except Exception as e:
            log.error("Error while registering instance with KillMe set in redis " + str(e))
            KillTries += 1


        if KillTries >= 2:
            shutdown()
            print("Under Kill Me Sleeping")


def SetUpStorageDirectory():
    try:
        result = sp.run(["mkdir",Storage_Directory])
    except Excepions as e:
        log.error("Error Creating Directory " + str(e))
        RegisterKillMe()


def SetUp():

    if not GetInstanceID():
        RegisterKillMe()
    print("Instance Done")

    log.SetUp(InstanceID=InstanceID)

    if not ru.ElasticacheRedisSetup(Host="", Port=):
        RegisterKillMe()
    ru.ElasticacheRedisClient.sadd("Active", InstanceID)
    print("Redis Done")

    if not s3u.S3Setup():
        RegisterKillMe()
    print("S3Done")

    if not qu.QueSetup():
        RegisterKillMe()
    print("Que Done")

    if not du.DynamoSetup():
        RegisterKillMe()
    print("Dynao Done")

    SetUpStorageDirectory()

    return

def CleanUp():

    try:
        if sp.run(["rm", "-r" , Storage_Directory]).returncode:
            RegisterKillMe()
        SetUpStorageDirectory()
    except Exception as e:
        log.error("Error Cleaning Up " + str(e))
        RegisterKillMe()

if __name__ == "__main__":
    #CleanUp(None)
    GetInstanceID()
    print("Instance ID " + InstanceID)
    SetUp()
