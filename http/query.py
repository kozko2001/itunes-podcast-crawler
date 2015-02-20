from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch

app = Flask(__name__)


@app.route("/search")
def search():
    q = request.args.get('q')
    es = Elasticsearch()
    r = es.search(q=q, size=100, sort="releaseDate:desc")
    result = {'results': [j['_source'] for j in r['hits']['hits']]}
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

