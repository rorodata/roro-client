import datetime
from roro import helpers as h

def test_datestr():
    now = datetime.datetime.utcnow()
    assert h.datestr(now, now) == 'Just now'

    t = now - datetime.timedelta(seconds=1)
    assert h.datestr(t, now) == '1 second ago'

    t = now - datetime.timedelta(seconds=5)
    assert h.datestr(t, now) == '5 seconds ago'

    t = now - datetime.timedelta(seconds=60*5)
    assert h.datestr(t, now) == '5 minutes ago'
