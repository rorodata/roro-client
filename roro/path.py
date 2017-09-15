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
        if self._path.is_dir():
            raise Exception('Cannot copy, {} is a directory'.format(str(self._path)))
        return self._path.open(*args, **kwargs)

    def safe_write(self, fileobj, name):
        file_path = self._get_file_path(name)
        if file_path.is_dir():
            raise Exception('Cannot copy, {} is a directory'.format(str(file_path)))
        p = file_path.with_suffix('.tmp')
        with p.open('wb') as f:
            shutil.copyfileobj(fileobj, f)
            p.rename(file_path)

    def _get_file_path(self, name):
        dest = self._path
        if dest.name != name:
            if not name:
                raise Excetption('Name of the file is required when path is poiting to a dir')
            dest = dest/pathlib.Path(name)
        if not dest.parent.is_dir():
            raise FileNotFoundError('No such file or directory: {}'.format(self.name+':'+path))
        return dest

    @property
    def size(self):
        return self._path.stat().st_size

    @property
    def name(self):
        return self._path.name
