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

class Sign:
    plist = []

def sendmail(To,filename):
    print(filename)
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
        smtpObj.login('qpython@lr.cool', 'rpyc8023RPYC')
        smtpObj.sendmail('qpython@lr.cool', To, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败: %s"%e)
    else:
        smtpObj.quit()

def run(task):
    uid,pyver,email = task
    filepath=home+'/'+uid+'/'
    # 共用packages和python-for-android, 巧妙的映射
    os.makedirs(filepath+'.buildozer/android/platform/build-'+pyver)
    os.system('ln -s /home/pi/packages '+filepath+'.buildozer/android/platform/build-'+pyver+'/packages')
    os.system('ln -s /home/pi/python-for-android '+filepath+'.buildozer/android/platform/python-for-android')

    try:
        os.system('cd %s &&buildozer android debug >build.log'%filepath) 
        apk = [i for i in os.listdir(filepath+'bin') if i[-3:]=='apk']
        if apk:
            sendmail(email, filepath+'bin/'+apk[0])
        else:
            sendmail(email, filepath+'build.log')
    except Exception as e:
        traceback.print_exc()
        sendmail(email, filepath+'build.log')
    finally:
        os.system('rm -rf ' + filepath)
        os.system('rm -rf /home/pi/python-for-android/*.apk')


def build():
    while True:
        time.sleep(30)
        try:
            task = Sign.plist.pop(0)
            print(task)
            run(task)
        except Exception as e:
            ctime=time.ctime()[11:19]
            print(ctime,e)

def write_project(project,dirs):
    uid=uuid.uuid1().hex
    filepath=home+'/'+uid+'/'
    os.mkdir(filepath)
    for i in dirs:
        os.makedirs(filepath+i)
    for name in project:
        with open(filepath+name,'wb') as f:
            f.write(project[name])
    return uid

def init_buildozer(uid,pyver,title,name,domain,version,requirements,permissions,fullscreen,orientation):
    filepath=home+'/'+uid+'/'
    os.system('cp /home/kivydev/buildozer-py3/buildozer.spec %s'%filepath)
    with open('%sbuildozer.spec'%filepath,'r') as f:
        oread = f.read().strip().split('\n')

    oread[3] = 'title = '+title
    oread[6] = 'package.name = '+name
    oread[9] = 'package.domain = '+domain
    oread[30] = 'version = '+version
    oread[38] = 'requirements = '+requirements
    oread[54] = 'orientation = '+orientation

    if eval(fullscreen):
        oread[77] = 'fullscreen = 1'
    else:
        oread[77] = 'fullscreen = 0'

    if permissions:
        oread[87] = 'android.permissions = '+permissions

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
        uid = write_project(project,dirs)
        init_buildozer(uid,pyver,title,name,domain,version,requirements,permissions,fullscreen,orientation)
        Sign.plist.append([uid,pyver,email])
        pcmd = os.popen('ls /home/kivydev/buildenv').read().split('\n')[:-1]
        pcount = len(pcmd)
        return pcount
        

if __name__ == '__main__':
    s = ThreadedServer(Build,port = 30033, auto_register=False)
    threading._start_new_thread(build,())
    s.start()

