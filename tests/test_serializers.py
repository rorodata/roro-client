import os.path
from roro import serializers
from sklearn.linear_model import LinearRegression
from keras.models import Sequential
from keras.layers import Dense
import h5py

def test_find_suitable_serializer():
    model = LinearRegression()
    assert serializers._find_suitable_serializer(model).NAME == "joblib"

    model = Sequential()
    assert serializers._find_suitable_serializer(model).NAME == "keras"

def test_save_model_scikit(tmpdir):
    model = LinearRegression()

    filepath = str(tmpdir.join("model.model"))
    serialization_method = serializers.save_model(model, filepath)
    assert serialization_method == 'joblib'
    assert os.path.exists(filepath)

def test_save_model_keras(tmpdir):
    model = Sequential()
    model.add(Dense(2, input_shape=(2,)))

    filepath = str(tmpdir.join("model.model"))
    serialization_method = serializers.save_model(model, filepath)
    assert serialization_method == 'keras'
    assert os.path.exists(filepath)

    # and the file should be a h5 file
    f = h5py.File(filepath)
    assert "model_config" in f.attrs
