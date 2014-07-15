from os.path import basename, exists, isdir, join
from system_cmd import system_cmd_result
import itertools
import os
import yaml
from quickapp import QuickAppBase


class DepsFind(QuickAppBase):
    """ 
        Finds packages defined in a Patience-compatible file and computes their dependences.
    """
    
    cmd = 'deps-find'
    
    def define_program_options(self, params):
        params.add_string('resources', default='../../resources.yaml')
        params.add_string('output', default='deps.yaml')
        
    
    def go(self):
        options = self.get_options()
        resources = options.resources
        output = options.output
            
        self.info('loading from %s' % resources)
        pkgs = load_packages_multi(resources)
        self.info('Found %d packages' % len(pkgs))
        for p in pkgs:
            p['requires'] = []
            p['required_by'] = []
    
        pkgs = dict([(p['id_package'], p) for p in pkgs])
        for p1, p2 in itertools.product(pkgs, pkgs):
            if p1 == p2: continue
            req = requires(pkgs[p1], pkgs[p2])
            if req:
                pkgs[p1]['requires'].append(p2)
                pkgs[p2]['required_by'].append(p1)
    
        self.info('writing to %s' % output)
        with open(output, 'w') as f:
            f.write(yaml.dump(pkgs))



main_deps_find = DepsFind.get_sys_main()
 

def load_packages(resources):
    root = os.path.dirname(resources)

    pkgs =  list(yaml.load_all(open(resources)))
    use = []
    for p in pkgs:
        p['id_package'] = basename(p['dir']) 
        if not exists(join(root, p['dir'], 'setup.py')):
            continue
        src = join(root, p['dir'], 'src')
        if not exists(src):
            #print('unknonw %r' % src)
            continue
        roots = os.listdir(src)
        this_pkgs = []
        for r in roots:
            if 'egg-info' in r:
                continue
            if not isdir(join(src,r)):
                continue
            this_pkgs.append(r)
        p['src'] = src
        p['packages'] = this_pkgs
        use.append(p)
    return use

def load_packages_multi(resources):
    root = os.path.dirname(resources)

    pkgs =  list(yaml.load_all(open(resources)))[0]
    use = []
    for p in pkgs:
        
        p['id_package'] = basename(p['dir']) 
        if not exists(join(root, p['dir'], 'setup.py')):
            continue
        src = join(root, p['dir'], 'src')
        if not exists(src):
            #print('unknonw %r' % src)
            continue
        roots = os.listdir(src)
        
        for r in roots:
            if 'egg-info' in r:
                continue
            if not isdir(join(src,r)):
                continue
            a = dict()
            a['src'] = join(src,r)
            a['repo'] = basename(p['dir'])
            a['id_package'] = r
            use.append(a)
    return use


def src_cites_pkg(src, pkg):
    cmd = ['grep', '-r', ' ' + pkg, src]
    print " ".join(cmd)
    res = system_cmd_result('.', cmd,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=False,
                      capture_keyboard_interrupt=True)  
    if res.ret == 1:
        return False
        # not found
    elif res.ret == 0:
        # found

        out = res.stdout
        if 'import' in out:
            return True
        else:
            return False
        # print out
        # # print res.stdout.split('\n')[-1]
        return True
    elif res.ret == -1: # error 
        raise Exception(res)
    

def requires(p1, p2):
    if 'packages' in p2:
        for pkg in p2['packages']:
            if src_cites_pkg(p1['src'], pkg):
                return True
    else:
        if src_cites_pkg(p1['src'], p2['id_package']):
            return True
    
    return False



    # graph = gvgen.GvGen()

    # pkg2node = {}
    # for id_pkg, pkg in pkgs.items():
    #     pkg2node[id_pkg] = graph.newItem(id_pkg)

    # for id_pkg, pkg in pkgs.items():
    #     print('%10s requires %10s' % (id_pkg, pkg['requires']))
    #     print('%10s required by %10s' % (id_pkg, pkg['required_by']))

    #     for child in pkg['requires']:
    #         graph.newLink(pkg2node[id_pkg], pkg2node[child])


    # # TODO: add check?
    # out = 'deps.dot'
    # with open(out, 'w') as f:
    #     graph.dot(f)

    # cmd = ['dot', out, '-Tpng', '-o', out + '.png']
    # system_cmd_result('.', cmd, raise_on_error=True)

