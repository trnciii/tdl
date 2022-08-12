a tiny wrapping for [youtube-dl](https://github.com/ytdl-org/youtube-dl) to download tver episodes.

## install

```sh
pip install git+https://github.com/trnciii/tdl
```

or install a local clone in editable mode

```sh
git clone https://github.com/trnciii/tdl
cd tdl
pip install -e .
```


## from console

```sh
tver-dl <url or episode id> <options>
```
Video and program info are saved in current directory.
Episode id is a string that starts with 'ep-' and found in a url as `https://tver.jp/episodes/<episode id>`.

### options

* `-o --output` sets output name inheriting [youtube-dl output template](https://github.com/ytdl-org/youtube-dl#output-template).
* `--dump` saves responses for all internal requests.
* `--no-dl` prevents downloading the video file.
* `--caption` saves caption.vtt file.


## from python

The below code downloads in the same way as console script.

```py
import tver_dl
tver_dl.main([list of arguments])
```

In `tver_dl.main` function, the direct link to the video is composed and passed to `youtube-dl`.
Actually, `tver_dl.get_program(episodeID, dump=False)` is doing it as well as collecting some useful information.

```py
import tver_dl

program = tver_dl.get_program('episode id')

print(program['video url']) # video url to be passed to youtube-dl
print(program['series']) # series title
print(program['subtitle']) # title of the episode
print(program['service']) # the name of the service, or broadcast provider
print(program['caption']) # if the episode is captioned
...
```

See what `tver_dl.tver_dl:get_program` returns for more items.
`tver_dl.tver_dl:main` is also a demo of how to use them.


## dependency

* [requests](https://requests.readthedocs.io/en/latest/)
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)


## Note

* accepts only one url/episodeID for a call.
* fail to get `videoRefID` on some episodes.
