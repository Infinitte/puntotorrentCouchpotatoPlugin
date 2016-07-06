from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import tryUrlencode
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import traceback

log = CPLog(__name__)


class puntotorrent(TorrentProvider, MovieProvider):

    urls = {
        'test' : 'https://xbt.puntotorrent.ch',
        'login' : 'https://xbt.puntotorrent.ch/index.php?page=login',
        'login_check': 'https://xbt.puntotorrent.ch/index.php',
        'search' : 'https://xbt.puntotorrent.ch/index.php?page=torrents&search=%s&category=%d&active=1',
        'download' : 'https://xbt.puntotorrent.ch/%s',
    }

    cat_ids = [
        ([57], ['720p', '1080p']),
        ([109], ['720p']),
        ([48], ['dvdrip']),
        ([56], ['brrip']),
    ]

    http_time_between_calls = 1 #seconds
    cat_backup_id = None

    def _searchOnTitle(self, title, movie, quality, results):
		log.info('Searching puntotorrent for %s, %d' % (title,self.getCatId(quality)[0]))
		url = self.urls['search'] % (title.replace(':', ''), self.getCatId(quality)[0] )
		data = self.getHTMLData(url)
		
		log.debug('Received data from puntotorrent')
		if data:
			log.debug('Data is valid from puntotorrent')
			html = BeautifulSoup(data)
			
			try:
				result_table = html.find_all('table', attrs = {'class' : 'lista'})
				result_table = result_table[3]
				if not result_table:
					log.error('No table results from puntotorrent')
					return
					
				torrents = result_table.find_all('tr')
				
				for result in torrents:
					columnas = result.find_all('td')
					if len(columnas)>9:
						release_name = columnas[1].find('a').contents[0]
						if release_name!='Nombre':
							if release_name[0]=='(':
								release_name = release_name[release_name.index(')')+1:]
							url = columnas[3].find('a')
							link = url['href']
							id = link[link.index('?')+1:link.index('&')]
							size = columnas[5].contents[0]
							num_seeders = columnas[7].find('a').contents[0]
							num_leechers = columnas[8].find('a').contents[0]
							results.append({
								'id': id,
								'name': release_name,
								'url': self.urls['download'] % url['href'],
								'size': self.parseSize(size.replace(',','.')),
								'seeders': num_seeders,
								'leechers': num_leechers,
							})

			except:
				log.error('Failed to parse puntotorrent: %s' % (traceback.format_exc()))
		
    def getLoginParams(self):
        log.debug('Getting login params for puntotorrent')
        return {
            'uid': self.conf('username'),
            'pwd': self.conf('password'),
        }

    def loginSuccess(self, output):
		log.info('Checking login success for puntotorrent: %s' % ('True' if ('Mi Panel' in output.lower() or 'de nuevo' in output.lower()) else 'False'))
		return 'Mi Panel' in output.lower() or 'de nuevo' in output.lower()

    loginCheckSuccess = loginSuccess
