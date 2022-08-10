a tiny wrapping for [youtube-dl](https://github.com/ytdl-org/youtube-dl) to download tver episodes.

## install

```sh
pip install git+https://github.com/trnciii/tdl
```

## from console

```sh
tver-dl <url>
# or
tver-dl <episode id>
```
episode id can be found in a url as `https://tver.jp/episodes/<episode id>`.

## from python

```sh
import tver_dl

tver_dl.main([<url | episode id>])
```

## Note

* accepts only one url/episodeID for a call.
* fail to get `videoRefID` on some episodes.
