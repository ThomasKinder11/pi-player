import os
import json
import sys

import includes

def writePlaylist(dstPath, fileList):
    if not isinstance(fileList, list):
        return False

    if not os.path.exists(dstPath):
        return False

    i = 0
    rootDict = {}

    print('length fileList  = {}'.format(len(fileList)))
    for item in fileList:

        itemDict = {}
        itemDict['path'] = item
        itemDict['name'] = os.path.basename(item)
        itemDict['post'] = ""
        itemDict['pre'] = ""
        itemDict['start'] = 0
        itemDict['end'] = 0

        rootDict[i]=itemDict

        i = i + 1

    #convert dict to json
    tmp = json.dumps(rootDict, indent=4, sort_keys=False)

    with open(os.path.join(dstPath, 'playlist.json'), "w") as f:
      f.write(tmp)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('please specify media file diretory and destination directory...')
        sys.exit(0)

    dir = sys.argv[1]
    if not os.path.isdir(dir):
        print('specified source path is not a directory...')
        sys.exit(0)

    dirDest = sys.argv[2]
    if not os.path.isdir(dirDest):
        print('specified destination path is not a directory...')
        sys.exit(0)

    files = os.listdir(dir)

    videoFormats =  tuple(includes.config['video']['types'].split(','))
    audioFormats = tuple(includes.config['music']['types'].split(','))

    playlistFiles = []
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            print(file)
            if path.lower().endswith(videoFormats) or path.lower().endswith(audioFormats):
                playlistFiles.append(path)

    writePlaylist(dirDest, playlistFiles)
