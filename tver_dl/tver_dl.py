import requests
import sys
import re
import argparse


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


def parse_args(_args):
	parser = argparse.ArgumentParser()

	parser.add_argument('episodeID', type=str,
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


	args = parser.parse_args(_args)

	args.episodeID = args.episodeID.rstrip('/').split('/')[-1].rstrip('a')

	if args.output.endswith('/'):
		args.output += out_default

	return args


def main(_args = sys.argv[1:]):
	import youtube_dl

	args = parse_args(_args)

	program = get_program(args.episodeID, dump=args.dump)

	dl = youtube_dl.YoutubeDL({
		'outtmpl': args.output,
		'writesubtitles': args.caption,
		'writeautomaticsub': args.caption,
		'convertsubtitles': '',
		'skip_download': args.no_dl,
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


if __name__ == '__main__':
	main()