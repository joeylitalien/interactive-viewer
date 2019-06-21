from __future__ import print_function

"""
A script to analyze performance by comparing images
using different metrics. To be used in conjuction
with Jeri in-browser visualization tool.
"""

import re
import os
import shutil
import argparse
from bs4 import BeautifulSoup as Soup


def add_to_index(root_dir, scene_name):
    """Add new scene to index."""

    index = os.path.join(root_dir, 'index.html')
    soup = Soup(open(index).read(), 'html.parser')
    scenes = soup.findAll('div', {"class": 'element-container'})[0]
    new_scene = soup.new_tag('div', **{'class': 'report-preview'})
    path_dir = os.path.join('scenes', scene_name.lower())
    scene_link = soup.new_tag('a', href=os.path.join(path_dir, 'index.html'))
    thumb = soup.new_tag('img', src=os.path.join(path_dir, 'thumb.png'), **{'class': 'report-thumb'})

    scene_link.append(thumb)
    new_scene.append(scene_link)
    new_scene.append(soup.new_tag('br'))
    new_scene.append(scene_name)
    scenes.append(new_scene)

    with open(index, 'w') as fp:
        fp.write(str(soup.prettify(indent_width=4)))


def list_index(root_dir):
    """List all the scenes in index."""

    index = os.path.join(root_dir, 'index.html')
    soup = Soup(open(index).read(), 'html.parser')
    print('All scenes: ')
    for s in soup.find_all('div', **{'class': 'report-preview'}):
        name = s.find('a').attrs['href'].split(os.path.sep)[1]
        print(' * {}'.format(name))


def remove_from_index(root_dir, scene_name):
    """Return true if targeted scene was deleted from index."""

    index = os.path.join(root_dir, 'index.html')
    soup = Soup(open(index).read(), 'html.parser')
    scenes = soup.findAll('div', {'class': 'element-container'})[0]
    
    # Find the html node
    scene_node = None
    for s in soup.find_all('div', **{'class': 'report-preview'}):
        name = s.find('a').attrs['href'].split(os.path.sep)[1]
        if name == scene_name:
            scene_node = s

    if scene_node == None:
        print('Unable to find scene {} in index'.format(scene_name))
        return False
    else:
        scenes.contents.remove(scene_node)
        index = os.path.join(root_dir, 'index.html')
        with open(index, 'w') as fp:
            fp.write(str(soup.prettify(indent_width=4)))
        return True


def create_dummy(root_dir, scene_name):
    """Create dummy index file for scene."""

    scene_dir = os.path.join(root_dir, 'scenes', scene_name.lower())
    if not os.path.exists(scene_dir):
        os.mkdir(scene_dir)

    example_index = os.path.join(root_dir, 'tools', 'example.html')
    soup = Soup(open(example_index).read(), 'html.parser')

    soup.title.string = scene_name
    title = soup.find('h1', **{'class': 'title'})
    title.string = scene_name

    with open(os.path.join(scene_dir, 'index.html'), 'w') as fp:
        fp.write(str(soup))


def remove_dummy(root_dir, scene_name):
    """Remove dummy scene from index."""

    scene_dir = os.path.join(root_dir, 'scenes', scene_name.lower())
    if not os.path.exists(scene_dir):
        print("Warning: scene directory {} does not exist".format(scene_dir))
    else:
        shutil.rmtree(scene_dir)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='HTML Scene Manager')
    parser.add_argument('-r', '--root', help='viewer root', type=str, default='../')
    subparsers = parser.add_subparsers(dest='action')
    # Create new scene
    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('-n', '--name', help='scene name', type=str)
    # List scenes
    parser_list = subparsers.add_parser('list')
    # Remove scene
    parser_remove = subparsers.add_parser('remove')
    parser_remove.add_argument('-n', '--name', help='scene name', type=str)

    args = parser.parse_args()

    # Soup prettify override
    orig_prettify = Soup.prettify
    r = re.compile(r'^(\s*)', re.MULTILINE)

    def prettify(self, encoding=None, formatter="minimal", indent_width=4):
        return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))
    Soup.prettify = prettify

     # Update directory index and create dummy file for new scene
    if args.action == 'add':
        add_to_index(args.root, args.name)
        create_dummy(args.root, args.name)

    # Update HTML index and remove dummy file
    elif args.action == 'remove':
        found = remove_from_index(args.root, args.name)
        if found: remove_dummy(args.root, args.name)
              
    elif args.action == 'list':
        list_index(args.root)

    else:
        raise Exception('Unknown action: {}'.format(args.action))