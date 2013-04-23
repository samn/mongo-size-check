## mongo-size-check

A rate of growth check for mongo collection sizes
meant to be used with [Riemann](https://github.com/aphyr/riemann)
and [riemann-sumd](https://github.com/bmhatfield/riemann-sumd).

### Usage

Call `mongo-size-check` with the name of the database to monitor.
The current size of each collection will be emitted as an event to riemann-sumd, which will sent to Riemann.  
Your Riemann config should calculate the rate of growth on collection sizes so you can shard before it's
[too late](http://docs.mongodb.org/manual/reference/limits/#Sharding%20Existing%20Collection%20Data%20Size).
