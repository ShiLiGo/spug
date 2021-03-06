# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the MIT License.
from libs.ssh import SSH
from apps.host.models import Host
from apps.setting.utils import AppSetting
from socket import socket
import requests
import logging

logging.captureWarnings(True)


def site_check(url):
    try:
        res = requests.get(url, timeout=10, verify=False)
        return 200 <= res.status_code < 400, f'返回状态码：{res.status_code}'
    except Exception as e:
        return False, f'异常信息：{e}'


def port_check(addr, port):
    try:
        sock = socket()
        sock.settimeout(5)
        sock.connect((addr, int(port)))
        return True, None
    except Exception as e:
        return False, f'异常信息：{e}'


def host_executor(host, pkey, command):
    try:
        cli = SSH(host.hostname, host.port, host.username, pkey=pkey)
        exit_code, out = cli.exec_command(command)
        return exit_code == 0, out.decode()
    except Exception as e:
        return False, f'异常信息：{e}'


def dispatch(tp, addr, extra):
    if tp == '1':
        return site_check(addr)
    elif tp == '2':
        return port_check(addr, extra)
    elif tp == '3':
        command = f'ps -ef|grep -v grep|grep {extra!r}'
    elif tp == '4':
        command = extra
    else:
        raise TypeError(f'invalid monitor type: {tp!r}')
    pkey = AppSetting.get('private_key')
    host = Host.objects.filter(pk=addr).first()
    return host_executor(host, pkey, command)
