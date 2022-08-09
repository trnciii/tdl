import requests, youtube_dl
import sys
import re


def get_episode(episodeID):
	response = requests.get(
		f'https://statics.tver.jp/content/episode/{episodeID}.json',
		params={
			'v': '8',
		}
	)

	if response.ok:
		return response.json()
	else:
		print('failed in get_episode')
		print(response.reason)
		return None


def get_video_id(accountID, videoRef, key):
	response = requests.get(
		f'https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref:{videoRef}',
		headers={
			'accept': f'application/json;pk={key}'
		}
	)

	if response.ok:
		return response.json()
	else:
		print('failed in get_video_id')
		print(response.reason)
		return None


def get_key(accountID, playerID):
	response = requests.get(
		f'https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js',
		headers={}
	)
	if response.ok:
		return re.search(
			r'(?<=policyKey:")(.*?)(?=")',
			response.text
		).groups(0)[0]
	else:
		print('failed in get_key')
		print(response.reason)
		exit()


def main(args = sys.argv[1:]):
	episodeID = args[0].rstrip('a')

	episodeRes = get_episode(episodeID)
	if episodeRes == None:
		exit()

	vid = episodeRes['video']
	accountID = vid['accountID']
	videoRef = vid['videoRefID']
	playerID = vid['playerID']
	print(f'{accountID=}')
	print(f'{videoRef=}')
	print(f'{playerID=}')


	key = get_key(accountID, playerID)
	print(f'{key=}')


	videoRes = get_video_id(accountID, videoRef, key)
	if videoRes == None:
		exit()

	videoID = videoRes['id']
	title = videoRes['name']
	desc = videoRes['description']

	print(f'{accountID=}')
	print(f'{title=}')
	print(f'{videoID=}')


	url = f'http://players.brightcove.net/{accountID}/default_default/index.html?videoId={videoID}'
	print(f'{url=}')


	dl = youtube_dl.YoutubeDL({
		'outtmpl': f'{title}.mp4',
		'writesubtitles': True,
		'writeautomaticsub': True,
		'convertsubtitles': 'srt',
	})
	filename = re.sub(r'\..*', '', dl.prepare_filename({}))

	print(f'{filename=}')

	with open(f'{filename}.txt', 'w', encoding='utf-8') as f:
		f.write(f'{title}\n')
		f.write(desc)

	dl.download([url])


if __name__ == '__main__':
	main()