#!/usr/bin/env python
import itertools
from os.path import join, exists, isdir, basename
import os
import yaml
import gvgen
from procgraph.utils import system_cmd_result



def load_data():
    f = 'deps.yaml'
    pkgs = list(yaml.load_all(open(f)))[0]
    return pkgs
    
def main():
    pkgs = load_data()
#    pkgs['bootstrapping_olympics']['requires'].remove('vehicles')
 #   pkgs['bootstrapping_olympics']['requires'].remove('procgraph_vehicles')
 #   pkgs['bootstrapping_olympics']['requires'].remove('vehicles_cairo')
 #   pkgs['boot_agents']['requires'].remove('vehicles')

    plot_pkgs(pkgs)

def plot_pkgs(pkgs, ignore_repo=[], cluster=False):
    graph = gvgen.GvGen()
    repo2node = {}
    pkg2node = {}

    def get_repo_node(repo):
        if not repo in repo2node:
            repo2node[repo] = graph.newItem(repo)
        return repo2node[repo] 

    def get_pkg_node(id_pkg):
        if not id_pkg in pkg2node:
            if cluster:
                pkg2node[id_pkg] = graph.newItem(id_pkg, repo2node[repo])
            else:
                pkg2node[id_pkg] = graph.newItem(id_pkg)        
        return pkg2node[id_pkg]


    # if cluster:
    #     repo2node = {}
    #     for id_pkg, pkg in pkgs.items():
    #         repo = pkg['repo']
    #         if repo in ignore_repo:
    #             continue
    #         if not repo in repo2node:
    #             repo2node[repo] = graph.newItem(repo)


    # if cluster:
    #     pkg2node['procgraph'] = graph.newItem('procgraph', repo2node['procgraph'])
    # else:
    #     pkg2node['procgraph'] = graph.newItem('procgraph')
    

    for id_pkg, pkg in pkgs.items():
        repo = pkg['repo']
        if repo in ignore_repo:
            continue

        # if repo == 'procgraph':
        #     pkg2node[id_pkg]  = pkg2node['procgraph']
        # else:
        get_pkg_node(id_pkg)

    for id_pkg, pkg in pkgs.items():
        for child in pkg['requires']:
            if not child in pkgs:
                print('warning, %s dependence %s not found in list' % (id_pkg, child))
            else:    
                child_repo = pkgs[child]['repo']
                if child_repo in ignore_repo:
                    continue
            same_repo = pkgs[id_pkg]['repo'] == child_repo
            if not same_repo:
                graph.newLink(get_pkg_node(id_pkg), get_pkg_node(child))

    # TODO: add check?
    out = 'deps.dot'
    with open(out, 'w') as f:
        graph.dot(f)

    cmd = ['dot', out, '-Tpng', '-o', out + '.png']
    system_cmd_result('.', cmd, raise_on_error=True)

if __name__ == '__main__':
    main()
