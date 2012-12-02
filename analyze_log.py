#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable-msg=
"""
File       : analyze_log.py
Author     : Valentin Kuznetsov <vkuznet@gmail.com>
Description: 
"""

# system modules
import os
import sys
import time
from   optparse import OptionParser

# matplotlib
import matplotlib
import matplotlib.pyplot as plt

class TestOptionParser: 
    "Test option parser"
    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option("--log", action="store", type="string", 
            default="", dest="log",
            help="input log file")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def parse(log, sep=', '):
    "Parse log file"
    columns = []
    with open(log, 'r') as stream:
        for line in stream.readlines():
            line = line.replace('\n', '')
            if  not columns:
                columns = line.split(sep)
            values = line.split(sep)
            if  values != columns:
                yield dict(zip(columns, values))

def adjust_value(key, val):
    "Adjust values in data"
    if  key in ['cpu', 'mem']:
        val = float(val.replace('%', ''))
    if  key in ['files', 'threads', 'vms', 'rss']:
        val = int(val)
        if  key in ['vms', 'rss']:
            val = val/1024./1024.
    if  key in ['user', 'system']:
        val = float(val)
    return val

def plot(data):
    "Plot given data"
    font = {'size': 8} # another keys are: family, weight, etc.
    matplotlib.rc('font', **font)
    plt.figure(1)
    nrows = 4
    ncols = 3
    figid = 1
    keys  = ['cpu', 'user', 'system', 'mem', 'rss', 'vms',
             'connections.CLOSE_WAIT', 'connections.ESTABLISHED',
             'connections.LISTEN', 'threads']
    for key in keys:
        plt.subplot(nrows, ncols, figid)
        plt.plot(data['time'], data[key], '-')
        plt.xlabel('Time')
        plt.ylabel(key.upper())
        figid += 1
    plt.subplot(nrows, ncols, figid)
    plt.plot(data['cpu'], data['rss'], 'bo')
    plt.xlabel('CPU')
    plt.ylabel('RSS')
    plt.subplot(nrows, ncols, figid+1)
    plt.plot(data['cpu'], data['vms'], 'bo')
    plt.xlabel('CPU')
    plt.ylabel('VMS')
    plt.savefig('summary.pdf', format='pdf', transparent=True)

def collect_data(log):
    "Collect all data for plotting"
    data  = {}
    time0 = 0
    for row in parse(log):
        for key, val in row.items():
            data.setdefault(key, []).append(adjust_value(key, val))
            if  key == 'timestamp':
                tstamp = time.strptime(row['timestamp'], '%d/%b/%Y:%H:%M:%S')
                if  not time0:
                    time0 = time.mktime(tstamp)
                data.setdefault('time', []).append(time.mktime(tstamp)-time0)
    return data

def main():
    "Main function"
    mgr      = TestOptionParser()
    opts, _  = mgr.get_opt()
    data = collect_data(opts.log)
    plot(data)

if __name__ == '__main__':
    main()
