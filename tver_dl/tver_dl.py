import requests, youtube_dl
import sys
import re


def request_episode(episodeID, dump=False):
	response = requests.get(
		f'https://statics.tver.jp/content/episode/{episodeID}.json',
		params={
			'v': '8',
		}
	)

	if response.ok:
		if dump:
			with open(f'episode_{episodeID}.json', 'w', encoding='utf-8') as f:
				f.write(response.text)
		return response.json()
	else:
		print('failed to get episode info')
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
		if dump:
			with open(f'video_{accountID}_{videoRef}.json', 'w', encoding='utf-8') as f:
				f.write(response.text)
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
		if dump:
			with open(f'key_{accountID}.js', 'w', encoding='utf-8') as f:
				f.write(response.text)
		return re.search(
			r'(?<=policyKey:")(.*?)(?=")',
			response.text
		).groups(0)[0]

	else:
		print('failed to get policy key')
		print(response.reason)
		exit()


def get_program(episodeID, dump=False):
	episodeRes = request_episode(episodeID, dump=dump)
	if episodeRes == None:
		exit()

	vid = episodeRes['video']
	accountID = vid['accountID']
	videoRef = vid['videoRefID']
	playerID = vid['playerID']
	print(f'{accountID=}')
	print(f'{videoRef=}')
	print(f'{playerID=}')


	key = get_key(accountID, playerID, dump=dump)
	print(f'{key=}')


	videoRes = request_video(accountID, videoRef, key, dump=dump)
	if videoRes == None:
		exit()

	videoID = videoRes['id']
	title = videoRes['name']
	desc = videoRes['description']

	return {
		'title': title,
		'desc': desc,
		'episode url': f'https://tver.jp/episodes/{episodeID}',
		'video url': f'http://players.brightcove.net/{accountID}/default_default/index.html?videoId={videoID}'
	}


def main(args = sys.argv[1:]):
	episodeID = args[0].rstrip('/').split('/')[-1].rstrip('a')

	program = get_program(episodeID, 'dump' in args)

	dl = youtube_dl.YoutubeDL({
		'outtmpl': f'{program["title"]}.mp4',
		'writesubtitles': True,
		'writeautomaticsub': True,
		'convertsubtitles': 'srt',
	})
	filename = re.sub(r'\..*', '', dl.prepare_filename({}))
	print(f'{filename=}')


	with open(f'{filename}.txt', 'w', encoding='utf-8') as f:
		f.write(f'{program["title"]}\n')
		f.write(f'{program["desc"]}\n')
		f.write('\n')
		f.write(f'episode url=\'{program["episode url"]}\'\n')
		f.write(f'video url=\'{program["video url"]}\'\n')

	dl.download([program['video url']])


if __name__ == '__main__':
	main()