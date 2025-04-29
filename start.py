from checker import checker_app
from uploader import uploader_app
from threading import Thread

def run_checker():
    checker_app.run(host="0.0.0.0", port=5000)

def run_uploader():
    uploader_app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    Thread(target=run_checker).start()
    Thread(target=run_uploader).start()
