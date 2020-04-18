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

def run(task):
    uid,pyver,email = task
    filepath=home+'/'+uid+'/'

    os.system('cp -a /home/pi/test/.buildozer %s'%filepath)

    try:
        os.system('cd %s &&buildozer android debug >build.log'%filepath) 
        apk = [i for i in os.listdir('bin') if i[-3:]=='apk']
        if apk:
            sendmail(email, filepath+'bin'+apk[0])
            # copy sucessful recipe
            buildlist = [i for i in os.listdir('.buildozer/android/platform') if i[:5] == 'build']
            for i in buildlist:
                current_i = filepath + '.buildozer/android/platform/' + i
                release_i = '/home/pi/test/.buildozer/android/platform/' + i
                # copy other_builds
                current_other = current_i+'/build/other_builds/'
                release_other = release_i+'/build/other_builds/'
                if not os.path.exists(release_other):
                    os.makedirs(release_other)
                current_other_list = os.listdir(current_other)
                release_other_list = os.listdir(release_other)
                for o in current_other_list:
                    if not o in release_other_list:
                        print('copy other_build %s'%o)
                        os.system('cp -a %s %s'%(current_other+o, release_other))
                # copy packages
                current_package = current_i+'/packages/'
                release_package = release_i+'/packages/'
                if not os.path.exists(release_package):
                    os.makedirs(release_package)
                current_package_list = os.listdir(current_package)
                release_package_list = os.listdir(release_package)
                for p in current_package_list:
                    if not p in release_package_list:
                        print('copy package %s'%p)
                        os.system('cp -a %s %s'%(current_package+p, release_package))
        else:
            sendmail(email, filepath+'build.log')
    except:
        sendmail(email, filepath+'build.log')
    finally:
        os.system('rm -rf ' + filepath)

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

