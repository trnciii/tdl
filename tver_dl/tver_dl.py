import requests, youtube_dl
import sys, re
import argparse
from datetime import datetime


def save(name, data):
	with open(name, 'w', encoding='utf-8') as f:
		f.write(data)


def request_episode(episodeID, dump=False):
	response = requests.get(
		f'https://statics.tver.jp/content/episode/{episodeID}.json',
		params={
			'v': '8',
		}
	)

	if response.ok:
		if dump: save(f'{episodeID}.json', response.text)
		return response.json()
	else:
		print('failed to get episode info')
		print(response.reason)
		return None


def request_series(seriesID, dump=False):
	response = requests.get(
		f'https://statics.tver.jp/content/series/{seriesID}.json',
		params={
			'v': '3',
		})

	if response.ok:
		if dump: save(f'{seriesID}.json', response.text)
		return response.json()
	else:
		print('failed to get series')
		print(response.reason)
		return None


def request_video(accountID, videoRef, key, dump=False):
	response = requests.get(
		f'https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref:{videoRef}',
		headers={
			'accept': f'application/json;pk={key}'
		}
	)

	if response.ok:
		if dump: save(f'video-{accountID}-{videoRef}.json', response.text)
		return response.json()
	else:
		print('failed to get video id')
		print(response.reason)
		return None


def get_key(accountID, playerID, dump=False):
	response = requests.get(
		f'https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js',
		headers={}
	)
	if response.ok:
		if dump: save(f'key-{accountID}.js', response.text)
		return re.search(
			r'(?<=policyKey:")(.*?)(?=")',
			response.text
		).groups(0)[0]

	else:
		print('failed to get policy key')
		print(response.reason)
		exit()

def get_video_id(episode, dump):
	try:
		vid = episode['video']
		print(vid.keys())

		if 'videoID' in vid.keys():
			return vid['videoID']

		if 'videoRefID' in vid.keys():
			videoRef = vid['videoRefID']
			accountID = vid['accountID']
			key = get_key(accountID, vid['playerID'], dump=dump)
			videoRes = request_video(accountID, videoRef, key, dump=dump)
			return  videoRes['id']

		raise Exception('no matching search method')

	except Exception as e:
		print('failed to get video info and so video id')
		print(e)
		exit()


def get_program(episodeID, dump=False):
	episodeRes = request_episode(episodeID, dump=dump)
	if episodeRes == None:
		print('failed to get episode info')
		exit()

	vid = episodeRes['video']
	accountID = vid['accountID']
	playerID = vid['playerID']
	videoID = get_video_id(episodeRes, dump=dump)
	url = f'http://players.brightcove.net/{accountID}/default_default/index.html?videoId={videoID}'
	print(f'{playerID=}')
	print(f'{accountID=}')
	print(f'{videoID=}')
	print(f'{url=}')


	seriesID = episodeRes['seriesID']
	if seriesRes := request_series(seriesID, dump=dump):
		series = seriesRes['title']
		desc_series = seriesRes['description']
	else:
		series = ''
		desc_series = ''

	return {
		'series': series,
		'desc_series': desc_series,

		'subtitle': episodeRes['title'],
		'index': episodeRes['no'],
		'date': episodeRes['broadcastDateLabel'],
		'service': episodeRes['broadcastProviderLabel'],
		'caption': episodeRes['isSubtitle'],
		'desc_episode': episodeRes['description'],

		'series url': f'https://tver.jp/lp/series/{seriesID}',
		'episode url': f'https://tver.jp/episodes/{episodeID}',
		'video url': url,

		'accountID': accountID,
		'episodeID': episodeID,
		'seriesID': seriesID,
	}

def create():
	response = requests.post('https://platform-api.tver.jp/v2/api/platform_users/browser/create',
		data={
			'device_type': 'pc'
		})
	return response.json()

def format_search_result(result):
	if result['type'] == 'episode':
		content = result['content']
		episode_id = content.get('id')
		series_id = content.get('seriesID')
		end_at = datetime.fromtimestamp(content['endAt'])
		if (end_at - datetime.now()).days < 7:
			end_at = f'\x1b[33m{end_at}\x1b[m'

		return f'''{content.get('seriesTitle')} {content.get('title')}
  Ends at {end_at}
  {episode_id} https://tver.jp/episodes/{episode_id}
  {series_id} https://tver.jp/series/{series_id}'''

	else:
		return result


def search(words):
	info = create()
	response = requests.get('https://platform-api.tver.jp/service/api/v2/callKeywordSearch',
		params={
			'platform_uid': info['result']['platform_uid'],
			'platform_token': info['result']['platform_token'],
			'sortKey': 'score',
			'filterKey': '',
			'keyword': words,
			'require_data': 'later',
		},
		headers={
			'x-tver-platform-type': 'web',
		})

	data = response.json()
	lines = [format_search_result(r) for r in data['result']['contents']]
	for line in lines:
		print(line)

def download(episodeID, output, caption, no_dl, dump):
	program = get_program(episodeID, dump=dump)

	dl = youtube_dl.YoutubeDL({
		'outtmpl': output,
		'writesubtitles': caption,
		'writeautomaticsub': caption,
		'convertsubtitles': '',
		'skip_download': no_dl,
	})

	info = dl.extract_info(program['video url']) # downloading here
	filename = re.sub(r'\..*', '', dl.prepare_filename(info))

	save(f'{filename}.txt', f'''{program["service"]} {program["date"]}
{program["series"]} #{program["index"]:02}
{program["subtitle"]}

{program["desc_series"]}

{program["desc_episode"]}

series:{program["series url"]}
episode:{program["episode url"]}
video:{program["video url"]}

accountID:{program["accountID"]}
episodeID:{program["episodeID"]}
seriesID:{program["seriesID"]}
''')

def extract_id(i):
	return i.rstrip('/').split('/')[-1].rstrip('a')

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('episodeID', type=str, nargs='*',
		help='tver url or episode id')

	parser.add_argument('--dump', action='store_true',
		help='dump responses')

	parser.add_argument('--no-dl', action='store_true',
		help='no video download')

	parser.add_argument('--caption', action='store_true',
		help='save caption')

	out_default = r'%(title)s.%(ext)s'
	out_default_raw = out_default.replace(r'%', r'%%')
	parser.add_argument('-o', '--output', type=str, default=out_default,
		help=f'output path inheriting youtube_dl output template. defult={out_default_raw}')

	parser.add_argument('--search', type=str, nargs='+')


	args = parser.parse_args()

	if args.output.endswith('/'):
		args.output += out_default

	##

	if args.search:
		search(' '.join(args.search))
	else:
		for i in map(extract_id, args.episodeID):
			download(i, args.output, args.caption, args.no_dl, args.dump)


if __name__ == '__main__':
	main()