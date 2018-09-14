#!/usr/bin/env python
"""Posts a random Kepler Target Pixel File (TPF) as an animated gif on Twitter.

Author: Geert Barentsen
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random
import sys
from twython import Twython

from astropy import log
from astropy.coordinates import SkyCoord

from k2flix import TargetPixelFile
from k2flix.crawler import KeplerArchiveCrawlerDB

import matplotlib.pyplot as pl
from lightkurve import KeplerTargetPixelFile

from secrets import *


def generate_tweet(tpf_fn=None, movie_length=60, step=49):
    """Generate a status message and animated gif.

    Parameters
    ----------
    tpf_fn : str (optional)
        Path or url to a TPF file. If `None`, a random file will be downloaded.

    movie_length : int (optional)
        Number of frames in the animation.

    Returns
    -------
    (status, gif, plot, tpf) : (str, str, str, `TargetPixelFile`)
    """
    # Open the Target Pixel File
    if tpf_fn is None:  # Get a random url
        db = KeplerArchiveCrawlerDB('tpf-urls/latest-tpf-urls.txt')
        tpf_fn = db.random_url()
    log.info('Opening {0}'.format(tpf_fn))
    tpf = TargetPixelFile(tpf_fn, cache=False)
    log.info('KEPMAG = {0}, DIM = {1}'.format(tpf.hdulist[0].header['KEPMAG'],
                                              tpf.hdulist[1].header['TDIM5']))
    # Don't tweet tiny strips
    if (tpf.hdulist[2].header['NAXIS1'] < 3) or (tpf.hdulist[2].header['NAXIS2'] < 3):
        raise Exception('Tiny strip')
    # Files contain occasional bad frames, so we make multiple attempts
    # with random starting points
    attempt_no = 0
    while attempt_no < 7:
        attempt_no += 1
        try:
            start = random.randint(0, tpf.no_frames - step*movie_length)
            try:
                kepmag = '🔆 Kp {:.1f}\n'.format(float(tpf.hdulist[0].header['KEPMAG']))
            except Exception:
                kepmag = ''
            timestr = tpf.timestamp(start).split(' ')[0]
            campaign = tpf.hdulist[0].header['CAMPAIGN']
            url = "https://archive.stsci.edu/k2/data_search/search.php?ktc_k2_id={}&action=Search".format(tpf.objectname.split(' ')[1])
            status = ('New Kepler data were recently released!\n'
                      '🔎 {}\n'
                      '🗓 {} (C{})\n'
                      '{}'
                      '🔗 {}'.format(tpf.objectname, timestr, campaign, kepmag, url))
            log.info(status)
            # Create the animated gif
            gif_fn = '/tmp/keplerbot.gif'
            tpf.save_movie(gif_fn, start=start, stop=start + step*movie_length,
                           step=step, fps=3, min_percent=0., max_percent=93.,
                           ignore_bad_frames=True)
            # Create the lightcurve plot
            plot_fn = '/tmp/keplerbot-lightcurve.png'
            ktpf = KeplerTargetPixelFile(tpf_fn)
            ktpf.to_lightcurve(aperture_mask='all').correct(restore_trend=True).remove_outliers().scatter(normalize=False)
            pl.tight_layout()
            print('Writing {}'.format(plot_fn))
            pl.savefig(plot_fn)
            pl.close()

            return status, gif_fn, plot_fn, tpf
        except Exception as e:
            log.error(e)
    raise Exception('Tweet failed')


def post_tweet(status, gif, plot):
    """Post an animated gif and associated status message to Twitter."""
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    upload_response = twitter.upload_media(media=open(gif, 'rb'))
    upload_response2 = twitter.upload_media(media=open(plot, 'rb'))
    response = twitter.update_status(status=status, media_ids=upload_response['media_id'])
    status2 = '...and here is the quicklook lightcurve:'
    response2 = twitter.update_status(status=status2, media_ids=upload_response2['media_id'],
                                      in_reply_to_status_id=response['id'])
    log.info(response)
    return twitter, response, response2


if __name__ == '__main__':
    attempt_no = 0
    while attempt_no < 10:
        attempt_no += 1
        try:
            status, gif, plot, tpf = generate_tweet()
            if 'test' in sys.argv:
                print('Running in test mode -- not posting to Twitter.')
            else:
                twitter, response, response2 = post_tweet(status, gif, plot)
            break
        except Exception as e:
            log.warning(e)
