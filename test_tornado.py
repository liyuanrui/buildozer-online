import tornado.ioloop
import tornado.web
import shutil
import os

class UploadFileHandler(tornado.web.RequestHandler):
    def get(self):
        filename=self.get_argument('filename')
        self.set_header ('Content-Type', 'application/octet-stream')
        self.set_header ('Content-Disposition', 'attachment; filename='+filename)
        with open(filename, 'rb') as f:
            data=f.read()
            self.write(data)
        self.finish()

app=tornado.web.Application([
    (r'/',UploadFileHandler),
])

if __name__ == '__main__':
    app.listen(30044)
    tornado.ioloop.IOLoop.instance().start()
