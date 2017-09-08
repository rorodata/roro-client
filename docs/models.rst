Model Management
================

The Rorodata Platform has built-in support for managing multiple versions of machine learning models. Along with storing the models, it allows keeping track of any metadata required to identify what went into building the model and also attaching any related files.

Overview
--------

Every project can have zero or more model repositories. Each model repository manages multiple versions of one model. Each version is called a ModelImage, which contains the serialized model object, associated metadata and attached files. ::

    +-----------------------------------------------+
    | ModelRepository A                             |
    |                                               |
    |  ModelImage - v1         ModelImage - v2      |
    | +---------------+       +---------------+     |
    | | Model v1      |       | Model v1      |     |
    | +---------------+       +---------------+     |
    | | Metadata v1   |       | Metadata v1   |     |
    | +---------------+       +---------------+     |
    +-----------------------------------------------+

    +-----------------------------------------------+
    | ModelRepository B                             |
    |                                               |
    |  ModelImage - v1         ModelImage - v2      |
    | +---------------+       +---------------+     |
    | | Model v1      |       | Model v1      |     |
    | +---------------+       +---------------+     |
    | | Metadata v1   |       | Metadata v1   |     |
    | +---------------+       +---------------+     |
    +-----------------------------------------------+

The system stores all the models and the attachments in an S3 bucket and the metadata is stored in a SQL database.

The Python Interface
--------------------

Here is a sample script to save a new version of an ML model::

    import roro
    project = roro.get_current_project()
    model_repo = project.get_model_repository("credit-risk")

    # run the training algorithm to build the model
    model = train_machine_learning_model()

    model_image = model_repo.new_image(model)
    model_image['Input-Data-Source'] = 's3://credit-risk-dataset-201706'
    model_image['Accuracy'] = 0.89
    model_image.attach("log.txt", open("log.txt"))
    model_image.save(comment="Built new model using the data till June 2017")

And another script that predicts from a saved model. ::

    import roro

    project = roro.get_current_project()

    # Take the repo for required model
    model_repo = project.get_model_repository("credit-risk")

    # get the image of the latest version or any tag
    model_image = model_repo.get_model_image(tag="latest")

    # get the actual model object
    model = model_repo.get_model()

    def predict(features):
        return model.predict(features)

The API
^^^^^^^


.. py:class:: Project

   .. py:method:: get_model_repository(name)

      Returns the :py:class:`ModelRepository` with given name.

   .. py:method:: list_model_repositories()

      Returns all the model repositories associated with this project.

   .. py:method:: create_model_repository(name)

      Creates a new :py:class:`ModelRepository` with given name.

.. py:class:: ModelRepository

   .. py:method:: new_model_image(self, model)

      Creates a new model image.

      The `save` method must be called on the model image object
      after preparing the image by adding metadata and attachments.

   .. py:method:: get_model_image(self, version=None, tag=None)

      Returns the model image with given version number or tag name.

   .. py:method:: get_tags(self)

      Returns all the tags available in this repository.

   .. py:method:: add_tag(self, tag, version)

      Tags the specified ``version`` of the model image as given ``tag`` name.

.. py:class:: ModelImage

   ModelImage represents one version of an ML model and its assocated metadata.

   Metadata can be added to a model image like a dictionary. ::

    model_image['Accuracy'] = 0.83
    model_image['Input-Source'] = 's3://credit-risk-201706'

   Some metadata like timestamp, author etc. are automatically added.

   .. py:method:: save(self, comment)

      Saves the model image as a new version.

   .. py:method:: __getattr__(self, name)

      Returns the metadata with given name.

   .. py:method:: __setattr__(self, name, value)

      Set value of the metadata attribute with given name.

   .. py:method:: get_metadata(self)

      Returns all metadata as a dictionary.

   .. py:method:: set_metadata(self, metadata)

      Sets the model metadata.

   .. py:method:: attach(self, filename, fileobj)

      Adds a new attachment to the model image.

   .. py:method:: get_attachments(self)

      Returns all the attachments added to this model image.

   .. py:method:: get_model(self)

      Returns the model object.

   .. py:attribute:: version

      Version number of this model image.

The Command-line API
--------------------

The Rorodata platform also provides a way to browse though the models from command line.

**roro models**

Lists all model repositories in the project.

**roro models:create name**

Creates a new model repository.

**roro models:log [name]**

Shows a log of model saves.

**roro models:show name:version-tag**

Shows the metadata of the model image specified by model name and version or tag.

**roro models:download name:version-tag**

Downloads the model of name with given version or tag.
