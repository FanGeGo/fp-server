# coding: utf-8
import re
import time

import config

key_prefix = 'proxy_'
searchable_keys = ('anonymity', 'scheme', 'ip', 'port')

IP_PATTERN = re.compile(r'^(\d+\.){3}\d+$')
PORT_PATTERN = re.compile(r'^\d+$')
IP_PORT_PATTERN = re.compile(r'^(\d+\.){3}\d+:\d+$')


def get_searchable_spec(spec):
    """
    :spec: filter the search conditions
    :return: dict
    """
    _spec = {}

    if spec:
        _spec = {k: v for k, v in spec.items()
                 if k in searchable_keys}

    return _spec


def build_key(item):
    """
    proxy items' key in redis
    """
    key = '{prefix}{anonymity}:{scheme}:{ip}:{port}'.format(
        prefix=key_prefix,
        anonymity=item['anonymity'],
        scheme=item['scheme'],
        ip=item['ip'],
        port=item['port'],
    )

    return key


def build_pattern(spec):
    """
    build pattern for searching

    :return: str
    """
    _pattern = '%s%s:%s:%s:%s' % (
        key_prefix,
        spec.get('anonymity') or '*',
        spec.get('scheme') or '*',
        spec.get('ip') or '*',
        spec.get('port') or '*',
    )

    return _pattern


def exceed_check_period(last_check):
    interval = config.PROXY_STORE_CHECK_SEC
    now = int(time.time())

    return now - int(last_check) > int(interval)


def valid_format(proxy_item):
    """
    check the format of ip and port

    :return: bool
    """
    scheme = proxy_item.get('scheme', '')
    ip = proxy_item.get('ip', '')
    port = proxy_item.get('port', '')
    anonymity = proxy_item.get('anonymity', 'transparent')
    if not isinstance(port, str):
        port = str(port)

    def _conditions():
        yield scheme and ip and port
        yield scheme.lower() in ('http', 'https')
        yield anonymity in ('anonymous', 'transparent')
        yield IP_PATTERN.match(ip)
        yield PORT_PATTERN.match(port)

    return all(_conditions())
