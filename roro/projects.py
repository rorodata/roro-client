import os
import shutil
import yaml
import time
from . import models, config
from .client import RoroClient
from .helpers import PY2
from click import ClickException

if PY2:
    from backports import tempfile
else:
    import tempfile


class Project:
    SERVER_URL = config.SERVER_URL

    def __init__(self, name, runtime=None):
        self.name = name
        self.runtime = runtime
        self.client = RoroClient(self.SERVER_URL)

    def create(self, repo_url=None):
        """Creates a new project.

        If the optional argument repo_url is specified, it initialized the project
        from that git repo. Since it is long task, the task id is returned instead
        of the project.

        Returns the project data when repo_url is absent.
        """
        result = self.client.create(
            name=self.name,
            runtime=self.runtime,
            repo_url=repo_url)
        if repo_url:
            return Task(result['task_id'])
        else:
            return result

    def delete(self):
        return self.client.delete(name=self.name)

    def run(self, command, instance_size=None):
        job = self.client.run(project=self.name, command=command, instance_size=instance_size)
        return job

    def stop(self, jobid):
        self.client.stop(project=self.name, jobid=jobid)

    def stop_service(self, service_name):
        self.client.stop_service(project=self.name, service_name=service_name)

    def start_service(self, service_name):
        self.client.start_service(project=self.name, service_name=service_name)

    def restart_service(self, service_name):
        self.client.restart_service(project=self.name, service_name=service_name)

    def run_notebook(self, instance_size=None, lab=False):
        job = self.client.run_notebook(project=self.name, instance_size=instance_size, lab=lab)
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

    def deploy(self, async=False):
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
                    format=format,
                    async=async
                )
            if async:
                return Task(response['task_id'])
            else:
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

    @classmethod
    def find_all(cls):
        client = RoroClient(cls.SERVER_URL)
        projects = client.projects()
        return [cls(p['name'], p.get('runtime')) for p in projects]

    @classmethod
    def find(cls, name, active_only=True):
        client = RoroClient(cls.SERVER_URL)
        p = client.get_project(project=name, active_only=active_only)
        return p and cls(p['name'], p.get('runtime'))

    def __repr__(self):
        return "<Project {}>".format(self.name)

def current_project():
    if os.path.exists("roro.yml"):
        d = yaml.safe_load(open("roro.yml"))
        project_name = d.get("project") or os.getenv("RORODATA_PROJECT")
        if project_name is None:
            raise ClickException("Please specify `project` in roro.yml file.")
        return Project(project_name, d.get('runtime'))
    else:
        raise ClickException("Unable to find roro.yml")

get_current_project = current_project

def list_projects():
    return Project.find_all()

class Task:
    def __init__(self, task_id):
        self.task_id = task_id
        self._client = RoroClient(config.SERVER_URL)

    def poll(self):
        return self._client.poll_task(task_id=self.task_id)

    def wait(self):
        """Waits for the task to finish and returns the result of the task.

        Raises Exception if the task fails.
        """
        while True:
            response = self.poll()
            if 'error' in response:
                raise Exception(response['error'])
            elif 'result' in response and response['status'] == 'SUCCESS':
                return response['result']
            time.sleep(1)
