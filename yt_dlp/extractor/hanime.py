from ..utils import (
    clean_html
)

from .common import InfoExtractor


class HanimeIE(InfoExtractor):
    _VALID_URL = r'https?://hanime\.tv/videos/hentai(?P<id>.+)'
    _TEST = {
        'url': 'https://hanime.tv/videos/hentai/itadaki-seieki',
        'md5': '03593d777d81180d864e175ec21a6ae6',
        'info_dict': {
            'ext': 'mp4',
            'id': 'itadaki-seieki',
            'title': 'Itadaki! Seieki',
            'thumbnail': r're:https?://.*\.jpg$',
            'description': 'md5:7521b746547193b5fb97d0ad35fee0fd',
            'timestamp': 1465257759,
            'upload_date': str,
            'release_timestamp': 1395932400,
            'release_date': str,
            'duration': 1378000 * 1000,
            'view_count': int,
            'like_count': int,
            'dislike_count': int,
            'categories': list,
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        hentai_id = self._parse_json(
            self._search_regex(r'"hentai_video":{"id":(?P<id>\d+)', webpage, 'hentai_id'),
            video_id)

        meta = self._download_json('https://hanime.tv/api/v8/video?id=%s' % hentai_id, video_id)

        hentai_meta = meta.get('hentai_video')

        categories = []
        for category in hentai_meta.get('hentai_tags'):
            categories.append(category.get('text'))

        raw_streams = meta.get('videos_manifest').get('servers')[0].get('streams')
        streams = [{}]
        for stream in raw_streams:
            if not stream.get('url'):
                continue
            else:
                streams.append({
                    'quality': int(stream.get('height')),
                    'url': stream.get('url')
                })
        streams = [i for i in streams if i]

        formats = []
        for stream in streams:
            data = self._extract_m3u8_formats(stream.get('url'), video_id, 'mp4', entry_protocol='m3u8_native', m3u8_id='hls', fatal=False)
            data[0].update({
                'quality': stream.get('quality')
            })
            formats.extend(data)
        self._sort_formats(formats)

        info = {
            'id': hentai_meta.get('slug'),
            'title': hentai_meta.get('name'),
            'formats': formats,
            'thumbnail': hentai_meta.get('poster_url'),
            'description': clean_html(hentai_meta.get('description')),
            'timestamp': hentai_meta.get('created_at_unix'),
            'release_timestamp': hentai_meta.get('released_at_unix'),
            'duration': hentai_meta.get('duration_in_ms') * 1000,
            'view_count': hentai_meta.get('views'),
            'like_count': hentai_meta.get('likes'),
            'dislike_count': hentai_meta.get('dislikes'),
            'age_limit': 18,
            'categories': categories,
        }

        return info
