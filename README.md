## mongo-size-check

A rate of growth check for mongo collection sizes
meant to be used with [Riemann](https://github.com/aphyr/riemann)
and [riemann-sumd](https://github.com/bmhatfield/riemann-sumd).

### Usage

    Usage: mongo-size-check.py [options]
    
    Options:
      -h, --help            show this help message and exit
      --database=DATABASE   Monitor the collections of this database
      --host=HOST           The host of the database to monitor.
                            (default=localhost)
      --max-collection-size=MAX_COLLECTION_SIZE
                            The max allowed size of a collection in GB.
                            (default=256)
      --compare-days=COMPARE_DAYS
                            The number of days to use to calculate a rate of
                            growth. (default=7)

Call `mongo-size-check.py` with the name of the database to monitor.
The current size of each collection will be emitted as an event to riemann-sumd, which will sent to Riemann.  
Your Riemann config should calculate the rate of growth on collection sizes so you can shard before it's
[too late](http://docs.mongodb.org/manual/reference/limits/#Sharding%20Existing%20Collection%20Data%20Size).

### riemann-sumd config

    service: 'mongo-collection-size'
    arg: 'mongo-collection-size.py --database DATABASE'
    ttl: 86400
    tags: ['notify', 'mongo-collection', 'rate-of-change']
    type: 'json'
