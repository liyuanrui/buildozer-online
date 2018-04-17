#coding=utf-8
#qpy:kivy
#qpy:fullscreen

import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.core.text import LabelBase
from kivy.core.window import WindowBase
from kivy.clock import Clock
import rpyc
import os

WindowBase.softinput_mode='below_target'
LabelBase.register(name='Roboto',fn_regular='droid.ttf')

class S:
    a1=False
    a2=False
    a3=False
    a4=False
    a5=False
    a6=False
    a7=False
    a8=False
    action=False
 
def decode(string):
    try:
        return string.decode('utf-8')
    except:
        return string
        
def checkcn(string):
    for ch in decode(string):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

class MyLayout(BoxLayout):
    
    def start(self):
        pyver = self.ids.pyver.text
        project0 = self.ids.project.text
        title = self.ids.title.text
        fullscreen = self.ids.fullscreen.text
        package = self.ids.package.text.split('.')
        name = package[-1]
        domain = '.'.join(package[:-1])
        version = self.ids.version.text
        orientation = self.ids.orientation.text
        requirements = self.ids.requirements.text
        permissions = self.ids.permissions.text
        email = self.ids.email.text

        if not S.a1&S.a2&S.a3&S.a4&S.a5&S.a6&S.a7&S.a8:
            self.ids.button.text='输入有误，请检查非法参数'
            return 1           
        if S.action:
            self.ids.button.text='已提交任务,如有新任务请重启app'
            return 1
        
        project = {}
        os.chdir(project0)
        dirs = [i[0] for i in os.walk('.') if i[0] !='.']
        
        for i in os.walk('.'):
            for j in i[2]:
                fname = i[0]+'/'+j
                with open(fname,'rb') as f:
                    project[fname]=f.read()
        
        #exit()
        c = rpyc.connect('111.230.24.37',30033)
        
        pcount = c.root.start(pyver,project,dirs,title,name,domain,version,requirements,permissions,email,fullscreen,orientation)
        c.close()
        S.action=True
        self.ids.button.text='队列位置:%s, 预计等待%s分钟'%(pcount,pcount*15)
        

class MainApp(App):
    theme_cls = ThemeManager()
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return MyLayout()
        
    def checkinput(self,nap):
        if S.action:return 1
        pyver = self.root.ids.pyver
        project = self.root.ids.project
        title = self.root.ids.title
        fullscreen = self.root.ids.fullscreen
        package = self.root.ids.package
        version = self.root.ids.version
        orientation = self.root.ids.orientation
        requirements = self.root.ids.requirements
        permissions = self.root.ids.permissions
        email = self.root.ids.email
        button = self.root.ids.button
        
        # a1
        if not os.path.exists(project.text)&os.path.exists(project.text+'/main.py'):
            project.hint_text='非法参数(路径或main.py不存在)'
            S.a1=False
        else:
            project.hint_text='项目路径'                  
            S.a1=True
        # a2
        if not ('@' in email.text and '.' in email.text):
            email.hint_text='非法参数(请输入邮箱)'
            S.a2=False
        else:
            email.hint_text='邮箱'
            S.a2=True
        # a3
        if checkcn(title.text) or title.text=='':
            title.hint_text='非法参数(只能英文)'
            S.a3=False
        else:
            title.hint_text='app名称'
            S.a3=True
        #a4
        if not fullscreen.text in ('True','False'):
            fullscreen.hint_text='非法参数(True or False)'
            S.a4=False
        else:
            fullscreen.hint_text='覆盖通知栏'
            S.a4=True
        #a5
        if not (len(package.text.split('.'))==3 and package.text.split('.')[-1]!=''):
            package.hint_text='非法参数(x.y.z)'
            S.a5=False
        else:
            package.hint_text='app包名'
            S.a5=True
        #a6
        if not orientation.text in ('portrait','landscape','all'):
            orientation.hint_text='非法参数'
            S.a6=False
        else:
            orientation.hint_text='屏幕方向'
            S.a6=True
        #a7
        if version.text=='':
            version.hint_text='非法参数'
            S.a7=False
        else:
            version.hint_text='app版本'
            S.a7=True
        #a8
        if pyver.text=='':
            pyver.hint_text='非法参数'
            S.a8=False
        else:
            pyver.hint_text='python版本'
            S.a8=True


            
        if S.a1&S.a2&S.a3&S.a4&S.a5&S.a6&S.a7&S.a8:
            button.text='提交打包任务'
        else:
            button.text='输入有误，请检查非法参数'
    
    def on_start(self):
        Clock.schedule_interval(self.checkinput,0)
MainApp().run()