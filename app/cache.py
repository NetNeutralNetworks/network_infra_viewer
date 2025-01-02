from flask_caching import Cache

appCache = Cache(config={'CACHE_TYPE': 'SimpleCache'})