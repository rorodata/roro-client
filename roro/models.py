
def get_model_repository(project, name):
    """Returns the ModelRepository with given name from the specified project.

    :param project: the name of the project
    :param name: name of the repository
    """
    return ModelRepository(project, name)

class ModelRepository:
    def __init__(self, project, name):
        self.project = project
        self.name = name

    def get_model_image(self, tag="latest", version=None):
        pass

    def new_model_image(self, model, metadata={}):
        """Creates a new ModelImage.
        """


class ModelImage:
    def __init__(self, repo, metadata, model=None, comment=None):
        self._repo = repo
        self._model = model
        self._metadata = metadata
        self.comment = comment

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

    def get(self, name, default=None):
        return self._metadata.get(name, default)

    def get_model(self):
        pass

    def save(self, comment):
        """Saves a new version of the model image.
        """
        if self.id is not None:
            raise Exception("ModelImage can't be modified once created.")






