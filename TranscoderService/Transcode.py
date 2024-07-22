import Lifecycle as lf
import Processor as pr
import QueUtils as qu
import S3Utils as s3u
import RedisUtils as ru
import CloudwatchUtils as cwu
import GenUtils as gu
import DynamoUtils as du

def FinishTask(ID, Resolutions, message):
    if not s3u.DeleteFile(ID=ID):
        qu.ReleaseMessage(message=message)
        lf.RegisterKillMe()
    
    if not qu.DeleteMessage(message=message):
        lf.RegisterKillMe()
    
    if not du.UpdateStatus(ID=ID):
        lf.RegisterKillMe()

    ru.RedisCleanup(ID=ID, Resolutions=Resolutions)
    return


def main():

    lf.SetUp()

    while True:

        message = qu.GetTask()

        if not message:
            lf.RegisterKillMe()

        Resolution = message["Resolution"]

        OrigionalVideoName = message["ID"]
        OrigionalVideoNameDirectory = gu.GenerateNameDirectory( ID=OrigionalVideoName)

        if not s3u.DownloadFile(ID=OrigionalVideoName, Location=OrigionalVideoNameDirectory):
            lf.RegisterKillMe()

        ProcessedVideoName = gu.GenerateProperVideoName(InitialName=OrigionalVideoName, Resolution=Resolution)
        ProcessedVideoNameDirectory = gu.GenerateNameDirectory(ID=ProcessedVideoName)
        
        if not pr.ProcessVideo(InputFilename=OrigionalVideoNameDirectory, OutputFilename=ProcessedVideoNameDirectory, Resolution=Resolution):
            lf.CleanUp(message=message)
            qu.ReleaseMessage(message=message)
            continue

        if not s3u.UploadFile(ID=ProcessedVideoName, Location=ProcessedVideoNameDirectory):
            qu.ReleaseMessage(message=message)
            lf.RegisterKillMe()

        if not ru.UpdateStatusFunc(Keys=[OrigionalVideoName, Resolution , gu.GenerateLastRedisField(ID=OrigionalVideoName)]):
            qu.ReleaseMessage(message=message)
            lf.RegisterKillMe()
            

        Result = ru.AmILastFunc(Keys=[OrigionalVideoName , gu.GenerateLastRedisField(ID=OrigionalVideoName)])

        if not Result:
            qu.ReleaseMessage(message=message)
            lf.RegisterKillMe()
            

        if Result.pop(0):
            AllVideoNamesDirectory =[]

            for res in Result:
                Name = gu.GenerateProperVideoName(InitialName=OrigionalVideoName, Resolution=res)

                NameDirectory = gu.GenerateNameDirectory(ID=Name)

                AllVideoNamesDirectory.append(NameDirectory)

                if not s3u.DownloadProcessedFile(ID=Name, Location=NameDirectory):
                    qu.ReleaseMessage(message=message)
                    lf.RegisterKillMe()

            SoundFileName = gu.GenerateProperAudioName(InitialName=OrigionalVideoName)

            SoundFileNameDirectory = gu.GenerateNameDirectory(ID=SoundFileName)

            pr.ProcessSoundTrack(InputFilename=OrigionalVideoNameDirectory, OutputFilename=SoundFileNameDirectory)

            s3u.UploadFile(ID=SoundFileName, Location=SoundFileNameDirectory)


            ThumbnailName = gu.GenerateProperThumbnailName(ID=OrigionalVideoName)

            ThumbnailNameDirectory = gu.GenerateNameDirectory(ThumbnailName)

            pr.CreateThumbnail(InputFilename=OrigionalVideoNameDirectory, OutputFilename=ThumbnailNameDirectory)

            s3u.UploadFile(ID=ThumbnailName, Location=ThumbnailNameDirectory)


            MpdName = gu.GenerateProperMpdName(ID=OrigionalVideoName)

            MpdNameDirectory = gu.GenerateNameDirectory(MpdName)

            pr.CreateMPD(InputStreams=[AllVideoNamesDirectory , [SoundFileNameDirectory]], OutputFilename=MpdNameDirectory)

            s3u.UploadFile(ID=MpdName, Location=MpdNameDirectory)


            FinishTask(ID=OrigionalVideoName, Resolutions=Result, message=message)
        else:

            if not qu.DeleteMessage(message=message):
                lf.RegisterKillMe()

        lf.CleanUp()



    return




main()
