from __future__ import print_function

"""
A script to analyze performance by comparing images 
using different metrics. To be used in conjuction 
with Jeri in-browser visualization tool.
"""

import os
import argparse
import pyexr
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json
from metric import compute_metric, falsecolor


def generate_thumbnail(ref):
    """Generate thumbnail image for index."""

    thumb = Image.fromarray((pyexr.tonemap(ref) * 255).astype(np.uint8))
    w, h = thumb.size
    thumb = thumb.resize((w//2, h//2), resample=Image.BICUBIC)
    thumb.save('thumb.png')


def write_data(data, stats):
    """Update JS dictionary files."""
    
    with open('stats.json', 'w') as fp:
        json.dump(stats, fp, indent=4)
    with open('data.json', 'w') as fp:
        json.dump(data, fp, indent=4)
    data_js = 'const data =\n' + json.dumps(data, indent=4)
    with open('data.js', 'w') as fp:
        fp.write(data_js)


def hdr_to_ldr(img):
    """HDR to LDR conversion for web display."""

    ldr = Image.fromarray((pyexr.tonemap(img['data']) * 255).astype(np.uint8))
    ldr_fname = '{}.png'.format(img['name'])
    ldr.save(ldr_fname)
    ldr_entry = {'title': img['name'], 'version': '-', 'image': ldr_fname}
    return ldr_entry


def update_stats(data, ref, tests, clip, eps=1e-2):
    """Update some entries of data.js.
       Assumes it was already created.
    """

    find_idx = lambda test, data: list(data['stats'][0]['labels']).index(test['name']) + 1
    metrics = [data['imageBoxes'][1:][i]['title'] for i in range(len(data['imageBoxes']) - 1)]

    for test in tests:
        # Update dictionary
        t = find_idx(test, data)
        data['imageBoxes'][0]['elements'][t] = hdr_to_ldr(test)
        data['stats'][0]['labels'][t] = test['name']

        # Compute desired metrics
        for metric in metrics:
            # Compute error
            err_img = compute_metric(ref, test['data'], metric.lower(), eps)
            err_mean = '{:.4f}'.format(np.mean(err_img))

            # Compute false color heatmap and save to files
            fc = falsecolor(err_img, clip, eps)
            fc_fname = '{}-{}.png'.format(test['name'], metric.upper());
            plt.imsave(fc_fname, fc)

    return data


def compute_all_stats(ref, tests, metrics, clip, eps=1e-2):
    """Generate all false color LDR maps and dictionary for JS.
       Assumes tests = {'name': 'my_alg', 'data': ...}
    """

    data = {}
    data['imageBoxes'] = [{'title': 'Images', 'elements': []}]
    data['stats'] = [{'title': 'Stats', 'labels': [], 'series': []}]
    ref_entry = hdr_to_ldr({'name': 'Reference', 'data': ref})
    data['imageBoxes'][0]['elements'].append(ref_entry)

    # Generate images and compute stats
    # Couldn't find a way to do it all in only two loops
    stats = []
    for t, test in enumerate(tests):
        # Update dictionary
        data['imageBoxes'][0]['elements'].append(hdr_to_ldr(test))
        data['stats'][0]['labels'].append(test['name'])

        # Compute all metrics
        stat_entry = {test['name']: {}}
        stats.append(stat_entry)
        for metric in metrics:
            # Compute error
            err_img = compute_metric(ref, test['data'], metric, eps)
            err_mean = '{:.4f}'.format(np.mean(err_img))

            # Compute false color heatmap and save to files
            fc = falsecolor(err_img, clip, eps)
            fc_fname = '{}-{}.png'.format(test['name'], metric.upper());
            plt.imsave(fc_fname, fc)

            # Save stats, if necessary
            stats[t][test['name']][metric.upper()] = {'val': err_mean, 'fc': fc_fname}

    # Write dictionary
    for metric in metrics:
        fc_entry = {'title': metric.upper(), 'elements': []}
        metric_entry = {'label': metric.upper(), 'data': [], 'track': []}

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

    generate_thumbnail(ref)
    return data, stats


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Batch analysis of rendered images.')
    parser.add_argument('-r',   '--ref', help='reference image filename', type=str, required=True)
    parser.add_argument('-t',   '--test', help='test images filename', nargs='+', type=str, required=True)
    parser.add_argument('-m',   '--metrics', help='difference metrics', nargs='+', choices=['l1', 'l2', 'mrse', 'mape', 'smape'], type=str)
    parser.add_argument('-eps', '--epsilon', help='epsilon value', type=float, default=1e-2)
    parser.add_argument('-c',   '--clip', help='clipping values for min/max', nargs=2, type=float, default=[0,1])
    parser.add_argument('-u',   '--update', help='update files', action='store_true')
    args = parser.parse_args()

    # Load images
    ref_fp = pyexr.open(args.ref)
    ref = np.array(ref_fp.get())
    tests = []
    for t in args.test:
        test_fp = pyexr.open(t)
        img = np.array(test_fp.get())
        test_name = os.path.splitext(t)[0]
        tests.append({'name': test_name, 'data': img})

    # Compute stats
    if args.update:
        with open('data.json', 'r') as fp:
            data = json.load(fp)
        with open('stats.json', 'r') as fp:
            stats = json.load(fp)
        data = update_stats(data, ref, tests, args.clip, args.epsilon)
    else:
        data, stats = compute_all_stats(ref, tests, args.metrics, args.clip, args.epsilon)

    write_data(data, stats)