import io
import os
import StringIO
import xmltv
import time
import json
import requests
import base64
from pyaes import aes
import argparse


parser = argparse.ArgumentParser(description='Usage: %prog [options]')
parser.add_argument(
        '--username',
        help=u'Username for Bulsatcom',
        default=os.environ.get('BULSAT_USERNAME', 'test'))
parser.add_argument(
        '--password',
        help=u'Password for Bulsatcom',
        default=os.environ.get('BULSAT_PASSWORD', 'test'))
parser.add_argument(
        '--output',
        help=u'Output directory',
        default=os.environ.get('BULSAT_OUTPUT', './'))
parser.add_argument(
        '--url',
        help=u'URL of API endpoint',
        default=os.environ.get('BULSAT_URL',
                                   'https://api.iptv.bulsat.com'))
parser.add_argument(
        '--timeout',
        help=u'Timeout in seconds (default: 10)',
        default=os.environ.get('BULSAT_TIMEOUT', 10))
parser.add_argument(
        '--os',
        help=u'OS Type [0: pcweb, 1: samsungtv] (default: 1)',
        default=os.environ.get('BULSAT_OS', 1))
parser.add_argument(
        '--epg',
        help=u'Download EPG',
        action='store_true',
        default=os.environ.get('BULSAT_EPG', False))
parser.add_argument(
        '--cache',
        help=u'Enable cache',
        action='store_true',
        default=os.environ.get('BULSAT_CACHE', False))
parser.add_argument(
        '--debug',
        help=u'Enable debugging',
        action='store_true',
        default=os.environ.get('BULSAT_DEBUG', False))
args = parser.parse_args()


_username = str(args.username)
_password = str(args.password)
_files_path = str(args.output)
_download_epg = bool(args.epg)
_cache = bool(args.cache)
_url = str(args.url)
_timeout = int(args.timeout)
_os = int(args.os)
_debug = bool(args.debug)


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
    if _debug:
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

    if str(r.headers['logged']) != 'true':
        raise SystemExit('Error: Could not log into API')

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
                p = channel['program']
                # debug
                log(p)
                if len(p['title']) > 0:
                    w.addProgramme({'start': p['start'], 'stop': p['stop'], 'title': [(p['title'], u'')], 'desc': [(p['desc'], u'')], 'category': [(channel['genre'], u'')], 'channel': channel['epg_name']})

        out = StringIO.StringIO()
        w.write(out, pretty_print=True)
        f_lmx = open(os.path.join(_files_path, '', 'bulsat.xml'), 'w+', 9)
        f_lmx.write(out.getvalue())
        f_lmx.close()
        out.close()


def load_channel():
    # check if cash is enabled in settings
    if not _cache:
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
    raise SystemExit('Error: Missing required parameters')
elif not os.access(_files_path, os.W_OK):
    raise SystemExit('Error: Cannot write to output directory')
else:
    # login
    session = login(_username, _password)

    # load data
    # channel session 2h
    if load_channel() == False:
        json_channel = get_channel(session)
        save_channel(json_channel)

        # epg
        if _download_epg:
            json_epg = get_epg(json_channel)
            save_epg(json_epg)
