import csv
from PIL import Image, ImageDraw

def one_col(pos):
    im = Image.new('1', (8,8), 0)
    draw = ImageDraw.Draw(im)
    draw.rectangle((pos*2, 0, pos*2, 7), 1, 1)
    return im

def octants(positions):
    im = Image.new('1', (8,8), 0)
    for pos in positions:
        draw = ImageDraw.Draw(im)
        draw.rectangle((pos[0]*2, pos[1]*2,
            pos[0]*2+1, pos[1]*2+1), 1, 1)
    return im

def one_octant(pos):
    im = Image.new('1', (8,8), 0)
    draw = ImageDraw.Draw(im)
    draw.rectangle((pos[0]*2, pos[1]*2,
        pos[0]*2+1, pos[1]*2+1), 1, 1)
    return im

def zeros():
    return Image.new('1', (8,8), 0)

def read_hosts(filename):
    hosts = dict()
    with open(filename, 'r') as hostfile:
        data = csv.DictReader(hostfile, skipinitialspace=True)

        for row in data:
            hosts[row['name']] = {k: row[k] for k in row if k != 'name'}
            hosts[row['name']]['posx'] = int(hosts[row['name']]['posx'])
            hosts[row['name']]['posy'] = int(hosts[row['name']]['posy'])

    return hosts

def host_url(ip):
    return 'http://'+ip+':5555'

def get_direction(start, finish):
    """Return left right up or down, dependent on dir between start finish (x,y) coordinate pairs""" 
    if start[1] > finish[1]:
        dir = "up"
    elif start[1] < finish[1]:
        dir = "down"
    elif start[0] > finish[0]:
        dir = "left"
    elif start[0] < finish[0]:
        dir = "right"
    else: 
        dir = "down"
    return dir

dir_angle_up = {
    "up": 0,
    "left": 90,
    "down": 180,
    "right": 270
}

def get_pos(host):
    """Return pos from dict"""
    return (host['posx'], host['posy'])

