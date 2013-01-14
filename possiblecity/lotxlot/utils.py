# lotxlot/utils.py
import gc
import json
import requests
from urllib import urlencode

from django.core.cache import cache

def fetch_json(url, params):
    """
    Gets data from a REST source and returns a python dictionary.
    If the result is already in cache, it returns cached data.
    Source should be a valid REST url.
    """
    cache_key = url + "?" + urlencode(params)
    cached = cache.get(cache_key)
    content = ""
    
    if not cached:
        data = requests.get(url, params=params)
        if (data.ok):
            cache.set(str(data.url), data.text)
            content = data.text
        else:
            data.raise_for_status()
    else:
        # return cached content
        content = cached
    
    return json.loads(content)    
      
def has_feature(url, params):
        """
           Query a Geographic REST service, return True if
           there are any features that match the query 
        """
        dict = fetch_json(url, params)
		
        if 'features' in dict:
            if dict['features']:
                return True
            else:
            		return False
        else:
            return False


import time, traceback, logging, sys
class Status(object):
    def __init__(self):
        self.num_successful = 0
        self.failed_ids = []
        self.done = False
        self.cur_idx = 0

    def __repr__(self):
        return u'<Status: %s/%s, %s failed>' % (
            getattr(self, 'cur_idx', '-'),
            getattr(self, 'total', '-'),
            self.num_failed)

    @property
    def num_failed(self): return len(self.failed_ids)

    def start(self):
        self.start_time = time.time()

    def finished(self):
        self.cur_idx = self.total
        self.done = True
        self.end_time = time.time()

    @property
    def rate(self):
        if self.done:
            end_time = self.end_time
        else:
            end_time = time.time()
        return self.cur_idx / (end_time - self.start_time)

    @property
    def time_left(self):
        rate = self.rate
        if rate == 0: return 0
        return (self.total - self.cur_idx) / self.rate

def progress_callback(status):
    sys.stderr.write('%d/%d failed=%d, rate~%.2f per second, left~%.2f sec    \r' % (
            status.cur_idx, status.total, status.num_failed, status.rate, status.time_left))
    if status.done: sys.stderr.write('\n')
    sys.stderr.flush()


def queryset_foreach(queryset, f, batch_size=1000,
                     progress_callback=progress_callback, transaction=True):
    '''
    Call a function for each element in a queryset (actually, any list).

    Features:
    * stable memory usage (thanks to Django paginators)
    * progress indicators
    * wraps batches in transactions
    * can take managers or even models (e.g., Assertion.objects)
    * warns about DEBUG.
    * handles failures of single items without dying in general.
    * stable even if items are added or removed during processing
    (gets a list of ids at the start)

    Returns a Status object, with the following interesting attributes
      total: number of items in the queryset
      num_successful: count of successful items
      failed_ids: list of ids of items that failed
    '''
    
    from django.conf import settings
    if settings.DEBUG:
        print >> sys.stderr, 'Warning: DEBUG is on. django.db.connection.queries may use up a lot of memory.'
    
    # Get querysets corresponding to managers
    from django.shortcuts import _get_queryset
    queryset = _get_queryset(queryset)
    
    # Get a snapshot of all the ids that match the query
    logging.info('qs4e: Getting list of objects')
    ids = list(queryset.values_list(queryset.model._meta.pk.name, flat=True))

    # Initialize status
    status = Status()
    status.total = len(ids)

    def do_all_objects(objects):
        for id, obj in objects.iteritems():
            try:
                f(obj)
                status.num_successful += 1
            except Exception: # python 2.5+: doesn't catch KeyboardInterrupt or SystemExit
                traceback.print_exc()
                status.failed_ids.append(id)
        
    if transaction:
        # Wrap each batch in a transaction
        from django.db import transaction
        do_all_objects = transaction.commit_on_success(do_all_objects)
    
    from django.core.paginator import Paginator
    paginator = Paginator(ids, batch_size)

    status.start()
    progress_callback(status)
    for page_num in paginator.page_range:
        status.page = page = paginator.page(page_num)
        status.cur_idx = page.start_index()-1
        progress_callback(status)
        objects = queryset.in_bulk(page.object_list)
        do_all_objects(objects)
    status.finished()

    progress_callback(status)

    return status


def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

# convert the projection type of a shapefile
# ogr2ogr -t_srs <New Projection> <Output SHP file> <Original SHP file>
# ogrinfo <Path to SHP file> -al -so
# ogr2ogr -f "ESRI Shapefile" -where "id < 10" new_shapefile.shp huge_shapefile.shp
