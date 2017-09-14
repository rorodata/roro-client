import shutil
import  pathlib

class Path:
    def __init__(self, path):
        self.volume = None
        if ':' in path:
            self.volume, self.path = path.split(':')
        else:
            self.path = path
        self._path = pathlib.Path(self.path)

    def is_volume(self):
        return self.volume is not None

    def open(self, *args, **kwargs):
        return self._path.open(*args, **kwargs)

    def safe_write(self, fileobj, name):
        file_path = self._get_file_path(name)
        p = file_path.with_suffix('.tmp')
        with p.open('wb') as f:
            shutil.copyfileobj(fileobj, f)
            p.rename(file_path)

    def _get_file_path(self, name):
        if not self._path.parent.is_dir():
            raise FileNotFoundError('No such file or directory: {}'.format(self.name+':'+path))
        if self._path.is_dir():
            if not name:
                raise Exception('Name of the file is required')
            return self._path/pathlib.Path(name)
        else:
            return self._path

    @property
    def size(self):
        return self._path.stat().st_size

    @property
    def name(self):
        return self._path.name
