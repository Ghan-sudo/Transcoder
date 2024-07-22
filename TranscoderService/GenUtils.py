
Storage_Directory = "Videos/"
LastFieldVal = "-Last"

def __init__():
    return

def GenerateProperVideoName(InitialName, Resolution):
    return str(InitialName + "-" + Resolution + ".webm")

def GenerateProperAudioName(InitialName):
    return str(InitialName + "-audio.webm")

def GenerateProperThumbnailName(ID):
    return str(ID + "-thumbnail.png")

def GenerateProperMpdName(ID):
    return str(ID + ".mpd")

def GenerateLastRedisField(ID):
    return str(ID + LastFieldVal)

def GenerateNameDirectory(ID):
    return Storage_Directory + ID

if __name__ == "__main__":

    ID = "shin"
    Resolution = "1080x920"

    print("ID : " + ID)

    print("ProperVideoName : " + GenerateProperVideoName(InitialName=ID , Resolution=Resolution))

    print("ProperAudioName : " + GenerateProperAudioName(InitialName=ID))

    print("ProperThumbnailName : " + GenerateProperThumbnailName(ID=ID))

    print("ProperMpdName : " + GenerateProperMpdName(ID=ID))

    print("RedisLastField : " + GenerateLastRedisField(ID=ID))

    print("ProperNameDirectory : " + GenerateNameDirectory(ID=ID))
