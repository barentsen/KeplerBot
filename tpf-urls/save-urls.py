"""Save Target Pixel File URLs for a given K2 Campaign as a text file.

Usage:

    python save-urls.py CAMPAIGN_NUMBER
"""
import sys
from k2flix.crawler import KeplerArchiveCrawler

campaign = sys.argv[1]

output_fn = 'c{0}-fits-urls.txt'.format(campaign)
print('Writing {}'.format(output_fn))
c = KeplerArchiveCrawler('http://archive.stsci.edu/missions/k2/'
                         'target_pixel_files/c' + campaign)
c.crawl(output_fn)

