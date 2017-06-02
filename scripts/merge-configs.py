#!/usr/bin/python3
#
# Copyright 2017 Canonical, Ltd. Authored by Marco Ceppi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import os
import sys
import yaml


def get_kubeconfig(cfg):
    if not os.path.exists(cfg):
        return

    with open(cfg) as f:
        return yaml.safe_load(f.read())


def merge_cfg(cfg, new_cfg):
    if not isinstance(cfg, dict) or not isinstance(new_cfg, dict):
        return None
    for k, v in new_cfg.items():
        if k not in cfg:
            cfg[k] = v
        elif isinstance(v, list):
            cfg[k] = cfg[k] + v
        else:
            cfg[k] = merge_cfg(cfg[k], v)

    return cfg


def merge_config(kubecfg_file, newcfg_file, name):
    kubecfg = get_kubeconfig(kubecfg_file)
    newcfg = get_kubeconfig(newcfg_file)

    if not kubecfg or not newcfg:
        print("kubecfg {} newcfg {}".format(kubecfg_file, newcfg_file))
        print(kubecfg, kubecfg_file)
        return 1

    newcfg['clusters'][0]['name'] = '{}-cluster'.format(name)
    newcfg['users'][0]['name'] = '{}-user'.format(name)
    newcfg['contexts'][0]['name'] = name
    newcfg['contexts'][0]['context']['cluster'] = '{}-cluster'.format(name)
    newcfg['contexts'][0]['context']['user'] = '{}-user'.format(name)

    kubecfg = merge_cfg(kubecfg, newcfg)

    with open(kubecfg_file, 'r+') as f:
        f.seek(0)
        f.write(yaml.dump(kubecfg, default_flow_style=False))
        f.truncate()


if __name__ == '__main__':
    KUBEHOME = os.path.expanduser('~/.kube')
    KUBECONFIG_FILE = os.path.join(KUBEHOME, 'config')

    if len(sys.argv) != 3:
       print('Where da args at?' if len(sys.argv) < 3 else 'Too many args bruv')
       sys.exit(1)

    NEWCONFIG_FILE = os.path.expanduser(sys.argv[1])
    NAME = sys.argv[2]

    rc = merge_config(KUBECONFIG_FILE, NEWCONFIG_FILE, NAME) or 0
    sys.exit(rc)

