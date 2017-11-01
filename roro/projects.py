import os
import shutil
import yaml
from . import models, config
from .client import Client
from .helpers import PY2
from click import ClickException

if PY2:
    from backports import tempfile
else:
    import tempfile


class Project:
    def __init__(self, name, runtime=None):
        self.name = name
        self.runtime = runtime
        self.client = Client(config.SERVER_URL)

    def create(self):
        return self.client.create(name=self.name)

    def run(self, command, instance_size=None):
        job = self.client.run(project=self.name, command=command, instance_size=instance_size)
        return job

    def stop(self, jobid):
        self.client.stop(project=self.name, jobid=jobid)

    def run_notebook(self, instance_size=None):
        job = self.client.run_notebook(project=self.name, instance_size=instance_size)
        return job

    def ps(self, jobid=None, all=False):
        return self.client.ps(project=self.name, jobid=jobid, all=all)

    def ls(self, path):
        return self.client.ls_volume(
            project=self.name,
            volume=path.volume,
            path=path.path
        )

    def logs(self, jobid):
        return self.client.logs(project=self.name, jobid=jobid)
        #return self.client.logs(project=self.name)

    def deploy(self):
        print("Deploying project {}. This may take a few moments ...".format(self.name))
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = self.archive(tmpdir)
            size = os.path.getsize(archive)
            with open(archive, 'rb') as f:
                format = 'tar'
                response =  self.client.deploy(
                    project=self.name,
                    archived_project=f,
                    size=size,
                    format=format
                )
            return response

    def archive(self, rootdir, format='tar'):
        base_name = os.path.join(rootdir, "roro-project-" + self.name)
        return shutil.make_archive(base_name, format)

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

    def get_model_repository(self, name):
        """Returns the ModelRepository from this project with given name.
        """
        return models.get_model_repository(client=self.client, project=self.name, name=name)

    def list_model_repositories(self):
        """Returns a list of all the ModelRepository objects present in this project.
        """
        return models.list_model_repositories(client=self.client, project=self.name)

    def get_model_activity(self, repo=None):
        response = self.client.get_activity(project=self.name, name=repo)
        return [models.ModelImage.from_activity(project=self, metadata=x) for x in response]

    def copy(self, src, dest):
        if src.is_volume():
            self._get_file(src, dest)
        else:
            self._put_file(src, dest)

    def _get_file(self, src, dest):
        fileobj = self.client.get_file(
            project=self.name,
            volume=src.volume,
            path=src.path
        )
        dest.safe_write(fileobj, src.name)

    def _put_file(self, src, dest):
        with src.open('rb') as fileobj:
            self.client.put_file(
                project=self.name,
                fileobj=fileobj,
                volume=dest.volume,
                path=dest.path,
                name=src.name,
                size=src.size
            )

    @staticmethod
    def find_all():
        client = Client(config.SERVER_URL)
        projects = client.projects()
        return [Project(p['name'], p.get('runtime')) for p in projects]

    @staticmethod
    def find(name):
        client = Client(config.SERVER_URL)
        p = client.get_project(name)
        return p and Project(p['name'], p.get('runtime'))

    def __repr__(self):
        return "<Project {}>".format(self.name)

def current_project():
    if os.path.exists("roro.yml"):
        d = yaml.safe_load(open("roro.yml"))
        return Project(d['project'], d.get('runtime'))
    else:
        raise ClickException("Unable to find roro.yml")

get_current_project = current_project

def list_projects():
    return Project.find_all()
