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
      --growth-interval=GROWTH_INTERVAL
                            The number of days to look at the growth rate for.
                            Alert if growth will exceed max-collection-size within
                            this interval.  (default=30)

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

### Riemann config

````
(defn when-growth-exceeds
  "Call children when the the metric of events
  will exceeed a threshold within some interval.
  Calculates the rate-of-growth of metric between events.
  Uses attributes on the event to determine the threshold
  and interval.  The names of those attribute keys are passed
  as args to this function."
  [growth_interval_key threshold_key & children]
  ;; the metric of the event emitted by this function is the rate-of-change
  (ddt-events
    (smap
      ;; call children if the growth is exceeding the threshold within the interval
      (fn [event]
        (let [growth_interval (growth_interval_key event)
              threshold (threshold_key event)
              rate-of-change (:metric event)]
          (when (> threshold (* growth_interval rate-of-change))
            event)))
      (apply sdo children))))

(streams
  (by [:host :service]
    (where (and (not (expired? event)) (tagged "rate-of-change"))
      (when-growth-exceeds :growth_interval :max_size
        (rollup 1 rollup-ttl (email notify-email))))))
````
