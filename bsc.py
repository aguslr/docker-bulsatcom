import io
import os
import StringIO
import gzip
import xmltv
import time
import json
import requests
import base64
from pyaes import aes


_username = str(os.environ.get('BULSAT_USER', 'test'))
_password = str(os.environ.get('BULSAT_PASS', 'test'))
_files_path = str(os.environ.get('BULSAT_DIR', './'))
_download_epg = str(os.environ.get('BULSAT_EPG', 'false'))
_cache = str(os.environ.get('BULSAT_CACHE', 'true'))
_url = str(os.environ.get('BULSAT_URL', 'https://api.iptv.bulsat.com'))
_timeout = int(os.environ.get('BULSAT_TIMEOUT', 10))
_os = int(os.environ.get('BULSAT_TIMEOUT', 1))
_debug = str(os.environ.get('BULSAT_DEBUG', 'false'))


_os_list = ['pcweb', 'samsungtv']


_s = requests.Session()

_ua = {
    'Host':'api.iptv.bulsat.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept':'*/*',
    'Accept-Language':'bg-BG,bg;q=0.8,en;q=0.6',
    'Accept-Encoding':'gzip, deflate, br',
    'Referer':'https://test.iptv.bulsat.com/iptv-login.php',
    'Origin':'https://test.iptv.bulsat.com',
    'Connection':'keep-alive'
}

def log(s):
    if _debug != 'false':
        print(s)

def login(username, password):
    url_auth = 'auth'
    # change auth url for diffrent then 'pcweb'
    if _os != 0:
        url_auth = '?' + url_auth

    r = _s.post(_url + '/' + url_auth, timeout = _timeout, headers = _ua)
    key = r.headers['challenge']
    session = r.headers['ssbulsatapi']

    if r.headers['logged'] == 'true':
        return session

    _s.headers.update({'SSBULSATAPI': session})

    enc = aes.AESModeOfOperationECB(key)
    password_crypt = enc.encrypt(password + (16 - len(password) % 16) * '\0')

    r = _s.post(_url + '/' + url_auth, timeout = _timeout, headers = _ua, data = {
        'user':['', username],
        'device_id':['', _os_list[_os]],
        'device_name':['', _os_list[_os]],
        'os_version':['', _os_list[_os]],
        'os_type':['', _os_list[_os]],
        'app_version':['', '0.01'],
        'pass':['', base64.b64encode(password_crypt)]
    })

    # debug
    log('Login ' + r.headers['logged'])
    log('Login ' + str(r.request.headers))

    return session


def get_channel(session):
    _s.headers.update({'Access-Control-Request-Method': 'POST'})
    _s.headers.update({'Access-Control-Request-Headers': 'ssbulsatapi'})
    _s.headers.update({'SSBULSATAPI': session})
    _s.options(_url + '/tv/' + _os_list[_os] + '/live', timeout = _timeout, headers = _ua)

    r = _s.post(_url + '/tv/' + _os_list[_os] + '/live', timeout = _timeout, headers = _ua)

    # debug
    log('Channel ' + str(r.status_code == requests.codes.ok))

    if r.status_code != requests.codes.ok:
        return [{}]
    else:
        # debug
        log('Channel ' + str(r.json()))

        return r.json()


def save_channel(live):
    if live[0] != '':
        play_list = u'#EXTM3U\n'
        for i, channel in enumerate(live):
            ch_epg_name = channel['epg_name']
            ch_title = channel['title']
            ch_sources = channel['sources']
            ch_radio = channel['radio']
            ch_genre = channel['genre']
            ch_id = channel['channel']

            play_list = play_list + '#EXTINF:%s radio="%s" group-title="%s" tvg-logo="%s" tvg-id="%s",%s\n%s\n' % (ch_id, ch_radio, ch_genre, ch_epg_name + '.png', ch_epg_name, ch_title, ch_sources)

        f_m3u = open(os.path.join(_files_path, '', 'bulsat.m3u'), 'wb+')
        f_m3u.write(play_list.encode('utf-8', 'replace'))
        f_m3u.close()


def get_epg(live):
    for i, channel in enumerate(live):
        if channel.has_key('program'):
            #'epg': 'nownext' / '1day' / '1week'
            r = _s.post(_url + '/' + 'epg/short', timeout = _timeout, headers = _ua, data = {'epg': '1day', 'channel': channel['epg_name']})

            if r.status_code == requests.codes.ok:
                channel['program'] = r.json().items()[0][1]['programme']

    # debug
    log('EPG ' + str(r.status_code == requests.codes.ok))
    log('EPG ' + str(live))

    return live


def save_epg(live):
    if live[0] != '':
        w = xmltv.Writer(encoding='UTF-8', date=str(time.time()), source_info_url="", source_info_name="", generator_info_name="", generator_info_url="")

        for i, channel in enumerate(live):
            w.addChannel({'display-name': [(channel['title'], u'bg')], 'id': channel['epg_name'], 'url': ['https://test.iptv.bulsat.com']})

            if channel.has_key('program'):
                for p in channel['program']:
                    if len(p['title']) > 0:
                        w.addProgramme({'start': p['start'], 'stop': p['stop'], 'title': [(p['title'], u'')], 'desc': [(p['desc'], u'')], 'category': [(channel['genre'], u'')], 'channel': channel['epg_name']})

        out = StringIO.StringIO()
        w.write(out, pretty_print=True)
        f_lmx = gzip.open(os.path.join(_files_path, '', 'bulsat.xml.gz'), 'w+', 9)
        f_lmx.write(out.getvalue())
        f_lmx.close()
        out.close()


def load_channel():
    # check if cash is enabled in settings
    if _cache == 'false':
        return False

    # check if file exist in folder
    if os.path.exists(_files_path + '/bulsat.m3u') == False:
        return False

    # get file modification (create time)
    file_time = os.path.getmtime(_files_path + '/bulsat.m3u')

    # check if it is old
    if time.time() - file_time < 60 * 60 * 1:
        return True

    return False


if not _username or not _password or not _files_path:
    # debug
    log('Settings empty')
else:
    # login
    session = login(_username, _password)

    # load data
    # channel session 2h
    if load_channel() == False:
        json_channel = get_channel(session)
        save_channel(json_channel)

        # epg
        if _download_epg != 'false':
            json_epg = get_epg(json_channel)
            save_epg(json_epg)
