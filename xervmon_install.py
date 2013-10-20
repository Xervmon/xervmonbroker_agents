#!/usr/bin/env python

import sys
import os
import platform
import fileinput
import urllib2
import urllib
import re
import urlparse
import socket

import json
import subprocess
import logging

from optparse import OptionParser, make_option

DEFAULT_TENANT = 'devmaas'
DEBIAN_LIKE_SYSTEMS = ["Debian", "Mint", "Ubuntu"]
DEFAULT_INTERFACE = 'eth0'
TMP_FILE = '/tmp/tesspackage'
URL_SCHEME = 'http'
URL_DOMAIN = 'xervmon.com'
URL_API_PATH = '/sudhi/operation-kriya/index.php/api/SystemMonitor/'
URL_GET_PARAMS = {
        'key': 'X-API-KEY',
        'username': 'username',
        'host': 'host',
        }

URL_METHODS = {
        'auth': 'Authenticate',
        'enable': 'EnableHost'
        }

DEB_PACKAGE = 'https://github.com/sseshachala/xervmonbroker_agents/raw/master/distros/xervmon-broker-agent_1.2.3i2-2_all.deb'
RPM_PACKAGE = 'https://github.com/sseshachala/xervmonbroker_agents/raw/master/distros/xervmon_broker-agent-1.2.3i2-1.noarch.rpm'

AGENT_CONFIG = '/etc/xinetd.d/xervmon_broker'


def get_interface_ip(ifname):
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                            ifname[:15]))[20:24])


def make_api_url(tenant, method, params):
    netloc = '%s.%s' % (tenant, URL_DOMAIN)
    url_method = URL_METHODS.get(method)
    if url_method is None:
        # logger.error("No such method %s" % method)
        return
    url_path = urlparse.urljoin(URL_API_PATH, url_method)
    params_url = {}
    for param_name, param_value in params.items():
        param = URL_GET_PARAMS.get(param_name)
        if param is None:
            # logger.error("No such param %s" % param_name)
            return
        params_url[param] = param_value
    enc_params = urllib.urlencode(params_url)
    params = ''
    fragment = ''
    url = urlparse.urlunparse((URL_SCHEME, netloc, url_path, params,
        enc_params, fragment))
    return url


def check_ip(ip):
    """Check if given ip is valid"""
    if re.match(
            r'^(([0-1]?[0-9]{1,2}|25[0-5]|2[0-4][0-9])\.){3}([0-1]?[0-9]{1,2}|25[0-5]|2[0-4][0-9])$',
            ip):
        return True
    return False


def make_api_call(url, api_key):
    print url
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('X-API-KEY', api_key)]
        res = opener.open(url)
    except urllib2.HTTPError, e:
        # logger.error(str(e))
        print 'Couldnt authenticate. Please try another api key or contact our support'
        return
    try:
        return json.loads(res.read())
    except StandardError:
        return


def get_package(dist):
    if dist in DEBIAN_LIKE_SYSTEMS:
        package = DEB_PACKAGE
    else:
        package = RPM_PACKAGE
    return package


def get_package_install_command(dist):
    if dist in DEBIAN_LIKE_SYSTEMS:
        command = "apt-get install %s"
    else:
        command = "yum install %s"
    return command


def get_install_command(dist):
    if dist in DEBIAN_LIKE_SYSTEMS:
        command = "dpkg -i %s"
    else:
        command = "yum install %s"
    return command


def configure(broker_ip, dist):
    added = False
    for line in fileinput.input(AGENT_CONFIG, inplace=1):
        if 'only_from' in line:
            if not added:
                print ('\tonly_from = %s\n' % broker_ip),
                added = True
        else:
            print line,
    if dist not in DEBIAN_LIKE_SYSTEMS:
        subprocess.call('chkconfig xinetd on')


def install_package(installer, package):
    command = installer % package
    p1 = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    output = p1.communicate()[0]
    print output


def install(dist):
    package = get_package(dist)
    resp = urllib2.urlopen(package)
    with open(TMP_FILE, 'w') as fp:
        fp.write(resp.read())
    installer = get_install_command(dist)
    package_installer = get_package_install_command(dist)
    install_package(package_installer, 'xinetd')
    if dist not in DEBIAN_LIKE_SYSTEMS:
        install_package(package_installer, 'chkconfig')
    install_package(installer, TMP_FILE)
    return True


def get_from_input(msg):
    var = raw_input('%s\n' % msg)
    var = var.strip()
    return var


def main():
    """Main control function"""

    system = platform.system()
    dist = platform.linux_distribution()[0]
    if system != 'Linux':
        print ("We are sorry. We do not support %s. Currently support is only \
            for Linux" % system)
        sys.exit()

    run_user = os.getenv("USER")
    if run_user != 'root':
        print 'Please run script as a root'
        sys.exit()

    usage = "usage: %prog [options]"
    option_list = [
            make_option("-k", "--key", action="store", type="string",
                dest="key", help="api key. If you do not have it please contact\
                our support on website"),
            make_option("-u", "--user", action="store", type="string",
                dest="user", help="your user"),
            make_option("-H", "--host", action="store", type="string",
                dest="host", help="host of the server. Please use -i if you\
                want to detect interface ip"),
            make_option("-i", "--interface", action="store", type="string",
                dest="interface", help="default interface to detect ip if no \
                host given", default=DEFAULT_INTERFACE),
            make_option("-t", "--tenant", action="store", type="string",
                dest="tenant", default=DEFAULT_TENANT,
                help="tenant to our api service. You can check it in your dashboard"),
            ]
    parser = OptionParser(usage, option_list=option_list)
    (options, args) = parser.parse_args()
    key = options.key
    user = options.user
    host = options.host
    if host is not None and not check_ip(host):
        print "Please enter valid ip in host parameter."
        sys.exit()

    if host is None:
        try:
            host = get_interface_ip(options.interface)
        except StandardError:
            print 'Couldnt detect ip for interface %s' % options.interface
            sys.exit()

    tenant = options.tenant
    if key is None:
        key = get_from_input("Enter api key")
    if user is None:
        user = get_from_input("Enter your username")

    base_params = {'key': key, 'username': user}
    auth_url = make_api_url(tenant, 'auth', base_params)
    auth_res = make_api_call(auth_url, key)
    if auth_res is None:
        print 'Error making auth api call'
        sys.exit()
    if auth_res['response'] == 'false':
        print auth_res['error']
        sys.exit()
    broker_ip = auth_res['broker_ip']

    res_install = install(dist)
    configure(broker_ip, dist)
    if not res_install:
        print "Couldnt install package"
        sys.exit()

    enable_params = base_params.copy()
    enable_params.update({'host': host})
    enable_url = make_api_url(tenant, 'enable', enable_params)
    enable_res = make_api_call(enable_url, key)
    if enable_res is None or enable_res['response'] == 'false':
        print "Error enabling host"
    print "*** XervmonBroker Agent Successfully installed!"
    sys.exit()


if __name__ == '__main__':
    main()
