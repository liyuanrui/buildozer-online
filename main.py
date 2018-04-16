#coding=utf-8
#qpy:kivy

import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.core.text import LabelBase
from kivy.core.window import WindowBase
import rpyc
import os

WindowBase.softinput_mode='below_target'
LabelBase.register(name='Roboto',fn_regular='droid.ttf')

class MyLayout(BoxLayout):
    sign=False
    def start(self):
        pyver = self.ids.pyver.text
        project0 = self.ids.project.text
        title = self.ids.title.text
        name = self.ids.name.text
        domain = self.ids.domain.text
        version = self.ids.version.text
        requirements = self.ids.requirements.text
        permissions = self.ids.permissions.text
        email = self.ids.email.text
        
        if email == '':
            self.ids.button.text='打包(请输入邮箱)'
            return 1
        if self.sign:
            self.ids.button.text='已提交任务,如有新任务请重启app'
            return 1
        self.ids.button.text='上传中...'
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
        
        c.root.start(pyver,project,dirs,title,name,domain,version,requirements,permissions,email)
        c.close()
        self.sign=True
        self.ids.button.text='打包中，请留意邮件'
        

class MainApp(App):
    theme_cls = ThemeManager()
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return MyLayout()

MainApp().run()