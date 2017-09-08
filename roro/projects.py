import os
import yaml
import firefly

SERVER_URL = "https://api.rorocloud.io/"

def login(email, password):
    client = firefly.Client(SERVER_URL)
    return client.login(email=email, password=password)

class Project:
    def __init__(self, name, runtime=None):
        self.name = name
        self.runtime = runtime
        self.client = firefly.Client(SERVER_URL)

    def create(self):
        return self.client.create(name=self.name)

    def run(self, command):
        job = self.client.run(project=self.name, command=command)
        return job

    def stop(self, jobid):
        self.client.stop(project=self.name, jobid=jobid)

    def ps(self):
        return self.client.ps(project=self.name)

    def logs(self, jobid):
        return self.client.logs(project=self.name, jobid=jobid)
        #return self.client.logs(project=self.name)

    def get_config(self):
        return self.client.get_config(project=self.name)

    def set_config(self, config_vars):
        return self.client.set_config(project=self.name, config_vars=config_vars)

    def unset_config(self, names):
        return self.client.unset_config(project=self.name, names=names)

    def list_volumes(self):
        volumes = self.client.volumes(project=self.name)
        return [volume['volume'] for volume in volumes]

    def add_volume(self, volume_name):
        volume =  self.client.add_volume(project=self.name, name=volume_name)
        return volume['volume']

def current_project():
    if os.path.exists("roro.yml"):
        d = yaml.safe_load(open("roro.yml"))
        return Project(d['project'], d.get('runtime', 'python36'))
    else:
        raise Exception("Unable to find roro.yml")
