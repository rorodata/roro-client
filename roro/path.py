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

    def safe_write(self, fileobj):
        if not self._path.parent.exists():
            raise FileNotFoundError('Directory {} does not exist'.format(self._path.parent.absolute))
        p = self._path.with_suffix('.tmp')
        with p.open('wb') as f:
            shutil.copyfileobj(fileobj, f)
            p.rename(self._path)

    @property
    def size(self):
        return self._path.stat().st_size
