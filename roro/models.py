from __future__ import print_function
import io
import joblib
import re

def get_model_repository(client, project, name):
    """Returns the ModelRepository with given name from the specified project.

    :param project: the name of the project
    :param name: name of the repository
    """
    return ModelRepository(client, project, name)

def list_model_repositories(client, project):
    return ModelRepository.find_all(client, project)

class ModelRepository:
    def __init__(self, client, project, name):
        self.client = client
        self.project = project
        self.name = name

    def get_model_image(self, tag=None, version=None):
        metadata = self.client.get_model_version(
                    project=self.project,
                    name=self.name,
                    tag=tag,
                    version=version)
        return ModelImage(repo=self, metadata=metadata)

    def new_model_image(self, model, metadata={}):
        """Creates a new ModelImage.
        """
        return ModelImage(repo=self, metadata=metadata, model=model)

    def get_activity(self):
        response = self.client.get_activity(project=self.project, name=self.name)
        return [ModelImage(repo=self, metadata=x) for x in response]

    @staticmethod
    def find_all(client, project):
        response = client.list_models(project=project)
        return [ModelRepository(client, project, name) for name in response]

    def __repr__(self):
        return "<ModelRepository {}/{}>".format(self.project, self.name)


class ModelImage:
    def __init__(self, repo, metadata, model=None, comment=None):
        self._repo = repo
        self._model = model
        self._metadata = metadata
        self.comment = comment or self.get("Comment")

    @property
    def id(self):
        return self._metadata.get("Model-Id")

    @property
    def version(self):
        return self._metadata["Model-Version"]

    @property
    def name(self):
        return self._metadata["Model-Name"]

    def __getitem__(self, name):
        return self._metadata[name]

    def __setitem__(self, name, value):
        self._metadata[name] = value

    def get_summary(self):
        keys = ["Model-ID", "Model-Name", "Model-Version", "Date"]
        f = io.StringIO()
        for k in keys:
            print("{}: {}".format(k, self.get(k, "")), file=f)
        print(file=f)

        comment = self._indent(self.comment)
        print("    {}".format(comment), file=f)
        return f.getvalue()

    def get_details(self):
        keys = ["Model-ID", "Model-Name", "Model-Version", "Date"]
        lower_keys = {k.lower(): i for i, k in enumerate(keys)}
        items = sorted(self._metadata.items(), key=lambda kv: (lower_keys.get(kv[0].lower(), 100), kv[0]))

        special_keys = ["comment", "tag"]
        items = [(k, v) for k, v in items if k.lower() not in special_keys]

        f = io.StringIO()
        for k, v in items:
            print("{}: {}".format(k, v), file=f)
        print(file=f)

        comment = self._indent(self.comment)
        print("    {}".format(comment), file=f)
        return f.getvalue()


    def _indent(self, text):
        text = text or ""
        return re.compile("^", re.M).sub("    ", text)

    def get(self, name, default=None):
        return self._metadata.get(name, default)

    def get_model(self):
        if self._model is None:
            self._model = self._load_model()
        return self._model

    def _load_model(self):
        f = self.client.get_model(
                    project=self.project,
                    name=self.name,
                    version=self.version)
        return joblib.load(f)

    def save(self, comment):
        """Saves a new version of the model image.
        """
        if self.id is not None:
            raise Exception("ModelImage can't be modified once created.")
        if self._model is None:
            raise Exception("model object is not specified")

        f = io.BytesIO()
        joblib.dump(self._model, f)
        self['Content-Encoding'] = 'joblib'
        self._repo.client.save_model(
            project=self._repo.project,
            name=self._repo.name,
            model=f,
            comment=comment,
            **self._metadata)
        # TODO: Update the version and model-id

    def __repr__(self):
        return "<ModelImage {}/{}@{}>".format(self._repo.project, self._repo.name, self.version)

    def __str__(self):
        return self.get_details()
