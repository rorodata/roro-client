"""
    roro.serializers
    ~~~~~~~~~~~~~~~~

    serialization support for various types of models.
"""
from collections import OrderedDict

# mapping from serializer name to class
_SERIALIZERS = OrderedDict()

def save_model(model, filename):
    """Saves the given model into a file.

    :param model: the model object
    :param filename: path to the file where the model is to be saved
    :return: the name of the serializer used to save the model
    """
    serializer = _find_suitable_serializer(model)
    serializer.dump(model, filename)
    return serializer.NAME

def load_model(filename, serializer):
    """Saves the given model into a file.

    :param filename: path to the filename containing the serialized model
    :param serializer: name of the serializer used to save this model
    :return: the model object
    """
    serializer_object = _get_serializer(name=serializer)
    return serializer_object.load(filename)

def _get_serializer(name):
    return _SERIALIZERS[name]()

def _find_suitable_serializer(model):
    for name, serializer_class in _SERIALIZERS.items():
        try:
            serializer = serializer_class()
            if serializer.can_dump(model):
                return serializer
        except ImportError as e:
            logger.warn("Unable to load the required dependencies for serializer {!r} ({})".format(name, e))
    raise ValueError("Object of type %s is not serializable" % model.__class__)

class BaseSerializer:
    def dump(model, filename):
        """Dumps the model into a file.

        :param model: the model object
        :param filename: path to the filename where the model is to be saved
        """
        raise NotImplementedError()

    def load(self, filename):
        """Loads the model from the given file.

        :param filename: path to the filename containing the serialized model.
        :return: the model object
        """
        raise NotImplementedError()

    def can_dump(self, model):
        """Checks if the given model is serializable by this serializer.
        """
        raise NotImplementedError()


class JoblibSerializer:
    NAME = "joblib"

    def __init__(self):
        from sklearn.base import BaseEstimator
        self.BaseEstimator = BaseEstimator

        import joblib
        self.joblib = joblib

    def dump(self, model, filename):
        self.joblib.dump(model, filename)

    def load(self, filename):
        return self.joblib.load(filename)

    def can_dump(self, model):
        return isinstance(model, self.BaseEstimator)

    def get_name(self):
        return "joblib"

class KerasSerializer:
    NAME = "keras"

    def __init__(self):
        from keras.models import save_model, load_model, Model
        self._keras_save_model = save_model
        self._keras_load_model = load_model
        self._Model = Model

    def dump(self, model, filename):
        self._keras_save_model(model, filename)

    def load(self, filename):
        return self._keras_load_model(filename)

    def can_dump(self, model):
        return isinstance(model, self._Model)

_SERIALIZERS['joblib'] = JoblibSerializer
_SERIALIZERS['keras'] = KerasSerializer

