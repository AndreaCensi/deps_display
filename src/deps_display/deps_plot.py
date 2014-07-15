from quickapp import QuickAppBase
from system_cmd import system_cmd_result
import yaml
from contracts import contract
import os


class DepsPlot(QuickAppBase):
    """ Creates plots from the data found by deps-find. """
    cmd = 'deps-plot'
    
    def define_program_options(self, params):
        params.add_string('deps', default='deps.yaml')
        params.add_string_list('ignore_repo', default=[])
        params.add_string_list('ignore_pkg', default=[])
        
        params.add_flag('cluster', help='Cluster packages in repos.')
        params.add_string('output', short='o', default='deps-plot-out',
                          help='Prefix for output files.')
    
    def go(self):
        options = self.get_options()
        deps = options.deps
        ignore_repo = options.ignore_repo
        ignore_pkg = options.ignore_pkg
        cluster = options.cluster
        output = options.output
        
        pkgs = load_data(deps)
        pkgs = filter_data(pkgs, ignore_repo=ignore_repo, ignore_pkg=ignore_pkg)

        if False:
            for id_pkg, p in pkgs.items():
                requires = set(p['requires'])
                required_by = set(p['required_by'])
                both =requires & required_by 
                if both:
                    print('%s: %s' % (id_pkg, both))
                
        plot_pkgs(pkgs, out=output, ignore_repo=ignore_repo, cluster=cluster)

            
main_deps_plot = DepsPlot.get_sys_main()

@contract(pkgs='dict(str:*)', returns='dict(str:*)')
def filter_data(pkgs, ignore_repo=[], ignore_pkg=[]):
    def include_repo(repo):
        return not repo in ignore_repo
    def include_pkg(id_pkg):
        if id_pkg in ignore_pkg:
            return False
        return include_repo(pkgs[id_pkg]['repo'])
    
    def filter_pkg_list(ps):
        return filter(include_pkg, ps)
    
    def filter_pkg(p):
        r = {}
        r['id_package'] = p['id_package']
        r['repo'] = p['repo']
        r['src'] = p['src']
        r['required_by'] = filter_pkg_list(p['required_by'])  
        r['requires'] = filter_pkg_list(p['requires'])
        return r
    
    res = {}
    for id_pkg, p in pkgs.items():
        if include_pkg(id_pkg):
            res[id_pkg] = filter_pkg(p)
        else:
            print('excluding %s' % id_pkg)
    return res
    

@contract(returns='dict(str:*)')
def load_data(f):
    pkgs = list(yaml.load_all(open(f)))[0]
    return pkgs
     
     

def plot_pkgs(pkgs, out, ignore_repo=[], cluster=False,
              link_same_repo=True):
    
    dirname = os.path.dirname(out)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
        
    import gvgen
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
                pkg2node[id_pkg] = graph.newItem(id_pkg, get_repo_node(repo))
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
#             if not same_repo:
            if link_same_repo or not same_repo:
                l = graph.newLink(get_pkg_node(id_pkg), get_pkg_node(child))
                
                d12 = child in pkgs[id_pkg]['requires']
                d21 = id_pkg in pkgs[child]['requires']
                loop = d12 and d21
                if loop: 
                    graph.propertyAppend(l,"color","red")

    # TODO: add check?
    
    with open(out, 'w') as f:
        graph.dot(f)

    cmd = ['dot', out, '-Tpng', '-o', out + '.png']
    system_cmd_result('.', cmd, raise_on_error=True)
