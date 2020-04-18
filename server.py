from rpyc import Service
from rpyc.utils.server import ThreadedServer
import uuid
import os
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


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

def sendmail(To,filename):
    #构建邮件头
    message = MIMEMultipart()
    message['From'] = Header("Buildozer Online", 'utf-8')
    message['To'] =  Header(To, 'utf-8')
    message['Subject'] = Header('Buildozer Online', 'utf-8')
 
    #邮件正文内容
    if filename[-3:] == 'apk':
        content='恭喜! 打包成功, 请查收附件'
    else:
        content='抱歉! 打包失败, 请检查日志'
    message.attach(MIMEText(content, 'plain', 'utf-8'))

    # 构造附件
    att1 = MIMEText(open(filename, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1["Content-Disposition"] = 'attachment; filename="%s"'%filename.split('/')[-1]
    message.attach(att1)

    # 发送邮件
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.exmail.qq.com')
        smtpObj.login('cv@lr.cool', 'xxxxxxxxxx')
        smtpObj.sendmail('qpython@lr.cool', To, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败: %s"%e)
    else:
        smtpObj.quit()

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

    if os.path.exists('%spresplash.png'%filepath):
        oread[48] = 'presplash.filename = '+home+'/'+uid+'/presplash.png'

    if os.path.exists('%sicon.png'%filepath):
        oread[51] = 'icon.filename = '+home+'/'+uid+'/icon.png'

    if 'WAKE_LOCK' in permissions:
        oread[169] = 'android.wakelock = True'

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

