import os
import time
import glob
import requests
from PIL import Image
from utils import *
import multiprocessing as mp
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Generic base class
class DisplayObject():
    def display(self, display): pass

# Generic image class
class DisplayImage(DisplayObject):
    def __init__(self, image_name=None, image=None, img_dir='img', delay=0.5):
        """"Loads image as DisplayObject from img_dir/image_name.

        Also can load from PIL image passed to "image".
        Will stay on screen for delay seconds.
        """
        if image_name:
            if img_dir: self.image = Image.open('{0}/{1}'.format(img_dir, image_name)).convert(mode='1')
            else: self.image = Image.open(image_name).convert(mode='1')
        elif image:
            self.image = image
        else:
            self.image = Image.new('1', (8,8), 0)
        self.delay = delay

    def rotate(self, angle):
        """Rotates image angle degrees counter-clockwise"""
        self.image = self.image.rotate(angle)
        return self

    def display(self, display, start_time=None):
        """Process image once reached in queue"""
        display.__process_frame__(self.image, start_time or time.time(), delay=self.delay)

# Animation class of DisplayObjects
class Animation(DisplayObject):
    def __init__(self, frames = None):
        """"Loads given array of DisplayObject's, or nothing"""
        self.frames = frames or list()

    def load_folder(self, folder, img_dir='img', format='ppm', delay=0.5):
        """Loads all images from given folder, globbing for format.
        Passes delay to DisplayImage
        """
        for fn in sorted(glob.glob('{0}/{1}/*.{2}'.format(img_dir, folder, format))):
            self.frames.append(DisplayImage(fn, img_dir=None, delay=delay))
        return self

    def rotate(self, angle):
        """Rotate images internally angle degrees counter-clockwise"""
        for im in self.frames:
            if isinstance(im, DisplayImage): im.rotate(angle)
        return self

    def display(self, display):
        """Process animation when reached in queue"""
        for im in self.frames:
            if isinstance(im, DisplayObject): im.display(display)

# Generic Blocking DisplayObject
class Block(DisplayObject):
    def __init__(self, connection=None, entry_seq = None, exit_seq = None):
        """Creates blocking display object.
        entry_seq - displayed before blocking
        exit_seq - displayed after blocking
        connection - the blocking object - normally a pipe, just needs to
        implement a recv method
        """

        self.entry_seq = entry_seq
        self.exit_seq = exit_seq
        self.connection = connection

    def on_entry(self, display):
        if isinstance(self.entry_seq, DisplayObject):
            self.entry_seq.display(display)

    def wait(self, display):
        return self.connection.recv()

    def on_exit(self, display):
        if isinstance(self.exit_seq, DisplayObject):
            self.exit_seq.display(display)

    def display(self,display):
        self.on_entry(display)
        self.wait(display)
        self.on_exit(display)

# Send Animation
class Send(Block):
    def __init__(self, src, dest, hosts, *args, **kwargs):
        """Send animation from src to dst with hostfile hsts """
        super().__init__(*args, **kwargs)
        self.src = src
        self.dest = dest
        self.hosts = hosts

        angle = dir_angle_up[get_direction(get_pos(hosts[src]), get_pos(hosts[dest]))]
        idle = DisplayImage('arrow-up/08.ppm').rotate(angle)
        dest_pos = (hosts[dest]['posx'], hosts[dest]['posy'])
        dest_anim = [DisplayImage(image=one_octant(dest_pos)),
                    idle]* 2

        self.entry_seq = Animation(dest_anim)
        self.exit_seq = Animation().load_folder('arrow-up').rotate(angle)

        logging.debug('Send created from {0} to {1} going {2}'.format(src, dest, angle))

    def on_entry(self, display):
        super().on_entry(display)
        # Post to `rank` node with send confirmation
        requests.post(host_url(self.hosts[self.dest]['ip']) + '/send/', data = { 'src' : self.src, 'dest': self.dest, 'c': 1 })

# Receive Animation
class Recv(Block):
    def __init__(self, src, dest, hosts, *args, **kwargs):
        """Receive animation from src to dst with hostfile hsts"""
        super().__init__(*args, **kwargs)
        self.src = src
        self.dest = dest
        self.hosts = hosts

        angle = dir_angle_up[get_direction(get_pos(hosts[src]), get_pos(hosts[dest]))]

        src_pos = (hosts[src]['posx'], hosts[src]['posy'])
        src_anim = [DisplayImage(image=one_octant(src_pos)),
                DisplayImage('arrow-up-in/08.ppm').rotate(angle)] * 2

        logging.debug('Receive created from {0} to {1} going {2}'.format(src, dest, angle))
        self.entry_seq = Animation(src_anim)
        self.exit_seq = Animation().load_folder('arrow-up-in').rotate(angle)
        self.exit_seq.frames.append(DisplayImage(image=zeros()))

    def on_entry(self, display):
        super().on_entry(display)
        # Post to `rank` node with send confirmation
        requests.post(host_url(self.hosts[self.src]['ip']) + '/receive/', data = { 'src' : self.src, 'dest': self.dest, 'c': 1})

# Non-blocking send animation
class Isend(Send):
    def wait(self, display): pass

# Idle animation
class Idle(Animation):
    def __init__(self, length, pause=0.1, frames=None):
        super().__init__(frames)
        if not frames:
            self.load_folder('idle')
            #  self.frames.append(self.frames[-1])
        self.length = float(length)
        self.pause = float(pause)

    def display(self, display):
        start_time = time.time()
        while time.time() - start_time < self.length:
            super().display(display)
            time.sleep(self.pause)

# Broadcast Animation
class Bcast(Block):
    def __init__(self, src, host, dests, conns, hosts, *args, **kwargs):
        """Creates broadcast animation from src to dests on host
        conns - dict of pipe-like objects (implements recv), which represent
        the destinations.
        """
        super().__init__(*args, **kwargs)
        self.src = src
        self.host = host
        self.dests = dests
        self.conns = conns
        self.hosts = hosts

        if self.host != self.src:
            src_pos = (hosts[src]['posx'], hosts[src]['posy'])
            src_anim = [DisplayImage(image=one_octant(src_pos)),
                    DisplayImage('arrow-down/09.ppm')] * 2

            self.entry_seq = Animation(src_anim)
            self.anim = Animation(src_anim)
            self.exit_seq = Animation([src_anim[-1]]).load_folder('arrow-down-out')
        else:
            self.anim = Animation().load_folder('bcast')
            self.exit_seq = Animation().load_folder('arrow-up')

    def on_entry(self, display):
        super().on_entry(display)
        if self.host != self.src:
            requests.post(host_url(self.hosts[self.src]['ip']) + '/bcast/', data = {
                'src' : self.src,
                'host': self.host,
                'c': 1})
            logging.debug("{0} confirmed with root node {1}".format(self.host, self.src))

    # Display anim loop until done
    #TODO: find better way?
    def wait(self, display):
        """Waits on a dict of pipes to finish, in a minimally-intensive way"""
        def get_conns(dests, conns):
            for dest in dests: conns.get()
        def loop_display(anim, display, ready):
            while not ready.poll(): anim.display(display)

        p1 = mp.Process(target=get_conns, args=(self.dests,self.conns))
        ready = mp.Pipe()
        p2 = mp.Process(target=loop_display, args=(self.anim, display, ready[1]))
        p1.start()
        p2.start()
        p1.join()
        ready[0].send(True)
        p2.join()

    def on_exit(self, display):
        def confirm(src,dests,host, hosts):
            for dest in dests:
                requests.post(host_url(hosts[dest]['ip']) + '/bcast/', data = {
                    'src' : src, 'host': host, 'c': 1})
                logging.debug("root node {0} confirmed with {1}".format(self.host, dest))
        if self.host == self.src:
            p = mp.Process(target=confirm, args=(self.src, self.dests,self.host, self.hosts))
            p.start()
            super().on_exit(display)
            p.join()

        else: super().on_exit(display)

class Gather(Block):
    def __init__(self, dest, host, srcs, conns, hosts, *args, **kwargs):
        """Creates gather animation from srcs to dest on host
        conns - dict of pipe-like objects (implements recv), which represent
        the destinations.
        """
        super().__init__(*args, **kwargs)
        self.dest = dest
        self.host = host
        self.srcs = srcs
        self.conns = conns
        self.hosts = hosts

        if self.host != self.dest:
            dest_pos = (hosts[dest]['posx'], hosts[dest]['posy'])
            dest_anim = [DisplayImage(image=one_octant(dest_pos)),
                        DisplayImage('arrow-up/08.ppm')]* 2

            self.entry_seq = Animation(dest_anim)
            self.anim = Animation(dest_anim)
            self.exit_seq = Animation().load_folder('arrow-up')

        else:
            self.anim = Animation().load_folder('gather')
            self.exit_seq = Animation().load_folder('arrow-down-out')

    def on_entry(self, display):
        super().on_entry(display)
        if self.host != self.dest:
            requests.post(host_url(self.hosts[self.dest]['ip']) + '/gather/', data = {
                'dest' : self.dest,
                'host': self.host,
                'c': 1})

    # Display anim loop until done - TODO: find better way?
    #TODO: Sync this with reception
    def wait(self, display):
        """Waits on a dict of pipes to finish, in a minimally-intensive way"""
        def get_conns(srcs, conns):
            for src in srcs: conns.get()
        def loop_display(anim, display, ready):
            while not ready.poll(): anim.display(display)

        p1 = mp.Process(target=get_conns, args=(self.srcs,self.conns))
        ready = mp.Pipe()
        p2 = mp.Process(target=loop_display, args=(self.anim, display, ready[1]))
        p1.start()
        p2.start()
        p1.join()
        ready[0].send(True)
        p2.join()

    def on_exit(self, display):
        def confirm(dest, srcs, host, hosts):
            for src in srcs:
                requests.post(host_url(hosts[src]['ip']) + '/gather/', data = {
                    'dest' : dest, 'host': host, 'c': 1})

        if self.host == self.dest:
            p = mp.Process(target=confirm, args=(self.dest, self.srcs, self.host, self.hosts))
            p.start()
            p.join()
            super().on_exit(display)

        else: super().on_exit(display)

class Scatter(Block):
    def __init__(self, src, host, dests, conns, hosts, *args, **kwargs):
        """Creates scatter animation from src to dests on host
        conns - dict of pipe-like objects (implements recv), which represent
        the destinations.
        """
        super().__init__(*args, **kwargs)
        self.src = src
        self.host = host
        self.dests = dests
        self.conns = conns
        self.hosts = hosts

        if self.host != self.src:
            src_anim = [DisplayImage(image=one_col(hosts[host]['posy'])),
                    DisplayImage('arrow-down/09.ppm')] * 2

            self.entry_seq = Animation(src_anim)
            self.anim = Animation(src_anim)
            self.exit_seq = Animation([src_anim[-1]]).load_folder('arrow-down-out')

        else:
            self.anim = Animation().load_folder('scatter')
            self.exit_seq = Animation().load_folder('arrow-up')

    def on_entry(self, display):
        super().on_entry(display)
        if self.host != self.src:
            requests.post(host_url(self.hosts[self.src]['ip']) + '/scatter/', data = {
                'src' : self.src,
                'host': self.host,
                'c': 1})

    # Display anim loop until done - TODO: find better way?
    #TODO: Sync this with reception
    def wait(self, display):
        """Waits on a dict of pipes to finish, in a minimally-intensive way"""
        def get_conns(dests, conns):
            for dest in dests: conns.get()
        def loop_display(anim, display, ready):
            while not ready.poll(): anim.display(display)

        p1 = mp.Process(target=get_conns, args=(self.dests,self.conns))
        ready = mp.Pipe()
        p2 = mp.Process(target=loop_display, args=(self.anim, display, ready[1]))
        p1.start()
        p2.start()
        p1.join()
        ready[0].send(True)
        p2.join()

    def on_exit(self, display):
        def confirm(src,dests,host, hosts):
            for dest in dests:
                requests.post(host_url(hosts[dest]['ip']) + '/scatter/', data = {
                    'src' : src, 'host': host, 'c': 1})
        if self.host == self.src:
            p = mp.Process(target=confirm, args=(self.src, self.dests,self.host, self.hosts))
            p.start()
            super().on_exit(display)
            p.join()

        else: super().on_exit(display)

class Reduce(Block):
    def __init__(self, op, dest, host, srcs, conns, hosts, *args, **kwargs):
        """Creates reduce animation from src to dests on host
        conns - dict of pipe-like objects (implements recv), which represent
        the destinations.
        """
        super().__init__(*args, **kwargs)
        self.op = op
        self.dest = dest
        self.host = host
        self.srcs = srcs
        self.conns = conns
        self.hosts = hosts

        dest_pos = (hosts[dest]['posx'], hosts[dest]['posy'])
        dest_anim = [DisplayImage(image=one_octant(dest_pos)),
                    DisplayImage('reduce/{0}.ppm'.format(op))]* 2

        self.entry_seq = Animation(dest_anim)
        self.anim = Animation(dest_anim)

        if self.host != self.dest:
            self.exit_seq = Animation().load_folder('arrow-up')
        else:
            self.exit_seq = Animation().load_folder('arrow-down-out')

    def on_entry(self, display):
        super().on_entry(display)
        if self.host != self.dest:
            requests.post(host_url(self.hosts[self.dest]['ip']) + '/reduce/', data = {
                'op': self.op, 'dest' : self.dest, 'host': self.host, 'c': 1})

    # Display anim loop until done - TODO: find better way?
    #TODO: Sync this with reception
    def wait(self, display):
        """Waits on a dict of pipes to finish, in a minimally-intensive way"""
        def get_conns(srcs, conns):
            for src in srcs: conns.get()
        def loop_display(anim, display, ready):
            while not ready.poll(): anim.display(display)

        p1 = mp.Process(target=get_conns, args=(self.srcs,self.conns))
        ready = mp.Pipe()
        p2 = mp.Process(target=loop_display, args=(self.anim, display, ready[1]))
        p1.start()
        p2.start()
        p1.join()
        ready[0].send(True)
        p2.join()

    def on_exit(self, display):
        def confirm(dest, srcs, host, hosts):
            for src in srcs:
                requests.post(host_url(hosts[src]['ip']) + '/reduce/', data = {
                'op': self.op, 'dest' : self.dest, 'host': self.host, 'c': 1})

        if self.host == self.dest:
            p = mp.Process(target=confirm, args=(self.dest, self.srcs, self.host, self.hosts))
            p.start()
            super().on_exit(display)
            p.join()

        else: super().on_exit(display)
