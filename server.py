from rpyc import Service
from rpyc.utils.server import ThreadedServer
import uuid
import os
import time
import threading
import smtplib


home = '/home/kivydev/buildenv'
if not os.path.exists(home):
    os.mkdir(home)


def encode(string):
    try:
        string=string.encode('utf-8')
    except:
        string=string
    finally:
        return string

class Sign:
    plist = []

def sendmail(email,filename=None):
    smtp=smtplib.SMTP()
    smtp.connect('smtp.exmail.qq.com')
    smtp.login('cv@lr.cool','rpyc8023RPYC')
    message = 'From:cv@lr.cool\nTo:%s\nSubject:Buildozer APK\n\n'%email
    if filename:
        message+='build successful.download it.\n http://111.230.24.37:30044/?filename=%s'%filename[0]
    else:
        message+='build failed, please check requirements.'
    smtp.sendmail('cv@lr.cool', email, message)
    smtp.quit()

def run(nl):
    uid,pyver,email = nl
    filepath=home+'/'+uid+'/'
    if pyver == 'python2':
        os.system('cp -a /home/kivydev/buildozer-py2/.buildozer %s'%filepath)
    else:
        os.system('cp -a /home/kivydev/buildozer-py3/.buildozer %s'%filepath)

    try:
        os.system('cd %s && buildozer android debug'%filepath) 
    except:
        os.system('rm -rf '+home+'/'+uid)

    try:
        sf = [j for i in os.walk('%sbin'%filepath) for j in i[2]]
        os.system('cp %sbin/%s /home/kivydev/apks/%s-%s'%(filepath,sf[0],uid[:20],sf[0]))
        sf[0]=uid[:20]+'-'+sf[0]
    except:
        sendmail(email)
    else:
        sendmail(email,sf)
    os.system('rm -rf '+home+'/'+uid)

def build():
    while True:
        time.sleep(30)
        try:
            nl = Sign.plist.pop(0)
            print(nl)
            run(nl)
        except Exception as e:
            ctime=time.ctime()[11:19]
            print(ctime,e)

def write_project(project,dirs):
    uiid=uuid.uuid1().hex
    filepath=home+'/'+uiid+'/'
    os.mkdir(filepath)
    for i in dirs:
        os.makedirs(filepath+i)
    for name in project:
        with open(filepath+name,'wb') as f:
            f.write(project[name])
    return uiid

def init_buildozer(uid,pyver,title,name,domain,version,requirements,permissions,fullscreen,orientation):
    filepath=home+'/'+uid+'/'
    if pyver == 'python2':
        os.system('cp /home/kivydev/buildozer-py2/buildozer.spec %s'%filepath)
    else:
        os.system('cp /home/kivydev/buildozer-py3/buildozer.spec %s'%filepath)
    with open('%sbuildozer.spec'%filepath,'r') as f:
        oread = f.read().strip().split('\n')

    oread[3] = 'title = '+encode(title)
    oread[6] = 'package.name = '+encode(name)
    oread[9] = 'package.domain = '+encode(domain)
    oread[30] = 'version = '+encode(version)
    oread[38] = 'requirements = '+encode(requirements)
    oread[54] = 'orientation = '+encode(orientation)

    if eval(fullscreen):
        oread[77] = 'fullscreen = 1'
    else:
        oread[77] = 'fullscreen = 0'

    if permissions:
        oread[87] = 'android.permissions = '+encode(permissions)

    if os.path.exists('icon.png'):
        oread[51] = 'icon.filename = '+home+'/'+uid+'/icon.png'

    nr = '\n'.join(oread)
    with open('%sbuildozer.spec'%filepath,'w') as f:f.write(nr)



    
class Build(Service):
    def exposed_start(self,pyver,project,dirs,title,name,domain,version,requirements,permissions,email,fullscreen,orientation):
        uiid = write_project(project,dirs)
        init_buildozer(uiid,pyver,title,name,domain,version,requirements,permissions,fullscreen,orientation)
        Sign.plist.append([uiid,pyver,email])
        pcmd = os.popen('ls /home/kivydev/buildenv').read().split('\n')[:-1]
        pcount = len(pcmd)
        return pcount
        

if __name__ == '__main__':
    s = ThreadedServer(Build,port = 30033, auto_register=False)
    threading._start_new_thread(build,())
    s.start()

