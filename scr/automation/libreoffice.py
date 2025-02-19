import subprocess
import time
from scr.utils.logging_config import logger

class LibreOffice:
    @staticmethod
    def start_libreoffice_headless():
        libreoffice_cmd = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "--headless",
            "--accept=socket,host=localhost,port=2002;urp;"
        ]
        process = subprocess.Popen(libreoffice_cmd)
        time.sleep(5)  # Wait for LibreOffice to start
        logger.info("LibreOffice port started")
        return process

    @staticmethod
    def stop_libreoffice_headless(process):
        process.terminate()
        process.wait()
        logger.info("LibreOffice port stopped")