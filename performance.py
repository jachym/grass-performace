#!/usr/bin/env python

from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules import Module
from grass.script import core as grass

import time, sys, cProfile
from optparse import OptionParser

COORDINATES = [
    [527859.005, 5522555.3149999995] # middle of czech
]

MODULES = [
    #["r.basins.fill"],
    #["r.bitpattern"],
    ["v.to.rast", {
        'input': 'reky',
        'use': 'attr',
        'attrcolumn': 'cat',
        'output': 'reky'
    }],
    ["r.blend", {
                    'first': 'inputraster1',
                    'second': 'inputraster2',
                    'output_prefix': 'elev_shade_blend'
                 }
    ],
    ["r.buffer", {
            'input': 'reky',
            'output': 'reky_buffer1',
            'distances': [1, 100, 200]
        }
    ],
    ["r.buffer.lowmem", {
            'input': 'reky',
            'output': 'reky_buffer2',
            'distances': [1, 100, 200]
        }
    ],
    ["r.carve", {
        'rast': 'dem_gtopo30',
        'vect': 'reky',
        'output': 'carve'
    }],
    ["r.category", {
        'map': 'inputraster1',
        'raster': 'inputraster2'
    }],
    ["r.circle", {
        "output": "circle",
        "coordinate": [COORDINATES[0][0], COORDINATES[0][1]],
        "max": 10000.
    }],
    ["r.clump", {
        "input": "inputraster1",
        "output": "clump"
    }],
    ["r.coin", {
        "map1": "inputraster1",
        "map2": "inputraster2",
        "units": "c"
    }],
    ["r.colors", {
        "map":"inputraster1",
        "raster":"inputraster2"
    }],
    ["r.colors.out", {}],
    ["r.colors.stddev", {}],
    ["r.composite", {}],
    ["r.compress", {}],
    ["r.contour", {}],
    ["r.cost", {}],
    ["r.covar", {}],
    ["r.cross", {}],
    ["r.describe", {}],
    ["r.distance", {}],
    ["r.drain", {}]
]


def tear_down():
    """Delete randomly created data
    """

    mlist = grass.pipe_command('g.mlist', type='rast', mapset='.')
    for raster in mlist.stdout:
        g.remove(rast=raster.strip())

    mlist = grass.pipe_command('g.mlist', type='vect', mapset='.')
    for vector in mlist.stdout:
        g.remove(vect=vector.strip())


def start_up():
    """Prepare input raster and vector data
    """
    # czech republic, resolution 1km
    g.region(flags="d", res='1000')
    r.random_surface(output='inputraster1')
    r.random_surface(output='inputraster2')


def test_module(name, kwargs):
    """Run tests for given module
    """

    #start_time = time.time()


    def run():
        module = Module(name, **kwargs)

    p = cProfile.Profile(time.clock)
    p.runcall(run)
    print p.snapshot_stats()

    #elapsed_time = time.time() - start_time
    #print name, elapsed_time


def __find_module__(mname):
    for m in MODULES:
        if m[0] == mname:
            return m

    return None

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-m", "--module", dest="module",
                  help="module you want to run (default is all)", metavar="NAME")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    modules = []
    if options.module:
        module = __find_module__(options.module)
        if not module:
            print "ERROR: Module %s not implemented" % options.module
            sys.exit(1)
    else:
        modules = MODULES

    start_up()

    for m in modules:

        test_module(m[0], m[1])

    tear_down()


