import click
import os
from subprocess import call
from requests import get
import json
import elasticsearch
import datetime
from lxml import etree
import multiprocessing

SCRAPY_RESULT = "result.json"
LOOKUP_RESULT = "lookup.json"
MERGE_RESULT = "merge.json"


@click.group()
def cli():
    pass


@cli.command()
def scrapy():
    """
    Executes scrapy and stores result in result.json
    """
    for fn in ["log", "result.json"]:
        os.remove(fn) if os.path.exists(fn) else None
    command = ("scrapy crawl --logfile=log -L ERROR "
               "itunesSpider -t json -o %s") % (SCRAPY_RESULT)
    call(command.split(" "))


@cli.command()
def lookup():
    """
    For each podcast id get more information using the lookup API of itunes

    instead of doing a webservice call for each podcast, bulk it to 200 items
    so itunes don't ban the request with the 403 response

    writing the data to different files
    """
    jsons = json.load(file(SCRAPY_RESULT))

    n = 180
    chunks = [jsons[x:x + n] for x in xrange(0, len(jsons), n)]
    data = []

    i = 0
    for chunk in chunks:
        ids = ",".join([j['itunesId'] for j in chunk])

        r = get("https://itunes.apple.com/lookup", params={'id': ids})
        print i, r.status_code
        i += 1
        data.extend(r.json()["results"])

    with open(LOOKUP_RESULT, 'w') as outfile:
            json.dump(data, outfile)


@cli.command()
def merge():
    """
    get data from scrappy and lookup, and merge them together in a new merge.json file
    """
    json_channels = json.load(file(SCRAPY_RESULT))
    json_lookup = json.load(file(LOOKUP_RESULT))
    result = []

    index = {}
    for channel in json_channels:
        index[int(channel['itunesId'])] = channel

    for lookup in json_lookup:
        _id = lookup['trackId']
        channel = index[_id] if _id in index else None

        validKeys = ["releaseDate", "trackId", "feedUrl",
                     "trackViewUrl", "artworkUrl600"]
        lookup = {k: v for (k, v) in lookup.iteritems() if k in validKeys}

        if channel:
            lookup.update(channel)

        if 'releaseDate' in lookup:
            date = datetime.datetime.strptime(lookup['releaseDate'],
                                              "%Y-%m-%dT%H:%M:%SZ")

            delta = datetime.datetime.now() - date
            if delta.days < 400:
                result.append(lookup)

    with open(MERGE_RESULT, 'w') as outfile:
            json.dump(result, outfile, indent=4)


@cli.command()
def addFeedData():
    """
    Downloads the feedurl from the merge data and add
    data for the channel description
    """

    pool = multiprocessing.Pool(100)
    json_merge = json.load(file(MERGE_RESULT))
    count = len(json_merge)

    data = [(_json, idx, count) for idx, _json in enumerate(json_merge)]
    result = pool.map(add_feed_data_worker, data, chunksize=1)
    pool.close()
    pool.join()

    with open(MERGE_RESULT, 'w') as outfile:
        json.dump(result, outfile, indent=4)


def add_feed_data_worker(data):
    _json, index, total = data
    try:
        url = _json['feedUrl']
        r = get(url, timeout=5)
        rss = etree.XML(r.content)
        description = "".join(rss.xpath('//channel/itunes:summary/text()',
                                        namespaces=rss.nsmap))
        _json['description'] = description
        print url, index, total
        return _json
    except:
        return _json


@cli.command()
def elasticSearch():
    """
    gets merge.json and adds it to the elastic search
    """
    json_merge = json.load(file(MERGE_RESULT))
    es = elasticsearch.Elasticsearch()

    indices = elasticsearch.client.IndicesClient(es)
    indices.delete('podcast', ignore=404)

    for _json in json_merge:
        _id = _json['trackId']
        date = datetime.datetime.strptime(lookup['releaseDate'],
                                          "%Y-%m-%dT%H:%M:%SZ")
        _json['releaseDate'] = date
        es.index(index='podcast', doc_type='podcast', id=_id, body=_json)


if __name__ == '__main__':
    cli()
