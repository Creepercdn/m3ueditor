# Just a sutpid parser
class M3U8(object):
    def __init__(self, extm3u, filelist):
        self.filelist=filelist
        self.extm3u=extm3u
    def dumps(self):
        result=''
        if self.extm3u:
            result+='#EXTM3U\n'
        for i in self.filelist:
            result+=i
            result+='\n'
        return result


def loads(text: str):
    extm3u = False
    starti = 0
    tsl = text.splitlines(False)
    flist = []
    if tsl:
        if tsl[0]=='#EXTM3U':
            extm3u = True
            starti += 1
        for i in range(len(tsl)):
            if(i<starti):
                continue
            flist.append(tsl[i])
        return M3U8(extm3u, flist)
    else:
        return M3U8(False, [])
