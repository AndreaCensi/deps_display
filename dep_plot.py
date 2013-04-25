#!/usr/bin/env python
import itertools
from os.path import join,exists,isdir, basename
import os
import yaml
import gvgen
from procgraph.utils import system_cmd_result



def load_data():
    f = 'deps.yaml'
    pkgs =  list(yaml.load_all(open(f)))[0]
    return pkgs
    
def main():
    pkgs = load_data()
    pkgs['bootstrapping_olympics']['requires'].remove('vehicles')
    pkgs['bootstrapping_olympics']['requires'].remove('procgraph_vehicles')
    pkgs['bootstrapping_olympics']['requires'].remove('vehicles_cairo')
    pkgs['boot_agents']['requires'].remove('vehicles')

    plot_pkgs(pkgs)

def plot_pkgs(pkgs, ignore_repo=['contracts'], cluster=False):
    graph = gvgen.GvGen()

    pkg2node = {}

    if cluster:
        repo2node = {}
        for id_pkg, pkg in pkgs.items():
            repo = pkg['repo']
            if repo in ignore_repo:
                continue
            if not repo in repo2node:
                repo2node[repo] = graph.newItem(repo)


    if cluster:
        pkg2node['procgraph'] = graph.newItem('procgraph', repo2node['procgraph'])
    else:
        pkg2node['procgraph'] = graph.newItem('procgraph')
    


    for id_pkg, pkg in pkgs.items():
        repo = pkg['repo']
        if repo in ignore_repo:
            continue

        if repo == 'procgraph':
            pkg2node[id_pkg]  = pkg2node['procgraph']
        else:
            if cluster:
                pkg2node[id_pkg] = graph.newItem(id_pkg, repo2node[repo])
            else:
                pkg2node[id_pkg] = graph.newItem(id_pkg)

    for id_pkg, pkg in pkgs.items():
        for child in pkg['requires']:
            child_repo = pkgs[child]['repo']
            if child_repo in ignore_repo:
                continue
            same_repo = pkgs[id_pkg]['repo'] == child_repo
            if not same_repo:
                graph.newLink(pkg2node[id_pkg], pkg2node[child])

    # TODO: add check?
    out = 'deps.dot'
    with open(out, 'w') as f:
        graph.dot(f)

    cmd = ['dot', out, '-Tpng', '-o', out + '.png']
    system_cmd_result('.', cmd, raise_on_error=True)

if __name__ == '__main__':
    main()