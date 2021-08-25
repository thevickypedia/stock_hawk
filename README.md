# Stock Hawk: 
This is the AWS version of [robinhood_monitor](https://github.com/thevickypedia/robinhood_monitor)

This repo contains scripts that run on lambda connecting to SSM.

Refer [Wiki](https://github.com/thevickypedia/stock_hawk/wiki) for setup information.

The following needs to be added before `GET FUNDAMENTALS` in `pyrh/robinhood.py` to get the watchlist feature working.

Refer https://github.com/robinhood-unofficial/pyrh/pull/274

```python
###########################################################################
#                           GET WATCHLIST
###########################################################################

def get_watchlists(self):
    """Fetch watchlists endpoint and queries for
    each instrumented result aka stock details returned from the watchlist
    Returns:
        (:obj:`dict`): values returned from `watchlists` and `instrument` endpoints
    """
    api_url = "https://api.robinhood.com"
    url = api_url + "/watchlists/"
    res = []
    watchlist = self.get_url(url)
    if watchlist and 'results' in watchlist:
        data = self.get_url(watchlist["results"][0]["url"])
        for rec in data["results"]:
            res.append(self.get_url(rec['instrument']))

    return res
```

## License & copyright

&copy; Vignesh Sivanandha Rao, Stock Hawk

Licensed under the [MIT License](LICENSE)
