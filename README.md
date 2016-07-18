# @KeplerBot

This repo contains the `keplerbot.py` script that is used
by @KeplerBot to post animated gifs of Kepler/K2 data on Twitter.

## Usage

To generate a test tweet:
```
python keplerbot.py test
```

To send an actual tweet:
```
python keplerbot.py
```

To obtain a list of Target Pixel File URLs to tweet:
```
cd tpf-urls
python save-urls.py CAMPAIGN_NUMBER
```

## Requirements

You need to add a `secrets.py` file in the same directory containing your
Twitter API secrets.

You will also need the following Python packages:

* astropy
* k2flix
* twython

