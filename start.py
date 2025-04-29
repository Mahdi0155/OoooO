from threading import Thread
from uploader_bot import app as uploader_app
from checker_bot import checker_app

if __name__ == '__main__':
    Thread(target=lambda: uploader_app.run(host='0.0.0.0', port=5000)).start()
    Thread(target=lambda: checker_app.run(host='0.0.0.0', port=5001)).start()
