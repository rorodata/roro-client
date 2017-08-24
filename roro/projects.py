import os
import yaml
import firefly

SERVER_URL = "https://api.rorodata.com/"

def login(email, password):
    client = firefly.Client(SERVER_URL)
    return client.login(email=email, password=password)

class Project:
    def __init__(self, name, runtime):
        self.name = name
        self.runtime = runtime
        self.client = firefly.Client(SERVER_URL)

    def run(self, command):
        job = self.client.run(project=self.name, command=command)
        return job

    def ps(self):
        return self.client.ps(project=self.name)

    def logs(self, jobid):
        return self.client.logs(project=self.name, jobid=jobid)
        #return self.client.logs(project=self.name)

def current_project():
    if os.path.exists("roro.yml"):
        d = yaml.safe_load(open("roro.yml"))
        return Project(d['project'], d.get('runtime', 'python36'))
    else:
        raise Exception("Unable to find roro.yml")
