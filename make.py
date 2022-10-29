import os
import subprocess
from subprocess import Popen
import json
import pip


class Executor:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        return subprocess.run(self.args)

    def __set__(self, instance, value: tuple[str]):
        self.args = value


class BuildSystem:
    install_docker = Executor()
    install_dockerio = Executor()
    set_docker_socket_access = Executor()
    install_yc = Executor()
    auth_user = Executor()
    a = Executor()
    create_iam = Executor()
    go_to_cert_root = Executor()
    generate_certs = Executor()

    def __init__(self, cloudconfigs: dict):


        self.install_yc = "curl", "-sSL", "https://storage.yandexcloud.net/yandexcloud-yc/install.sh", "|", "bash", "-s"
        self.auth_user = "yc", "config", "set", "token", cloudconfigs['OAuth']

        self.create_iam = "yc", "iam", "key", "create", "--service-account-name", cloudconfigs[
            'sa'], "--output", "key.json", "--folder-id", cloudconfigs["folder-id"]

        self.go_to_cert_root = f"cd", f"{cloudconfigs['volume']}"

        self.generate_certs = ("yc", "certificate-manager",
                               "certificate", "content",
                               "--id", cloudconfigs['certid'],

                               "--chain", f"{cloudconfigs['volume']}/certificate_full_chain.pem",
                               "--key", f"{cloudconfigs['volume']}/private_key.pem")


        self.dockerfile = f"""
FROM python:3.9
WORKDIR /{cloudconfigs["container_root"]}
COPY ./requirements.txt /{cloudconfigs["container_root"]}/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /{cloudconfigs["container_root"]}/requirements.txt
COPY ./main.py /{cloudconfigs["container_root"]}/main.py
COPY ./cxm /{cloudconfigs["container_root"]}/cxm
ENV AWS_ACCESS_KEY_ID={cloudconfigs['key-id']}, AWS_SECRET_ACCESS_KEY={cloudconfigs['acces-key']},AWS_DEFAULT_REGION={cloudconfigs['region']}
VOLUME ["{cloudconfigs['container_root']}/{cloudconfigs['volume']}"]
CMD ["python", "main.py"]"""

    def run(self):
        if os.getenv("OS")=='OSX':
            calls = (
                self.install_yc,
                self.auth_user,
                self.create_iam,
                self.go_to_cert_root,
                self.generate_certs)
        elif os.getenv("OS")!='Win':

            calls = (

                self.install_yc,
                self.auth_user,
                self.create_iam,
                self.go_to_cert_root,
                self.generate_certs)
        else:
            raise "Windows Docker is currently not supported :("
        for call in calls:
            try:
                subprocess.run(call)
                print(f"\n\n\nSUCCSESS {call}\n\n\n\n"
                      )
                print(call)
            except:
                #subprocess.run(call)
                print(f"\n\n\nGOVNO {call}\n\n\n\n"
                      )
                print(call)

        with open(f"Dockerfile", "w") as dcf:
            dcf.write(self.dockerfile)


if __name__ == "__main__":
    with open("cloudconfig.json", "r") as cloudconfigfile:
        cloudconfigs = json.load(cloudconfigfile)

    BuildSystem(cloudconfigs).run()
    subprocess.run(["docker", "build" ])
