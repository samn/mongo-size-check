#! /usr/bin/env python
import json
from optparse import OptionParser
import subprocess
import sys

class MongoSizeCheck():
    # The mongo command outputs stuff before showing the output of what it runs
    # this is used to split that out so the rest can be parsed as json.
    JS_SENTINEL = "WWWEB$CALE"

    JS_SIZES = """
    var out = [];
    db.getCollectionNames().forEach(function(collection) {
        var collectionInfo = {name: collection};
        var size = db.runCommand({collStats: collection})['storageSize'];
        collectionInfo["size"] = size;
        out.push(collectionInfo);
    })
    print("%s");
    printjson(out);
    """ % JS_SENTINEL

    def __init__(self, options):
        self.database = options.database
        self.host = options.host
        self.max_collection_size = options.max_collection_size 
        self.growth_interval = options.growth_interval

    def strip_mongo_preamble(self, mongo_output):
        return mongo_output.partition(self.JS_SENTINEL)[-1]

    def get_collections_info(self):
        output = subprocess.check_output(["mongo", self.database, "--host", self.host, "--eval", self.JS_SIZES])
        return json.loads(self.strip_mongo_preamble(output))

    def construct_event(self, collection_info):
        event = {}
        event["service"] = "mongodb collection sizes"
        event["state"] = "warn"
        event["description"] = collection_info["name"]
        event["metric"] = collection_info["size"]
        event["attributes"] = {}
        event["attributes"]["max_size"] = self.max_collection_size
        event["attributes"]["growth_interval"] = self.growth_interval
        return event

    def report_collection_sizes(self):
        events = [self.construct_event(e) for e in self.get_collections_info()]
        print json.dumps(events)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--database", help="Monitor the collections of this database")
    parser.add_option("--host", default="localhost", help="The host of the database to monitor. (default=localhost)")
    parser.add_option("--max-collection-size", default=256, help="The max allowed size of a collection in GB. (default=256)")
    parser.add_option("--growth-interval", default=30, help="The number of days to look at the growth rate for.  Alert if growth will exceed max-collection-size within this interval.  (default=30)")
    options, args = parser.parse_args()
    if options.database is None:
        parser.print_help()
        exit(-1)
    MongoSizeCheck(options).report_collection_sizes()
