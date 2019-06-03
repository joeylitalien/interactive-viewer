from __future__ import print_function

"""
A script to batch render and update interactive viewer.
"""

import os, sys
import argparse
import pyexr
import numpy as np
import json
import subprocess as sp
from analyze import update_stats, compute_stats, write_data


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Batch analysis of rendered images.')
    parser.add_argument('-mts', '--mitsuba', help='mitsuba executable', type=str, default='./mitsuba')
    parser.add_argument('-r',   '--ref', help='reference image', type=str, required=True)
    parser.add_argument('-s',   '--scene', help='scene xml file', type=str, required=True)
    parser.add_argument('-o',   '--options', help='mitsuba options', type=str)
    parser.add_argument('-d',   '--dir', help='corresponding viewer scene directory', type=str, required=True)
    parser.add_argument('-n',   '--name', help='algorithm name', type=str, required=True)
    parser.add_argument('-a',   '--alg', help='mitsuba algorithm keyword', type=str, required=True)
    parser.add_argument('-t',   '--timeout', help='render time (s)', type=int)
    parser.add_argument('-f',   '--frequency', help='intermediate image output frequency (s)', type=int)

    parser.add_argument('-m',   '--metrics', help='difference metrics', nargs='+', choices=['l1', 'l2', 'mrse', 'mape', 'smape'], type=str)
    parser.add_argument('-eps', '--epsilon', help='epsilon value', type=float, default=1e-2)
    parser.add_argument('-c',   '--clip', help='clipping values for min/max', nargs=2, type=float, default=[0,1])
    args = parser.parse_args()

    # Create Mistuba command
    fname = '{}.exr'.format(args.name.replace(' ', '-'))
    out_path = os.path.join(os.path.dirname(args.scene), fname)
    render = '{} {} -D integrator={}'.format(args.mitsuba, args.scene, args.alg)
    if args.frequency:
        render = '{} -r {}'.format(render, args.frequency)
    if args.options:
        render = '{} {}'.format(render, args.options)
    render = '{} -o {}'.format(render, out_path)
    cmd = render.split()

    # Run and time out after fixed amount of time
    sys.stdout.write('Rendering... ')
    sys.stdout.flush()
    try:
        out = sp.check_output(cmd, shell=False, timeout=args.timeout)
    except sp.TimeoutExpired as e:
        print('done.')

    # Update interactive viewer
    sys.stdout.write('Recomputing metrics... ')
    sys.stdout.flush()
    ref_fp = pyexr.open(args.ref)
    ref = np.array(ref_fp.get())
    img_fp = pyexr.open(out_path)
    img = np.array(img_fp.get())
    test = [{'name': args.name, 'data': img}]

    with open(os.path.join(args.dir, 'data.json'), 'r') as fp:
        data = json.load(fp)
    with open(os.path.join(args.dir, 'stats.json'), 'r') as fp:
        stats = json.load(fp)

    data = update_stats(args.dir, data, ref, test, args.metrics, args.clip, args.epsilon)
    write_data(args.dir, data)
    print('done.')

    web_url = os.path.abspath(os.path.join(args.dir, 'index.html'))
    print('Interactive viewer updated: {}'.format(web_url))