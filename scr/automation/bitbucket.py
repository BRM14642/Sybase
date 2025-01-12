import os
from dotenv import load_dotenv
import requests
load_dotenv()


class Bitbucket:
    def __init__(self):
        self.bibucket_domain = os.getenv("BITBUCKET_DOMAIN")
        self.url = os.getenv("BITBUCKET_URL")
        self.auth = (os.getenv("BITBUCKET_USER"), os.getenv("BITBUCKET_PASSWORD"))

    def download_file(self, repository, remote_file_path, branch):
        file_path = "../../scripts/downloaded/" + remote_file_path
        url = f"{self.bibucket_domain}/projects/SYB16/repos/{repository}/raw/{remote_file_path}?at={branch}"

        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
                print(f"Archivo {file_path} descargado correctamente.")
                return file_path
        else:
            print(f"Error al descargar el archivo: {response.status_code} - {response.text}")
            return None

    def download_file_to(self, output_path, repository, remote_file_path, branch):
        file_path = output_path
        url = f"{self.bibucket_domain}/projects/SYB16/repos/{repository}/raw/{remote_file_path}?at={branch}"

        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
                print(f"Archivo {file_path} descargado correctamente.")
                return file_path
        else:
            print(f"Error al descargar el archivo: {response.status_code} - {response.text}")
            return None