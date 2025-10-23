import os
from sys import path as sys_path
from ipaddress import ip_address
from requests import head as requests_head


def find_package_project_dir():
    for path_str in sys_path:
        try:
            try_path = os.path.join(path_str, 'lampsible', 'project')
            assert os.path.isdir(try_path)
            return try_path
        except AssertionError:
            pass
    raise RuntimeError("""
        Could not find a 'project_dir' for Ansible Runner in the expected
        location. Your Lampsible installation is likely broken, please reinstall.
        """)


def host_is_local(host):
    if host.lower() == 'localhost':
        return True
    try:
        tmp_ip = ip_address(host)
        return tmp_ip.is_loopback
    except ValueError:
        return False


def host_is_private(host):
    try:
        tmp_ip = ip_address(host)
        return tmp_ip.is_private or tmp_ip.is_link_local
    except ValueError:
        return False


def is_valid_wordpress_version(wp_version):
    from .constants import RECENT_WORDPRESS_VERSIONS
    if wp_version in RECENT_WORDPRESS_VERSIONS:
        return True

    try:
        r = requests_head(
            'https://wordpress.org/wordpress-{}.tar.gz'.format(wp_version)
        )
        assert r.status_code == 200
        return True
    except AssertionError:
        return False
