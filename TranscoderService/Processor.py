from Log import *
import subprocess as sp



def CreateMPD(InputStreams, OutputFilename):

    cmd = ["ffmpeg"]

    VideoFile_cmd = ["-f","webm_dash_manifest","-i"]
    
    AllMaps_cmd = []
    Maps_cmd = ["-map"]

    AdaptationSet_cmd = ["-adaptation_sets"]

    ForceMPD = ["-f", "webm_dash_manifest"]


    SetId = 0
    AdaptationSet_str = ""
    FileNum = 0
    StreamNum = 0
    NumStream = len(InputStreams)
    for InputFilename in InputStreams:
        AdaptationSet_str += "id="+str(SetId) + ","
        AdaptationSet_str += "streams="


        StreamLen = len(InputFilename)
        for InputFilename in InputFilename:

            tmp_cmd = list(VideoFile_cmd)
            tmp_cmd.append(InputFilename)
            cmd.extend(tmp_cmd)

            tmp_cmd = list(Maps_cmd)
            tmp_cmd.append(str(FileNum))
            AllMaps_cmd.extend(tmp_cmd)

            AdaptationSet_str += str(FileNum)


            FileNum += 1
            if FileNum >= StreamLen:
                continue

            AdaptationSet_str += ","
            
        SetId += 1
        StreamNum += 1

        if StreamNum >= StreamLen:
            continue

        AdaptationSet_str += " "


    print(str(cmd))
    print(str(AllMaps_cmd))
    print(AdaptationSet_str)

    Copy_cmd = ["-c","copy"]

    cmd.extend(Copy_cmd)
    cmd.extend(AllMaps_cmd)
    cmd.extend(ForceMPD)
    AdaptationSet_cmd.append(AdaptationSet_str)
    cmd += AdaptationSet_cmd

    cmd.append(OutputFilename)

    print(cmd)
    
    try:
        if sp.run(cmd, timeout=500000).returncode:
            return 0
        return 1
    except Exception as e:
        return 0
    


def CreateThumbnail(InputFilename, OutputFilename):
    cmd = ["ffmpeg","-y","-i",InputFilename,"-ss","00:00:14","-frames:v","1", OutputFilename]
    try:
        if sp.run(cmd, timeout=500000).returncode:
            return 0
        return 1
    except Exception as e:
        return 0

def ProcessSoundTrack(InputFilename , OutputFilename):

    cmd = ["ffmpeg","-y","-i",InputFilename,"-vn","-acodec","libvorbis","-ab","500k","-dash","1", OutputFilename]

    try:
        if sp.run(cmd, timeout=500000).returncode:
            return 0
        return 1
    except Exception as e:
        return 0


def ProcessVideo(InputFilename , OutputFilename, Resolution):

    cmd = ["ffmpeg" ,"-y", "-i" , InputFilename , "-c:v", "libsvtav1", "-keyint_min", "150", "-g","150","-tile-columns","4","-frame-parallel", "1" , "-f","webm","-dash", "1" , "-an", "-vf" ,"scale=" + Resolution , "-b:v", "250k", "-dash", "1" , OutputFilename]

    print(str(cmd))

    try:
        if sp.run(cmd, timeout=500000).returncode:
            return 0
        return 1
    except Exception as e:
        return 0

if __name__ == "__main__":
    
    Storage_Directory = "TranscoderService/Vide/"
    
    print("Proccessed Video Return : " + str(ProcessVideo("TranscoderService/Shin", Storage_Directory +"9999-640x360" + ".webm", "360x100")))
    
    print("Proccessed Video Return : " + str(ProcessVideo("TranscoderService/Shin", Storage_Directory + "9999-1280x720" + ".webm", "1280x720")))
    
    print("Proccessed Sound Return " + str(ProcessSoundTrack("TranscoderService/Shin",Storage_Directory + "9999-audio" + ".webm")))
    
    print("Processed Thumbnail Return : " + str(CreateThumbnail("TranscoderService/Shin", Storage_Directory + "9999-thumbnail" +".png")))
    
    print("Processed Mpd Return : " + str(CreateMPD([[Storage_Directory + "9999-640x360.webm",Storage_Directory + "9999-1280x720.webm"], [Storage_Directory + "9999-audio.webm"]], Storage_Directory + "9999-testm.mpd")))

    Storage_Directory = "TranscoderService/Videos/"

    print("Proccessed Video Return : " + str(ProcessVideo("TranscoderService/Shin", Storage_Directory +"9999-640x360" + ".webm", "360x100")))
    
    print("Proccessed Video Return : " + str(ProcessVideo("TranscoderService/Shin", Storage_Directory + "9999-1280x720" + ".webm", "1280x720")))
    
    print("Proccessed Sound Return " + str(ProcessSoundTrack("TranscoderService/Shin",Storage_Directory + "9999-audio" + ".webm")))
    
    print("Processed Thumbnail Return : " + str(CreateThumbnail("TranscoderService/Shin", Storage_Directory + "9999-thumbnail" +".png")))
    
    print("Processed Mpd Return : " + str(CreateMPD([[Storage_Directory + "9999-640x360.webm",Storage_Directory + "9999-1280x720.webm"], [Storage_Directory + "9999-audio.webm"]], Storage_Directory + "9999-testm.mpd")))

