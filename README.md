## Arweave Scraper

This is a scraper that scrapes the Arweave blockchain. We use the GQL endpoint, which is listed as the most robust way to query the Arweave blockchain currently.

The process is straightforward: we repeatedly get the maximum number of transacations we can collect in one query, and keep track of the returned cursor for pagniation. We also save frequently in case the endpoint temporarily blocks (and have other failsafes in place, including retries and proxy support). 

The query can also be modified to collect less information is desired, and is provided in `query.txt`.

We provide a `requirements.txt` file for easy installation of dependencies and the scraper can then be run with `python scraper.py`.

--Rohan Bansal and Jordan Olmstead