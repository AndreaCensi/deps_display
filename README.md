Simple tool to plot dependencies between Python modules.
=================================================


The input file is a [Patience][patience]-compatible resources.yaml ([see example][example-resources]).

The ``deps-find`` command finds the dependencies:

    deps-find --resources=resources.yaml --output=deps/deps.yaml

The ``deps-plot`` command plots the dependencies:


    deps-plot --deps=deps/deps.yaml -o deps/all

The ``--cluster`` option clusters the packages by repo:

    deps-plot --deps=deps/deps.yaml -o deps/cluster --cluster

Use ``--ignore_repo`` or ``--ignore_pkg`` to ignore repos/packages while drawing:

    deps-plot --deps=deps/deps.yaml -o deps/clearer --ignore_repo contracts conf_tools reprep system_cmd compmake comptests procgraph

See below for some examples, contained in the [``example-output`` directory][example-output].

[patience]: https://github.com/AndreaCensi/patience
[example-output]: example-output/
[example-resources]: https://github.com/AndreaCensi/env_fault/blob/master/resources.yaml

<img src='blob/env_fault/example_output/all.png?raw=true'/>
<img src='blob/env_fault/example_output/cluster.png?raw=true'/>
<img src='blob/env_fault/example_output/clearer.png?raw=true'/>
