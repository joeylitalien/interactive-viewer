from __future__ import print_function

"""
A script to analyze performance by comparing images 
using different metrics. To be used in conjuction 
with Jeri in-browser visualization tool.
"""

import re
import os
import argparse
from bs4 import BeautifulSoup as Soup


def add_to_index(root_dir, scene_name):
    """Add new scene to index."""

    index = os.path.join(root_dir, 'index.html')
    soup = Soup(open(index).read(), 'html.parser')
    scenes = soup.findAll('div', {"class": 'element-container'})[0]
    new_scene = soup.new_tag('div', **{'class':'report-preview'})
    path_dir = os.path.join('scenes', scene_name.lower())
    scene_link = soup.new_tag('a', href=os.path.join(path_dir, 'index.html'))
    thumb = soup.new_tag('img', src=os.path.join(path_dir, 'thumb.png'), **{'class':'report-thumb'})
    
    scene_link.append(thumb)
    new_scene.append(scene_link)
    new_scene.append(soup.new_tag('br'))
    new_scene.append(scene_name)
    scenes.append(new_scene)

    with open(index, 'w') as fp:
        fp.write(str(soup.prettify(indent_width=4)))


def create_dummy(root_dir, scene_name):
    """Create dummy index file for scene."""
    
    scene_dir = os.path.join(root_dir, 'scenes', scene_name.lower())
    if not os.path.exists(scene_dir):
        os.mkdir(scene_dir)

    example_index = os.path.join(root_dir, 'tools', 'example.html')
    soup = Soup(open(example_index).read(), 'html.parser')

    soup.title.string = scene_name
    title = soup.find('h1', **{'class':'title'})
    title.string = scene_name

    with open(os.path.join(scene_dir, 'index.html'), 'w') as fp:
        fp.write(str(soup))


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='New scene creator.')
    parser.add_argument('-r', '--root', help='viewer root', type=str, default='../')
    parser.add_argument('-n', '--name', help='scene name', type=str)
    args = parser.parse_args()

    # Soup prettify override
    orig_prettify = Soup.prettify
    r = re.compile(r'^(\s*)', re.MULTILINE)
    def prettify(self, encoding=None, formatter="minimal", indent_width=4):
        return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))
    Soup.prettify = prettify

    # Update directory index
    add_to_index(args.root, args.name)

    # Create dummy file for new scene
    create_dummy(args.root, args.name)

