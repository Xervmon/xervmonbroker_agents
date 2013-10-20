#!/usr/bin/env python

import sys
import os
import platform
import urllib2
import urllib
import urlparse
import socket

import json
import subprocess
import logging

from optparse import OptionParser, make_option

DEFAULT_TENNANT = 'devmaas'
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


def make_api_url(tennant, method, params):
    netloc = '%s.%s' % (tennant, URL_DOMAIN)
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


def make_api_call(url):
    try:
        res = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        # logger.error(str(e))
        raise
        return
    try:
        return json.loads(res.read())
    except StandardError:
        return


def get_package(dist):
    if dist in ["Debian", "Mint", "Ubuntu"]:
        package = DEB_PACKAGE
    else:
        package = RPM_PACKAGE
    return package


def get_install_command(dist):
    if dist in ["Debian", "Mint", "Ubuntu"]:
        command = "sudo dpkg -i %s"
    else:
        command = "sudo yum install %s"
    return command


def install_package():
    system = platform.system()
    if system != 'Linux':
        print ("We are sorry. We do not support %s. Currently support is only \
            for Linux" % system)
        sys.exit()
    dist = system.linux_distribution()[0]
    package = get_package(dist)
    resp = urllib2.urlopen(package)
    with open(TMP_FILE, 'w') as fp:
        fp.write(resp)
    command = get_install_command(dist)
    p1 = subprocess.Popen([command % TMP_FILE], stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    print output
    return True


def main():
    """Main control function"""

    usage = "usage: %prog [options]"
    option_list = [
            make_option("-k", "--key", action="store", type="string",
                dest="key"),
            make_option("-u", "--user", action="store", type="string",
                dest="user"),
            make_option("-H", "--host", action="store", type="string",
                dest="host"),
            make_option("-t", "--tennant", action="store", type="string",
                dest="tennant", default=DEFAULT_TENNANT),
            ]
    parser = OptionParser(usage, option_list=option_list)
    (options, args) = parser.parse_args()
    key = options.key
    user = options.user
    host = options.host
    tennant = options.tennant
    if key is None:
        key = raw_input("Enter api key\n")
    if user is None:
        user = raw_input("Enter your username\n")
    if host is None:
        host = raw_input("Please enter your public host\n")
    base_params = {'key': key, 'username': user}
    auth_url = make_api_url(tennant, 'auth', base_params)
    print auth_url
    auth_res = make_api_call(auth_url)
    if auth_res is None:
        print 'Error making auth api call'
        sys.exit()
    if auth_res['status'] == 'false':
        print auth_res['error']
        sys.exit()

    res_install = install_package()
    if not res_install:
        print "Couldnt install package"
        sys.exit()

    enable_params = base_params.copy()
    enable_params.update({'host': host})
    enable_url = make_api_url(tennant, 'enable', enable_params)
    enable_res = make_api_call(enable_url)
    if enable_res is None or enable_res['status'] == 'false':
        print "Error enabling host"
    print "Successful install"
    sys.exit()


if __name__ == '__main__':
    main()
