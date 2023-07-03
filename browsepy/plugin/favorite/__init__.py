#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path
from pathlib import Path

from flask import Blueprint, render_template, redirect, url_for, current_app
from werkzeug.exceptions import NotFound

from browsepy import stream_template, get_cookie_browse_sorting, \
                     browse_sortkey_reverse
from browsepy.file import OutsideDirectoryBase


__basedir__ = os.path.dirname(os.path.abspath(__file__))

favorite = Blueprint(
    'favorite',
    __name__,
    url_prefix='/favorite',
    template_folder=os.path.join(__basedir__, 'templates'),
    static_folder=os.path.join(__basedir__, 'static'),
    )

def favfile():
  fname = os.path.join(current_app.config['DIRECTORY_BASE'], '.browsepy.favorites')
  return fname

def isfav(f):
  fname = favfile()
  if not os.path.exists(fname):
    return False
  with open(fname) as ff:
    while True:
      line = ff.readline()
      if line == str(f.urlpath) + '\n':
        return True
      if not line:
        return False

@favorite.route('/fav/<path:path>')
def fav(path):
    try:
        p = Path(path)
        with open(favfile(), 'a') as ff:
          ff.write(path + '\n')
        return redirect(url_for("browse", path=p.parent))
    except OutsideDirectoryBase:
        pass
    return NotFound()

@favorite.route('/unfav/<path:path>')
def unfav(path):
    try:
        p = Path(path)
        with open(favfile(), 'r') as ff:
          lines = ff.readlines()
        lines.remove(path + '\n')
        with open(favfile(), 'w') as ff:
          ff.writelines(lines)
        return redirect(url_for("browse", path=p.parent))
    except OutsideDirectoryBase:
        pass
    return NotFound()


def register_arguments(manager):
    '''
    Register arguments using given plugin manager.

    This method is called before `register_plugin`.

    :param manager: plugin manager
    :type manager: browsepy.manager.PluginManager
    '''



def register_plugin(manager):
    '''
    Register blueprints and actions using given plugin manager.

    :param manager: plugin manager
    :type manager: browsepy.manager.PluginManager
    '''
    manager.register_blueprint(favorite)

    # add style tag
    manager.register_widget(
        place='styles',
        type='stylesheet',
        endpoint='favorite.static',
        filename='css/browse.css'
    )

    # register action buttons
    manager.register_widget(
        place='entry-actions',
        css='fav',
        type='button',
        endpoint='favorite.fav',
        filter=(lambda x: x.is_file and not isfav(x))
    )
    manager.register_widget(
        place='entry-actions',
        css='unfav',
        type='button',
        endpoint='favorite.unfav',
        filter=isfav
    )
