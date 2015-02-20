
Extract podcast from itunes
===========================


1) create a virtualenv and activate

2) pip install requirements.txt

3) python crawl.py scrapy ## will download podcast names from itunes pages

4) python crawl.py lookup ## will download more info from podcast using the lookup itunes api https://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html

5) python crawl.py merge ## merge the two datafiles

6) python crawl.py addfeeddata ## download the rss xml and extracts the information 

7) python crawl.py elasticsearch ## add data to elasticsearch service

8) cd http; python query.py ## to see the search on a rest api
