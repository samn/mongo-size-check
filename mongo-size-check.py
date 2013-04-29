import json
import subprocess
import sys

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

def strip_mongo_preamble(mongo_output):
    return mongo_output.partition(JS_SENTINEL)[-1]

def get_collections_info(host, database):
    output = subprocess.check_output(["mongo", database, "--host", host, "--eval", JS_SIZES])
    return json.loads(strip_mongo_preamble(output))

def construct_event(collection_info):
    event = {}
    event["service"] = "mongodb collection sizes"
    event["state"] = "warn"
    event["description"] = collection_info["name"]
    event["metric"] = collection_info["size"]
    return event

def report_collection_sizes(database, host):
    events = [construct_event(e) for e in get_collections_info(host, database)]
    print json.dumps(events)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s database [host=localhost]" % sys.argv[0]
        sys.exit(1)
    database = sys.argv[1]
    host = "localhost"
    if len(sys.argv) > 2:
        host = sys.argv[2]
    report_collection_sizes(database, host)
