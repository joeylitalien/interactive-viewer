from __future__ import print_function

"""
A script to analyze performance by comparing images 
using different metrics. To be used in conjuction 
with Jeri in-browser visualization tool.
"""

import os, sys
import argparse
import pyexr
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json
import csv
import math
from metric import compute_metric, falsecolor


def generate_thumbnail(path_dir, ref):
    """Generate thumbnail image for index."""

    thumb_w, thumb_h = 640, 360
    img = Image.fromarray((pyexr.tonemap(ref) * 255).astype(np.uint8))
    w, h = img.size
    resized_h = [w, h].index(max([w, h]))
    ratio = thumb_h / h if resized_h else thumb_w / w

    w, h = int(w * ratio), int(h * ratio)
    thumb = img.resize((w, h), resample=Image.BICUBIC)

    bg = Image.new('RGBA', (thumb_w, thumb_h), (0,0,0,255))
    if resized_h:
        bg.paste(thumb, (int((thumb_w - w) / 2), 0))
    else:
        bg.paste(thumb, (0, int((thumb_h - h) / 2)))

    bg.save(os.path.join(path_dir, 'thumb.png'))


def write_data(path_dir, data):
    """Update JS dictionary files."""
    
    with open(os.path.join(path_dir, 'data.json'), 'w') as fp:
        json.dump(data, fp, indent=4)
    
    data_js = 'const data =\n' + json.dumps(data, indent=4)
    with open(os.path.join(path_dir, 'data.js'), 'w') as fp:
        fp.write(data_js)


def hdr_to_ldr(path_dir, img):
    """HDR to LDR conversion for web display."""

    ldr = Image.fromarray((pyexr.tonemap(img['data']) * 255).astype(np.uint8))
    ldr_fname = '{}.png'.format(img['name'])
    ldr_path = os.path.join(path_dir, ldr_fname)
    ldr.save(ldr_path)
    ldr_entry = {'title': img['name'], 'version': '-', 'image': ldr_fname}
    return ldr_entry


def parse_stats(test_dirs, test_names):
    """Parse Mitsuba statistics file.
    Ugly but it does the job; could use regex.
    TODO: Incorporate this into data dictionary.
    """

    stat_dicts = {}
    for t, test_dir in enumerate(test_dirs):
        stat_file = '{}_stats.txt'.format('_'.join(test_dir.split('_')[:-1]))
        with open(os.path.join(test_dir, stat_file), 'r') as fp:
            stat_txt = fp.read()

        stat_dict = {}
        stats = stat_txt.split('*')[2:]
        stats = [s.replace('\n', '').split(' - ') for s in stats]
        for i, stat in enumerate(stats):
            stats[i] = [s.strip().replace('--','') for s in stat]
        stats[0][0] = 'Algorithm'
        for stat in stats:
            entry = {}
            for s in stat[1:]:
                l = s.split(' : ')
                entry[l[0]] = l[1]
            stat_dict[stat[0].replace(' :','')] = entry
        
        stat_dicts[test_names[t]] = stat_dict['Algorithm']

    return stat_dicts
        


def track_convergence(data, ref, test_dirs, metrics, eps=1e-2):
    """Track error convergence over partial renders."""

    num_order = lambda x: int(x.split('_')[-1].split('.')[0])
    round_10 = lambda x: int(round(x / 10.0)) * 10

    # All partial directories (one per algorithm)
    all_stats = []
    for partial_dir in test_dirs:
        partial_files = [f for f in os.listdir(partial_dir) if f.endswith('.exr')]
        partial_files = sorted(partial_files, key=num_order)

        # All partial images within a directory
        dir_stat = []
        for partial_f in partial_files:
            test_path = os.path.join(partial_dir, partial_f)
            test_fp = pyexr.open(test_path)
            test = np.array(test_fp.get())

            # Compute all metrics on (ref, test) pair
            metric_dict = {}
            for metric in metrics:
                err_img = compute_metric(ref, test, metric.lower(), eps)
                err_mean = '{:.6f}'.format(np.mean(err_img))
                metric_dict[metric] = err_mean
            dir_stat.append(metric_dict)

        all_stats.append(dir_stat)

    # Not sure if there's a better way to do this, maybe using itertools.chain?
    all_metrics = {}
    for metric in metrics:
        all_metrics[metric] = []
    for p, partial_dir in enumerate(test_dirs):
        for metric in metrics:
            seq = [float(stat[metric]) for stat in all_stats[p]]
            all_metrics[metric].append(seq)

    # Insert into dictionary (the ugliness of this is an artefact of using JSON...)
    for t, test_dir in enumerate(test_dirs):
        time_file = '{}_time.csv'.format('_'.join(test_dir.split('_')[:-1]))
        with open(os.path.join(test_dir, time_file)) as fp:
            timesteps = [item for sublist in list(csv.reader(fp)) for item in sublist]

        # Round to nearest ten, assuming frequency % 10 = 0
        timesteps = list(map(float, list(filter(None, timesteps))))
        timesteps = list(map(round_10, timesteps))

        for metric in metrics:
            for entry in data['stats'][0]['series']:
                if entry['label'] == metric.upper():
                    entry['track']['x'].append(timesteps)
                    entry['track']['y'].append(all_metrics[metric][t])


def update_stats(path_dir, data, ref, tests, metrics, clip, eps=1e-2):
    """Update some entries of data.js; assumes it was already created."""

    find_idx = lambda t, d: list(d['stats'][0]['labels']).index(t['name'])

    for test in tests:
        # Check if entry exists
        is_new = test['name'] not in data['stats'][0]['labels']

        # Update dictionary
        if is_new:
            data['imageBoxes'][0]['elements'].append(hdr_to_ldr(path_dir, test))
            data['stats'][0]['labels'].append(test['name'])
        else:
            t = find_idx(test, data)
            hdr_to_ldr(path_dir, test)

        # Compute desired metrics
        for m, metric in enumerate(metrics):
            # Recompute error
            err_img = compute_metric(ref, test['data'], metric.lower(), eps)
            err_mean = '{:.6f}'.format(np.mean(err_img))
            if is_new:
                data['stats'][0]['series'][m]['data'].append(err_mean)
            else:
                data['stats'][0]['series'][m]['data'][t] = err_mean

            # Recompute false color heatmap and save to files
            fc = falsecolor(err_img, clip, eps)
            fc_fname = '{}-{}.png'.format(test['name'], metric.upper())
            plt.imsave(os.path.join(path_dir, fc_fname), fc)

            if is_new:
                fc_entry = {'title': test['name'], 'version': '-', 'image': fc_fname}
                data['imageBoxes'][m+1]['elements'].append(fc_entry)

    # TODO: Update stats.json
    return data


def compute_stats(path_dir, ref, tests, metrics, clip, eps=1e-2):
    """Generate all false color LDR maps and dictionary for JS.
       Assumes tests = {'name': 'my_alg', 'data': ...}
    """

    data = {}
    data['imageBoxes'] = [{'title': 'Images', 'elements': []}]
    data['stats'] = [{'title': 'Stats', 'labels': [], 'series': []}]
    ref_entry = hdr_to_ldr(path_dir, {'name': 'Reference', 'data': ref})
    data['imageBoxes'][0]['elements'].append(ref_entry)

    # Generate images and compute stats
    # Couldn't find a way to do it all in only two loops
    stats = []
    for t, test in enumerate(tests):
        # Update dictionary
        data['imageBoxes'][0]['elements'].append(hdr_to_ldr(path_dir, test))
        data['stats'][0]['labels'].append(test['name'])

        # Compute all metrics
        stat_entry = {test['name']: {}}
        stats.append(stat_entry)
        for metric in metrics:
            # Compute error
            err_img = compute_metric(ref, test['data'], metric, eps)
            err_mean = '{:.6f}'.format(np.mean(err_img))

            # Compute false color heatmap and save to files
            fc = falsecolor(err_img, clip, eps)
            fc_fname = '{}-{}.png'.format(test['name'], metric.upper())
            plt.imsave(os.path.join(path_dir, fc_fname), fc)

            # Save stats, if necessary
            stats[t][test['name']][metric.upper()] = {'val': err_mean, 'fc': fc_fname}

    # Write dictionary
    for metric in metrics:
        fc_entry = {'title': metric.upper(), 'elements': []}
        metric_entry = {'label': metric.upper(), 'data': [], 'track': {'x': [], 'y': []}}

        for t, test in enumerate(tests):
            # Add false color filenames to dict
            fc_fname = stats[t][test['name']][metric.upper()]['fc']
            entry = {'title': test['name'], 'version': '-', 'image': fc_fname}
            fc_entry['elements'].append(entry)

            # Add metric value to dict
            err_mean = stats[t][test['name']][metric.upper()]['val']
            metric_entry['data'].append(err_mean)

        # Update dictionary with false colro filenames and metrics
        data['imageBoxes'].append(fc_entry)
        data['stats'][0]['series'].append(metric_entry)

    generate_thumbnail(path_dir, ref)
    return data


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Batch analysis of rendered images.')
   
    parser.add_argument('-r',   '--ref',      help='reference image filename', type=str, required=True)
    parser.add_argument('-t',   '--tests',    help='test images filename', nargs='+', type=str, required=True)
    parser.add_argument('-n',   '--names',    help='algorithms names', nargs='+', type=str)
    parser.add_argument('-m',   '--metrics',  help='difference metrics', nargs='+', choices=['l1', 'l2', 'mrse', 'mape', 'smape'], type=str, required=True)
    parser.add_argument('-p',   '--partials', help='partial renders to track convergence', nargs='+', type=str)
    parser.add_argument('-eps', '--epsilon',  help='epsilon value', type=float, default=1e-2)
    parser.add_argument('-c',   '--clip',     help='clipping values for min/max', nargs=2, type=float, default=[0,1])
    parser.add_argument('-d',   '--dir',      help='corresponding viewer scene directory', type=str, required=True)

    args = parser.parse_args()

    # Load images
    ref_fp = pyexr.open(args.ref)
    ref = np.array(ref_fp.get(), dtype=np.float64)
    tests, test_names = [], []
    for i, t in enumerate(args.tests):
        test_fp = pyexr.open(t)
        img = np.array(test_fp.get(), dtype=np.float64)
        if args.names:
            test_name = args.names[i]
        else:
            test_name = os.path.splitext(t)[0].replace('-',' ')
        test_name = test_name.encode('utf8').decode('unicode_escape') # For e.g. handling greek symbols
        test_names.append(test_name)
        tests.append({'name': test_name, 'data': img})
    
    # Compute stats
    sys.stdout.write('Computing stats... ')
    sys.stdout.flush()
    data = compute_stats(args.dir, ref, tests, args.metrics, args.clip, args.epsilon)
    if (args.partials):
        track_convergence(data, ref, args.partials, args.metrics, args.epsilon)
    write_data(args.dir, data)
    print('done.')

    # parse_stats(args.partials, test_names)
