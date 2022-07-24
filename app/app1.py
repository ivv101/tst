# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python [conda env:p39] *
#     language: python
#     name: conda-env-p39-py
# ---

# same as test2, added Nikolay Oskolkov https://towardsdatascience.com/how-to-cluster-in-high-dimensions-4ef693bacc6

def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')


# +
import os

# runs only once, safe to execute when in different folder
try:
    notebook_dir # does a exist in the current namespace
except NameError:
    notebook_dir = os.getcwd()

if notebook_dir[-4:] != '/app':
    notebook_dir += '/app'

# if is_interactive():
#     notebook_dir = os.path.abspath(os.path.dirname('__main__'))
# else:    
#     notebook_dir = os.path.abspath(os.path.dirname('__file__'))
    
os.chdir(notebook_dir)    
    
print(notebook_dir)

# +
with open('bokeh_modules.py', 'wt') as _:
    _.write(r'''
from bokeh.embed import file_html, json_item, autoload_static, components
from bokeh.events import Tap
from bokeh.io import curdoc, output_notebook, export_png, export
from bokeh.layouts import layout, column, row, gridplot
from bokeh.models import ColumnDataSource, CustomJS, Slider, Legend, \
        Button, CheckboxButtonGroup, RadioButtonGroup, RadioGroup, CheckboxGroup, Label, Spacer, Title, Div, \
        PanTool, WheelZoomTool, SaveTool, ResetTool, HoverTool, TapTool, \
        BasicTicker, Scatter, CustomJSHover, FileInput, Toggle, TableColumn, DataTable, TextAreaInput, \
        Panel, Tabs, DateFormatter, LogColorMapper, LinearColorMapper, ColorBar, Select, PreText, \
        HTMLTemplateFormatter, NumberFormatter, ScientificFormatter, TextInput
from bokeh.plotting import figure, output_file, show, save
from bokeh.resources import CDN
from bokeh.themes import Theme
from bokeh.util.compiler import TypeScript
from bokeh.util.hex import hexbin
from bokeh.transform import linear_cmap, log_cmap
''')
import bokeh_modules as bk 
import importlib
importlib.reload(bk)
import bokeh.palettes as bkp

if is_interactive():
    bk.output_notebook()

# +
import os
# import os.path
import numpy as np
import pandas as pd

# import scipy.stats

import itertools  
# from collections import Counter

import pickle as pkl

import json
from glob import glob
import re

from astropy.io import fits
# from astropy.io.fits import getdata

from urllib.request import urlopen, urlretrieve

import logging

from PIL import Image

import sys

# import cupy as cp

# from cuml.cluster import DBSCAN
# from cuml.metrics.cluster import silhouette_score
# from cuml.metrics.cluster import silhouette_samples

import extended_library as ext_lib
import cxo_cluster_4_library as cxo_lib

import app1_library as app1_lib


# -

def get_table(data):

    '''
    data is dict
    '''

    props = ['color', 'silhouette', 'area', 'n-n_bkg', 'signif.', 'sigmas', 'x', 'y', 'ra', 'dec']

    tbl_data = {k: data[k] for k in props}

    tbl_data['n-n_bkg'] = [int(_) for _ in tbl_data['n-n_bkg']]

    color_template = '''             
        <p style="color:<%= 
            (function f(){                    
                    return(color)
                }()) %>;"> 
            <%= "&#9608;" %>
        </p>
        '''

    cols = []
    for _ in tbl_data.keys():

        if _ == 'color':
            frmt = bk.HTMLTemplateFormatter(template=color_template)
        elif _ == 'n-n_bkg':
            frmt = bk.NumberFormatter()       
        elif _ in ['area', 'signif.']:
            frmt = bk.ScientificFormatter(precision=2, power_limit_low=-2)   
        elif _ in ['ra', 'dec']:
            frmt = bk.NumberFormatter(format='0.0000')                  
        else:
            frmt = bk.NumberFormatter(format='0.00')    

        c = bk.TableColumn(field=_, title=_, formatter=frmt)    

        cols.append(c)  

    return tbl_data, cols   


# +
hug_dir = 'https://huggingface.co/datasets/oyk100/Chandra-ACIS-clusters-data/resolve/main'

hug_tree = json.load(urlopen(f'{hug_dir}/obsids.json'))

# +
upper_dir = '/'.join(notebook_dir.split('/')[:-1])

cache_dir = f'{upper_dir}/cache' # 'app_cache'

print(cache_dir)

os.system(f'mkdir -p {cache_dir}')

# fits_dir = '../data' #'/mnt/data_ssd/holes'

fits_dir = {
    'local': f'{upper_dir}/data', #'/mnt/data_ssd/holes'
    'hug': 'https://huggingface.co/datasets/oyk100/Chandra-ACIS-clusters-data/resolve/main'
}

# obsids = {
#     'local': np.sort([int(_) for _ in os.listdir(fits_dir['local']) if _[0]!='.']).astype(str).tolist(),
#     'hug': list(hug_tree.keys())
# }

n_max = 20_000   

# +
# bk.curdoc().clear()

# +
# from sklearn import datasets
# n_samples = 10_000
# noisy_moons_X, noisy_moons_y = datasets.make_moons(n_samples=n_samples, noise=0.)

# no_structure = np.random.rand(n_samples, 2)

# scaled_xy = ext_lib.scale(*noisy_moons_X.T)

# X = np.transpose([scaled_xy['x'], scaled_xy['y']])

# X = np.concatenate([X, no_structure])

# X_moon = (X - X.min(0)) / (X.max(0) - X.min(0))

# p = bk.figure()
# p.scatter(*X_moon.T)
# bk.show(p)

# +
# X, db = pkl.load(open('tmp.pkl', 'rb'))
                
# silhs = app1_lib.get_silhouette_samples(X, db)  
# silhs

# +
# glb = ''

# +
# class local_fits_class:
    
#     def __init__(self, fits_dir):   
        
#         self.fits_dir = fits_dir
        
#         obsids = subdirs_search(fits_dir)
        
#         self.obsids = {}
        
#         for obsid in obsids:
            
#             ccds = subdirs_search(f'{fits_dir}/{obsid}')
            
#             self.obsids[obsid] = {'ccds': ccds}
            
            
            
            
        
        
        
        
#     def get_obsids(self, loc):
    
#         if loc == 'local':
#             return np.sort([int(_) for _ in os.listdir(f'{self.fits_dir}') if _[0]!='.']).astype(str).tolist()
        
#         else:            
#             return list(hug_tree.keys())    
        
        
        
    
    
# -

log = logging.getLogger('bokeh')



# +
subdirs_search = lambda d: np.sort([int(_) for _ in next(os.walk(d))[1] if _[0]!='.']).astype(str).tolist()

def get_obsid_folders(loc):
    
    if loc == 'local':
        return subdirs_search(fits_dir['local'])
    else:            
        return list(hug_tree.keys())

    
def get_ccd_folders(obsid):
    
    if str(obsid) in get_obsid_folders('hug'):
        
        ccds = hug_tree[str(obsid)]
    
    else:
        
        json_fn = f'{cache_dir}/{obsid}_ccds.json'   
        
        if os.path.isfile(json_fn):            
            ccds = json.load(open(json_fn, 'rt'))
        else:   
            
            obsid_dir = f'{fits_dir["local"]}/{obsid}'
        
            fn = glob(f'{obsid_dir}/*fits*')[0]
            
            X = fits.getdata(fn, 1)
            
            ccds = np.sort(np.unique(X['ccd_id'])).tolist()
            
            json.dump(ccds, open(json_fn, 'wt'))
                
    return [str(_) for _ in ccds]
    
# def get_ccd_folders_old(obsid, loc):
    
#     if loc == 'local':
#         return subdirs_search(f"{fits_dir['local']}/{obsid}")
#     else:            
#         return [str(_) for _ in hug_tree[str(obsid)]]    


# +
# get_ccd_folders(333)
# -

if notebook_dir.split('/')[-1] != 'app':
    
    sys.exit(f'incorrect notebook_dir! {notebook_dir}')

# +
# head = fits.getheader('../data/333/acisf00333N003_evt2.fits.gz', 1)

# +
# [_[7:] for _ in set(head.keys()) if _[:7]=='BIASFIL']
# +
# fn = '../data/755/7/755_7_holes_evt2_05_8keV.fits'

# fn = '../data/333/acisf00333N003_evt2.fits.gz'

# fn = '../data/333/4/333_4_evt2_05_8keV.fits'

# fits.getheader(fn, 1)
# -




# +
# url = 'https://static.bokeh.org/branding/logos/bokeh-logo.svg'

# url = 'https://cxc.cfa.harvard.edu/cdaftp/byobsid/3/333/primary/acisf00333N003_full_img2.jpg'

# local_fn = url.split('/')[-1]

# urlretrieve(url, local_fn) 



# +
# importlib.reload(ext_lib)

# +
# obsid = 333

# # %time ext_lib.get_evt2_file(obsid, path=f"{fits_dir['local']}/{obsid}", search_mask='full_img2.jpg')

# +
# url = 'https://live.staticflickr.com/803/40807467832_eaf4690da0_b.jpg'

# p = bk.figure()
# z = p.image_url(url=[url], x=0, y=1, visible=True)
# p.x_range.start = p.y_range.start = 0
# p.x_range.end = p.y_range.end = 1    
# p.x_range.range_padding = p.y_range.range_padding = 0
# bk.show(p)

# +
# p = bk.figure(title='', tools=['hover'])
# # p.image?

# +
# # !wget https://live.staticflickr.com/803/40807467832_eaf4690da0_b.jpg

# +
# fn = '/home/ivv101/oyk/Extended_sources/2022/Chandra-ACIS-clusters-app/app/40807467832_eaf4690da0_b.jpg'
# -

def image_url_pars(fn):
    
    img =  Image.open(fn)
    
    # img = img.resize((100,400))
    
    w, h = img.getdata().size
    
    if w > h:
    
        h /= w
        w = 1    
        x, y = 0, (1 + h) / 2
        
    else:
        
        w /= h
        h = 1    
        x, y = (1 - w) / 2, 1
        
    return x, y, w, h

# +
# url = 'https://live.staticflickr.com/803/40807467832_eaf4690da0_b.jpg'

# fn = '40807467832_eaf4690da0_b.jpg'

# x, y, w, h = image_url_pars(fn)

# p = bk.figure(title='zzz')
# z = p.image_url(url=[url], x=0, y=1, w=1, h=1, visible=True)



# z.glyph.x = x
# z.glyph.y = y
# z.glyph.w = w
# z.glyph.h = h

# def xxx():
#     p.title.text = 'kkk'


# p.x_range.start = p.y_range.start = 0
# p.x_range.end = p.y_range.end = 1    
# p.x_range.range_padding = p.y_range.range_padding = 0

# xxx()


# bk.show(p)

# +
frz = app1_lib.friz_class(history=True, inactive=False)

DEBUG_WINDOW = False

len_pre_VISIBLE = False

def modify_doc(doc):    
    
    divTemplate = bk.Div(text="""
            <style>
            .bk.sent-later {
                font-size: 11px;
                font-color: green;
                border: 1px solid green;
                background-color: cyan;
            }
            </style>
    """)
    
    msg = bk.PreText(text=' ')
    
    debug_info_window = bk.PreText(text=f'check when deploying!!! {notebook_dir}\n', width=400, height=500, visible=DEBUG_WINDOW)    
    debug_info_window.css_classes.append('sent-later')
    
    holes_cb_group = bk.CheckboxButtonGroup(labels=['holes'], active=[0], width=70, margin=(0, -1, 0, 0))
    n_max_cb_group = bk.CheckboxButtonGroup(labels=['n_max'], active=[0], width=70, margin=(0, -1, 0, 0))
    cache_cb_group = bk.CheckboxButtonGroup(labels=['cache'], active=[0], width=70, margin=(0, -1, 0, 0))
    
    cb_group = bk.row([holes_cb_group, n_max_cb_group, cache_cb_group])
        
    data_loc_rbg = bk.RadioButtonGroup(labels=['hug', 'local'], active=1, width=200)    
    data_loc_active = lambda :  data_loc_rbg.labels[data_loc_rbg.active]
            
    query_input = bk.TextInput(value='', placeholder='obsid', width=100)
    query_button = bk.Button(label='query', button_type='success', width=100)
        
    len_pre = bk.PreText(text='', visible=len_pre_VISIBLE)
    
    eps_slider = bk.Slider(start=2, end=4, value=2.86, step=.1, title='eps', width=400)
    
    slider_min_samples = bk.Slider(start=30, end=60, value=46, step=2, title='min_samples', width=400)
    
    tbl_source = bk.ColumnDataSource()
    tbl = bk.DataTable(source=tbl_source, visible=False) 
    
    sigma_slider = bk.Slider(start=0, end=3, value=1, step=0.01, title='sigma', width=100)
    nbins_slider = bk.Slider(start=1, end=200, value=100, step=1, title='nbins', width=100)
    
    pallettes_dict = {'Viridis256': bkp.Viridis256, 'Spectral11': bkp.Spectral11}    
    pals = list(pallettes_dict.keys())    
    select_pallette = bk.Select(title='pallette', 
                           value=pals[0], 
                           options=pals,
                           width=200)
    
    p = bk.figure(title='', tools=['hover'])
    img = p.image(image=[], x=0, y=0, dw=1, dh=1, 
                  palette=pallettes_dict[select_pallette.value], level='image')
    
    obsids = get_obsid_folders('local')
    
    obsid_ini = '755' if '755' in obsids else obsids[0]
    
    ccds = get_ccd_folders(obsid_ini)
    
    ccd_ini = '7' if obsid_ini=='755' else ccds[0]
    
    p.title = f'{obsid_ini}/{ccd_ini}'
        
    jpg_img = p.image_url(url=[], x=0, y=1, w=1, h=1, visible=True, global_alpha=1)
    
    clus_source = bk.ColumnDataSource({'xs': [], 'ys': [], 'color': []})
    clus_source_filtered = bk.ColumnDataSource({'xs': [], 'ys': [], 'color': []})
    text_source = bk.ColumnDataSource(dict(x=[], y=[], text=[]))
    
    apply_button = bk.Button(label='Apply', button_type='success', width=100)  
    
    min_sigma_slider = bk.Slider(start=0, end=10, value=5, step=1, title='min sigma', width=100)
    
    select_obsid = bk.Select(title='obsid', 
                         value=obsid_ini, 
                         options=obsids,
                         width=100)    

    select_ccd = bk.Select(title='ccd',                            
                           value=ccd_ini,
                           options=[''] + ccds,
                           width=50)

    
    def show_jpg_img(obsid, path=fits_dir['local']):
    
        status, url, fn_jpg = ext_lib.get_evt2_file(obsid, 
                                                    path=f'{path}/{obsid}',
                                                    search_mask='full_img2.jpg')       
        jpg_img.data_source.data['url'] = [url]
        
        x, y, w, h = image_url_pars(fn_jpg)
        
        jpg_img.glyph.x = x
        jpg_img.glyph.y = y
        jpg_img.glyph.w = w
        jpg_img.glyph.h = h
        
        jpg_img.visible = True
        img.visible = False
        
        apply_button.disabled = True
    
    def all_done_func():
        if msg.text == 'working ...':
            msg.text = ' '
                
    def clear_clusters(): 
        
        empty = {'xs': [], 'ys': [], 'color': []}            
        clus_source.data = empty            
        clus_source_filtered.data = empty  
        text_source.data = dict(x=[], y=[], text=[])
        tbl.visible = False 
        img.data_source.data['image'] = []
    
    def select_obsid_callback_aux():
        
        global frz                                
        if frz.unfreeze('select_obsid'): return
    
        clear_clusters()
            
        obsid = select_obsid.value
                
        frz.freeze('select_ccd')
        select_ccd.value = ''
        frz.unfreeze('select_ccd')
        
        obsid_dir = f"{fits_dir['local']}/{obsid}"
        
        os.system(f'mkdir -p {obsid_dir}')
        
        if obsid in get_obsid_folders('hug'):
                                    
            holes_cb_group.disabled = False            
            holes_cb_group.active = [0]
                        
        else:
            
            holes_cb_group.disabled = True
            holes_cb_group.active = []
                                                            
            status, url, evt2_filename = ext_lib.get_evt2_file(obsid, path=obsid_dir) 
            
            if status != 'ok': 
                
                # os.system(f'rm -rf {obsid_dir}')                
                debug_info_window.text += f'get_evt2_file error: {status}\n'                
                return
                    
        ccds = get_ccd_folders(obsid)
        
        select_ccd.options = [''] + ccds
                    
        show_jpg_img(obsid)  
                
        p.title.text = f'{obsid}'
        
    def select_obsid_callback(attr, old, new):
        msg.text = 'working ...'
        doc.add_next_tick_callback(select_obsid_callback_aux)
        doc.add_next_tick_callback(all_done_func)
    
                
    def get_ccd_evt2(obsid, ccd):   
        
        holes = True if holes_cb_group.active else False        
        hls = '_holes' if holes else ''
        
        evt2_fn = f'{obsid}_{ccd}{hls}_evt2_05_8keV.fits'          
        evt2_fn_full = f"{fits_dir['local']}/{obsid}/{ccd}/{evt2_fn}"
        
        if os.path.isfile(evt2_fn_full): 
            pass
        
        elif obsid in get_obsid_folders('hug'):
                                        
            os.system(f"mkdir -p {fits_dir['local']}/{obsid}/{ccd}")
                
            url = f"{fits_dir['hug']}/{obsid}/{ccd}/{evt2_fn}"  
                
            urlretrieve(url, evt2_fn_full) 
                    
        else:
            
            os.system(f"mkdir -p {fits_dir['local']}/{obsid}/{ccd}")
            
            app1_lib.create_fits(obsid, int(ccd), fits_dir['local'], hls, cache=bool(cache_cb_group.active))
            
        # return evt2_fn, evt2_fn_full    
                        
    def show_ccd(obsid, ccd):
        
        holes = True if holes_cb_group.active else False        
        hls = '_holes' if holes else ''
                
        evt2_fn = f'{obsid}_{ccd}{hls}_evt2_05_8keV.fits'    
        evt2_fn_full = f"{fits_dir['local']}/{obsid}/{ccd}/{evt2_fn}"
        
        scaled_xy = app1_lib.get_data(evt2_fn_full, ccd)
        
        X = scaled_xy['X'].copy()
        
        H, bkg_dens = app1_lib.nbins_sigma_func(X, nbins_slider.value, sigma_slider.value)
        
        img.data_source.data['image'] = [H.T]
        
        jpg_img.visible = False
        img.visible = True
        
        apply_button.disabled = False
        
        frz.comment += 'show_ccd_passed\n'
        
    show_ccd(obsid_ini, ccd_ini)
                   
    def select_ccd_callback_aux():
                
        global frz        
        if frz.unfreeze('select_ccd'): return
    
        clear_clusters()
    
        obsid = select_obsid.value
        ccd = select_ccd.value
        
        if ccd == '':    
            show_jpg_img(obsid)
            p.title.text = obsid            
            return
        
        p.title.text = f'{obsid}/{ccd}'
        
        get_ccd_evt2(obsid, ccd)
        
        show_ccd(obsid, ccd)
        
    def select_ccd_callback(attr, old, new):
        msg.text = 'working ...'
        doc.add_next_tick_callback(select_ccd_callback_aux)
        doc.add_next_tick_callback(all_done_func)
   
    def data_loc_rbg_callback(attr, old, new):
                
        global frz              
        if frz.unfreeze('data_loc_rbg'): return
            
        obsids = get_obsid_folders(data_loc_active())
                               
        select_obsid.options = obsids   
        select_obsid.value = obsids[0]
        
    def query_button_callback_aux():
                
        global frz        
        if frz.unfreeze('query_button'): return
       
        frz.freeze('data_loc_rbg')
        data_loc_rbg.active = 1
        frz.unfreeze('data_loc_rbg')
                    
        tbl.visible = False
        
        obsid = query_input.value.rstrip()
                        
        local_obsids = get_obsid_folders('local')
                        
        if obsid not in local_obsids:
            local_obsids = np.sort(local_obsids + [obsid]).tolist()  
                    
        select_obsid.options = local_obsids   
        
        frz.freeze('select_obsid')
        select_obsid.value = obsid
        frz.unfreeze('select_obsid')
        
        select_obsid_callback_aux()
        
    def query_button_callback():
        msg.text = 'downloading obsid ...'
        doc.add_next_tick_callback(query_button_callback_aux)
        doc.add_next_tick_callback(all_done_func)    
                
    def holes_cb_group_callback_aux():  
        
        global frz        
        if frz.unfreeze('holes_cb_group'): return
        
        select_ccd_callback_aux()
        
    def holes_cb_group_callback(attr, old, new):
        msg.text = 'working ...'
        doc.add_next_tick_callback(holes_cb_group_callback_aux)
        doc.add_next_tick_callback(all_done_func)    
        
        
        
        
        
        
        
    TOOLTIPS = [
        ('index', '$index'),
        ('(x,y)', '@center_of_mass'),
        ('silhouette', '@silhouette')
    ]
    
    query_button.on_click(query_button_callback)
    select_obsid.on_change('value', select_obsid_callback)  
    select_ccd.on_change('value', select_ccd_callback)  
    data_loc_rbg.on_change('active', data_loc_rbg_callback)
    holes_cb_group.on_change('active', holes_cb_group_callback)
            
    p.toolbar.autohide = True
    
    hov = p.select_one(bk.HoverTool)
    
    # hov.tooltips = TOOLTIPS
        
    p.x_range.start = p.y_range.start = 0
    p.x_range.end = p.y_range.end = 1    
    p.x_range.range_padding = p.y_range.range_padding = 0
    
    opacity_slider = bk.Slider(start=0, end=1, value=0.5, step=.01, title='opacity', width=100)
        
    clus = p.multi_polygons(xs='xs', ys='ys', color='color', source=clus_source_filtered, fill_alpha=opacity_slider.value)   
    
    hov.renderers = [clus]

    txts = p.text(x='x', y='y', text='text', angle=0, text_color='white', source=text_source)
            
    opacity_slider.js_link('value', clus.glyph, 'fill_alpha')
    
    alpha_slider = bk.Slider(start=0, end=10, value=1, step=.01, title='alpha', width=100)    
        
    def alpha_slider_callback(attr, old, new):
        
        data = clus_source.data.copy()  
        
        hull_dict = app1_lib.get_hull(data['clusters'], new)
        
        data.update(hull_dict)        
        
        data = pd.DataFrame(data)
            
        clus_source.data = data.copy()
                        
        clus_source_filtered.data = data[data['sigmas'] >= min_sigma_slider.value]
            
    alpha_slider.on_change('value_throttled', alpha_slider_callback)
        
    p.grid.visible = False
    
    # p.toolbar_location = None
    p.axis.visible = False
    
    p.border_fill_color = 'white' #border_fill_color
    p.title.background_fill_color = 'white'
        
    def select_pallette_callback(attr, old, new):
        
        img.glyph.color_mapper.palette = pallettes_dict[new]
                     
    select_pallette.on_change('value', select_pallette_callback)
    
    X_source = bk.ColumnDataSource({'X': [], 'db': []})
                        
    def nbins_sigma_slider_callback(attr, old, new):
        
        # k = scipy.stats.gaussian_kde([x,y], sigma)
        # xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
        # zi = k(np.vstack([xi.flatten(), yi.flatten()]))    
        # d = zi.reshape(xi.shape).T
        
        H, bkg_dens = app1_lib.nbins_sigma_func(X_source.data['X'], nbins_slider.value, sigma_slider.value)
              
        img.data_source.data['image'] = [H.T]
                
    sigma_slider.on_change('value', nbins_sigma_slider_callback)                       
    nbins_slider.on_change('value', nbins_sigma_slider_callback)   
    
    
    
    def min_sigma_slider_callback(attr, old, new):
        
        data = pd.DataFrame(clus_source.data)
        
        new_data = data[data['sigmas'] >= new]
        
        clus_source_filtered.data = new_data
        
        text_source.data = {
            'x': new_data['x_scaled'],
            'y': new_data['y_scaled'],
            'text': np.arange(len(new_data['clusters'])).tolist()            
        }
        
        tbl_source.data, tbl.columns = get_table(new_data) 
                
    min_sigma_slider.on_change('value', min_sigma_slider_callback)     
    
    pal_reverse_checkbox = bk.CheckboxGroup(labels=['reverse'], active=[])
    
    def pal_reverse_checkbox_callback(attr, old, new):
        
        _ = pallettes_dict[select_pallette.value]
                
        img.glyph.color_mapper.palette = _[::-1] if len(new)==1 else _
            
    pal_reverse_checkbox.on_change('active', pal_reverse_checkbox_callback)
            
    
    
#     d = Div(text="start")

#     b = Button()

#     def work():
#         sleep(2)
#         d.text = "end"

    def cb():
        msg.text = 'working ...'
        doc.add_next_tick_callback(apply_button_callback)
        doc.add_next_tick_callback(all_done_func)
           
    def apply_button_callback():
        
        global frz        
        if frz.unfreeze('apply_button'): return
                        
        obsid = select_obsid.value
        ccd = select_ccd.value
        
        if ccd == '':
            return
        
        # debug_info_window.text += f'{obsid}/{ccd}\n'
                
        # msg.text = f'{cb_group.active}'
                       
        holes = True if holes_cb_group.active else False        
        n_lim = True if n_max_cb_group.active else False
        
        args_func = {
            'eps': eps_slider.value, 
            'min_samples': slider_min_samples.value
        }
                        
        res = app1_lib.process_ccd(obsid, ccd, 
                                   holes=holes, 
                                   n_lim=n_lim, n_max=n_max, 
                                   args_func=args_func, 
                                   nbins=nbins_slider.value, 
                                   sigma=sigma_slider.value,
                                   alpha=alpha_slider.value,
                                   local_fits_dir=fits_dir['local'])    
                
        if res=='empty':
            img.data_source.data['image'] = []  
            
            clear_clusters()
                   
            msg.text = f'{obsid}_{ccd} empty'
            
            debug_info_window.text += f'emptyyyy\n'
            
            return 'empty'
        
        new_data = res
        
        X = new_data['X']
        len_X_orig = new_data['len_X_orig']
        db = new_data['db']
        n_clusters = new_data['n_clusters']
        bkg_dens = new_data['bkg_dens']
        clusters = new_data['clusters']
        H = new_data['H']
        
        debug_info_window.text += f'{n_clusters}\n'
        
        img.data_source.data['image'] = [H.T]
                                            
        len_pre.text = f'{len(X)} events' if len_X_orig==len(X) else f'{len(X)}/{len_X_orig} events'     
                    
        X_source.data = {'X': X, 'db': db}  
        
        hls = '_holes' if holes_cb_group.active else '' 
        
        pkl.dump(X, open(f'{cache_dir}/X_{obsid}_{ccd}{hls}.pkl', 'wb'))
                                   
        n_clusters_text = f'\n{n_clusters} clusters'
        if n_clusters==1:
            n_clusters_text = n_clusters_text[:-1]
        
        len_pre.text += n_clusters_text
                       
        palette = itertools.cycle(bkp.Category20[20]) 
        
        # start = 0
        # palette = itertools.islice(palette, start, None)

        colors = np.array(['']*n_clusters, dtype='U7')
            
        for i in range(n_clusters): 
        
            colors[i] = next(palette)
            
        colors[0] = cxo_lib.rgb2hex(0, 255, 255) # turquoise   
        
        msg.text = f'len_X: {len(X)}, bkg: {bkg_dens}'
                                    
        new_data.update({'clusters': clusters, 'color': colors.tolist()})
        
        excl = ['X', 'len_X_orig', 'db', 'n_clusters', 'bkg_dens', 'H']
        
        h = [_ for _ in new_data.keys() if _ not in excl]                
        new_data = pd.DataFrame(new_data, columns=h).fillna('')
                                
        clus_source.data = new_data.copy()
        
        new_data = new_data[new_data['sigmas'] >= min_sigma_slider.value]
        
        clus_source_filtered.data = new_data
        
        text_source.data = {
            'x': new_data['x_scaled'],
            'y': new_data['y_scaled'],
            'text': np.arange(len(new_data['clusters'])).tolist()            
        }
                        
        tbl_source.data, tbl.columns = get_table(new_data) 
                        
        # msg.text = f'{obsid}_{ccd} done'
        
        tbl.visible = True
        
        return 'success'
                        
    apply_button.on_click(cb)
    # apply_button.on_click(log_callback)
        
    process_all_button = bk.Button(label='Process all', button_type='primary', width=100) 
    
    def process_all_button_callback():
        
        # global glb
        
        bad_obsids_ccd = []
        
        all_dir = f'{cache_dir}/all'
        
        loop_progress = cxo_lib.loop_class(obsids)
        
        for obsid in obsids:
            
            loc = data_loc_active()
            
            ccds = get_ccd_folders(obsid)
            
            # ccds = get_folders(obsid)
            
            # process_all_button.label = f'{i}/{len(obsids)}''
            
            for ccd in ccds:
                
                select_obsid.value = obsid
                select_ccd.value = ccd
                
                try:
                    res = apply_button_callback()
                except:
                    bad_obsids_ccd.append([obsid, ccd, 'error'])
                    continue
                
                if res == 'empty':
                #     # print(f'{obsid}_{ccd} empty')
                    bad_obsids_ccd.append([obsid, ccd, 'empty'])
                    continue
                
                hls = '_holes' if holes_cb_group.active else ''
                                                
                os.system(f'cd {notebook_dir}; mkdir -p {all_dir}')
                
                tbl_json = json.loads(pd.DataFrame(tbl_source.data).to_json(orient='split', index=False, indent=4))
                json.dump(tbl_json, open(f'{all_dir}/{obsid}_{ccd}{hls}.json', 'wt'))
                
                # glb = tbl_json
                  
                _ = clus_source_filtered.data.copy()    
                pkl.dump(_, open(f'{all_dir}/{obsid}_{ccd}{hls}.pkl', 'wb'))
                
                bk.export_png(p, filename=f'{all_dir}/{obsid}_{ccd}{hls}.png')  
                
                # print(f'{obsid}_{ccd} done')
                
            loop_progress()
            
        pkl.dump(bad_obsids_ccd, open(f'{cache_dir}/bad_obsids_ccd.pkl', 'wb'))    
        
    process_all_button.on_click(process_all_button_callback)    
        
    row1 = bk.row([select_obsid, select_ccd, len_pre], width=800)
    
    settings_column = bk.column([msg, bk.row(apply_button), #process_all_button), 
                                 bk.row(data_loc_rbg, bk.Spacer(width=100), bk.row(query_input, query_button)), 
                                 row1, cb_group, eps_slider, slider_min_samples, tbl, divTemplate, debug_info_window])
    
    layout = bk.row([bk.column([p, bk.row(select_pallette, pal_reverse_checkbox, min_sigma_slider), 
                                bk.row(opacity_slider, alpha_slider), bk.row(nbins_slider, sigma_slider)]), settings_column])
    
    doc.add_root(layout)
    
    doc.title = 'Sliders'
    
    # cb()
    
    #qqq
    
    
    # bk.export_png(p, filename=f'{save_dir}/{obsid_ccd}{hls}_blur.png')
# -
if is_interactive():
    bk.show(modify_doc, notebook_url='localhost:1111', port=8910) # change
else:
    modify_doc(bk.curdoc())

print(frz.history)

print(frz.comment)



# +
# obsid = '333'
# ccd = '4'
# hls = ''

# obsid_dir = f'{fits_dir["local"]}/{obsid}'
# fn_ccd = f'{obsid_dir}/{ccd}/{obsid}_{ccd}{hls}_evt2_05_8keV.fits'


# +
# fits.info(fn_ccd)

# +
# data, head = fits.getdata(fn_ccd, 1), fits.getheader(fn_ccd, 1)

# +
# fits.getheader('zzz.fits', 1)

# +
# evt2_data, head = ext_lib.process_fits(fn)
# evt2_data

# +
#||||||||||||||||||||\ \
#<style>
#             .bk.sent-later {
#                 font-size: 40px;
#                 border: 1px solid green;
#                 background-color: white;
#             }
#             </style>
#     """)



# a = bk.PreText(text='zzz\nfff\n\nggg', width=400, height=500)

# a.css_classes.append('sent-later')

# bk.show(bk.layout([divTemplate, a]))

# +
# # log.log?
# -



# +
# a = app1_lib.friz_class()

# a.freeze('zzz')

# def tst():
    
#     global a
    
#     if a.unfreeze('zzz'): return 
    
#     print('ttt')

# tst()    
# +
# i = 0

# ttt = []

# def modify_doc(doc):
    
    
    
#     freeze_select_ccd = False
    
#     p = bk.figure()
    
    
    
#     url755 = 'https://cxc.cfa.harvard.edu/cdaftp/byobsid/5/755/primary/acisf00755N004_full_img2.jpg'
    
#     url333 = 'https://cxc.cfa.harvard.edu/cdaftp/byobsid/3/333/primary/acisf00333N003_full_img2.jpg'
    
#     z = p.image_url(url=[url755], x=0, y=1, w=1, h=1, visible=True, global_alpha=0.5)
    
#     # div_image = bk.Div(text=f"""<img src="{url}" alt="div_image">""", width=450, height=450)
    
#     ttt.append(z)
    
#     z.data_source.data['url'][0] = url755
    

#     select_ccd = bk.Select(title='ccd',                            
#                                value='1',
#                                options=['1','2','3','4','5'],
#                                width=50)

#     but = bk.Button(label='clik')

#     def but_callback():
        
#         nonlocal freeze_select_ccd
        
#         # ccds = get_ccd_folders(new, data_loc_active())
        
#         freeze_select_ccd = False

#         select_ccd.options = ['7','8','9']  
#         select_ccd.value = '7' 

#         print(select_ccd.options, select_ccd.value)

        
#     def select_ccd_callback(attr, old, new):
        
#         nonlocal freeze_select_ccd
        
# #         global i 
        
# #         i += 1
                
#         if freeze_select_ccd:
#             freeze_select_ccd = False
#             return

#         # ccds = get_ccd_folders(new, data_loc_active())
        
#         # select_ccd.value = str(i)

#         print('zzz')

#     but.on_click(but_callback) 
#     select_ccd.on_change('value', select_ccd_callback) 
    
#     layout = bk.layout(select_ccd, but, p)
    
#     doc.add_root(layout)

# bk.show(modify_doc, notebook_url='localhost:1111', port=8911) # change
# +
# x = "global"

# def foo():
#     x = x * 2
#     print(x)

# foo()
# -



# +
# from urllib.request import urlretrieve

# obsid = 1042
# ccd = 3

# loc = 'hug'

# holes = True



# local_fits_dir = fits_dir['local']

# hls = '_holes' if holes else ''
        
# evt2_fn = f'{obsid}_{ccd}{hls}_evt2_05_8keV.fits'

# evt2_fn_local = f'{local_fits_dir}/{obsid}/{ccd}/{evt2_fn}'

# if os.path.isfile(evt2_fn_local) or loc=='local':
#     pass
# elif loc=='hug':        
#     url = f'{fits_dir[loc]}/{obsid}/{ccd}/{evt2_fn}'
    
#     os.system(f'mkdir -p {local_fits_dir}/{obsid}/{ccd}')
    
#     urlretrieve(url, evt2_fn_local)        
# elif loc=='query':        
#     status, url, evt2_fn_local = ext_lib.get_evt2_file(obsid, f'{local_fits_dir}/{obsid}')        
#     if status != 'ok':
#         sys.exit(status)  
        
        
# scaled_xy = app1_lib.get_data(evt2_fn_local, ccd)    

# +
# https://huggingface.co/datasets/oyk100/Chandra-ACIS-clusters-data/resolve/main/755/2/755_2_evt2_05_8keV.fits


# +
# # create json with data files structure

# data_dir = '/home/ivv101/oyk/Extended_sources/2022/Chandra-ACIS-clusters-data'

# lst = glob(f'{data_dir}/**/*fits', recursive=True)

# dir_tree = {}

# for f in lst:
    
#     obsid, ccd = np.array(f.split('/')[-3:-1], dtype=int).tolist()
    
#     if obsid not in dir_tree.keys():        
#         dir_tree[obsid] = []
    
#     if ccd not in dir_tree[obsid]:
#         dir_tree[obsid].append(ccd)
#         dir_tree[obsid] = sorted(dir_tree[obsid])
        
# dir_tree = dict(sorted(dir_tree.items()))   

# json.dump(dir_tree, open(f'{data_dir}/obsids.json', 'wt'))

# # dir_tree
# -



# +











# a = np.array([
#     [ 0,  2, 1],
#     [ 0,  0, 3],
#     [ 0,  0, 2],
#     [-1,  8, 0],
#     [-6,  7, 0],
#     [-1,  1, 0]
# ])

# a[np.lexsort(a[:,::-1].T)] # sorts by first, second etc
# +

        
#     def select_ccd_callback_aux():
                
#         global frz        
#         if frz.unfreeze('select_ccd'): return
    
#         obsid = select_obsid.value
#         ccd = select_ccd.value
        
#         if ccd == '':    
#             show_jpg_img(obsid)
#             p.title.text = obsid            
#             return
        
#         p.title.text = f'{obsid}/{ccd}'
        
#         get_ccd_evt2(obsid, ccd)
        
#         show_ccd(obsid, ccd)
    
        
#     show_ccd(obsid_ini, ccd_ini) 
    
    
#     def query_button_callback():
        
#         global frz        
#         if frz.unfreeze('query_button'): return
    
#         frz.freeze('data_loc_rbg')
#         data_loc_rbg.active = 1
        
#         tbl.visible = False
        
#         obsid = query_input.value.rstrip()
#         obsid_dir = f"{fits_dir['local']}/{obsid}"
                
#         if obsid in get_obsid_folders('hug'):
            
#             ccds = get_ccd_folders(obsid, 'hug')
#             ccd = [0]
            
#             ccd_dir = f'{obsid_dir}/{ccd}'
            
#             holes = True if holes_cb_group.active else False        
#             hls = '_holes' if holes else ''
        
#             fn_ccd = f'{obsid}_{ccd}{hls}_evt2_05_8keV.fits'
            
#             fn_ccd_full = f'{ccd_dir}/{fn_ccd}'
            
#             if not os.path.isfile(fn_ccd_full):
                
#                 os.system(f'mkdir -p {ccd_dir}')
                
#                 url = f"{fits_dir['hug']}/{obsid}/{ccd}/{fn_ccd}"  
                
#                 urlretrieve(url, fn_ccd_full)  
                                
#         else:
#             if not os.path.isdir(obsid_dir):

#                 debug_info_window.text += f'create obsid {obsid} folder\n'

#                 status, url, evt2_filename = ext_lib.get_evt2_url(obsid) 

#                 debug_info_window.text += status + '\n'        

#                 if status != 'ok':
#                     msg.text = status            
#                     return

#                 evt2_filename_full = f'{obsid_dir}/{evt2_filename}'

#                 os.system(f'mkdir -p {obsid_dir}')
#                 urlretrieve(url, evt2_filename_full)  

#                 with fits.open(evt2_filename_full) as hdul:
#                     _ = hdul[1].data
#                     ccds = np.sort(np.unique(_['ccd_id'])).tolist()

#                 [os.system(f'mkdir -p {obsid_dir}/{ccd}') for ccd in ccds]

#             ccds = get_ccd_folders(obsid, 'local') 

#             ccd = ccds[0]      

#             app1_lib.create_fits(obsid, ccd, fits_dir['local'], hls, use_cache)
                
#         local_obsids = get_obsid_folders('local')
        
#         select_obsid.options = local_obsids
#         frz.freeze('select_obsid')
#         select_obsid.value = obsid
        
#         select_ccd.options = ccds
#         frz.freeze('select_ccd')
#         select_ccd.value = ccd
        
        
        
#         show_ccd(obsid, ccd)
        
                            
        
        
    
        
        
        
        
        
        
   
            
#     def data_loc_rbg_callback(attr, old, new):
        
        
        
#         global frz              
#         if frz.unfreeze('data_loc_rbg'): return
    
        

# #         obsid = obsids[data_loc_active()][0]
        
# #         print(obsid)







#         # frz.comment += f'{data_loc_active()}\n'
        
#         cur_obsids = get_obsid_folders(new)
        
#         # frz.comment += f'{cur_obsids}\n'
        
#         # debug_info_window.text += 'loc: ' + data_loc_active() + '\n' 
#         # debug_info_window.text += cur_obsids + '\n'     
                       
#         select_obsid.options = cur_obsids   
#         select_obsid.value = cur_obsids[0]
        
#         # frz.comment += f'data_loc_rbg_callback done\n'
        
        
        
        
        
        
#         # select_obsid_callback(0, 0, select_obsid.value)
                
#         # cb()
        
        
