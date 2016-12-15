import datetime as a
from datetime import datetime
fmt = '%Y-%m-%d %H:%M:%S'
d1 = datetime.strptime(a.datetime.now().strftime(fmt), fmt)
d2 = datetime.strptime('2016-12-16 17:31:22', fmt)

print ((d2-d1).days * 24 * 60)