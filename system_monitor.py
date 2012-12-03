#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable-msg=
"""
File       : system_monitor.py
Author     : Valentin Kuznetsov <vkuznet@gmail.com>
Description: system monitoring toolkit,
             retrives system information via psutil
             and provide csv values on stdout
"""

# system modules
import time
import psutil
from   optparse import OptionParser

class TestOptionParser:
    "Test option parser"
    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option("--out", action="store", type="string",
            default="", dest="out",
            help="output file name")
        self.parser.add_option("--pid", action="store", type="string",
            default="", dest="pid",
            help="pid of the process to monitor")
        self.parser.add_option("--sleep", action="store", type="string",
            default=1, dest="sleep",
            help="sleep interval in sec for monitor activity")
        activities = "cpu,mem,threads,user,system,rss,vms,connections,io,files"
        self.parser.add_option("--activity", action="store", type="string",
            default=activities,dest="activity",
            help="list of activities: %s" % activities)
        self.parser.add_option("--network", action="store_true",
            dest="network",
            help="monitor network activity")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def timestamp():
    "Standard time stamp"
    tstamp = time.strftime('%d/%b/%Y:%H:%M:%S', time.localtime())
    return tstamp

def safe_value(value):
    "Return formatted float value"
    try:
        return '%s' % value
    except:
        return None

def float_value(value):
    "Return formatted float value"
    return '%0.2f' % value

def percent_value(value):
    "Return formatted percent value"
    return '%3.1f%%' % value

def get_object_data(name, obj):
    "Retrive service data"
    data = {}
    for att in obj.__dict__.keys():
        item = '%s.%s' % (name, att)
        data[item] = getattr(obj, att)
    return data

def get_srv_data(srv):
    "Retrive service data"
    data = {}
    for key, val in srv.items():
        data.update(get_object_data(key, val))
    return data

def monitor_process(pid, activity, sleep=5):
    "Monitor given process"
    proc = psutil.Process(pid)
    cmd  = ' '.join(proc.cmdline)
    name = cmd.split('/')[-1]
    while True:
        data = {'pid': pid, 'name': name, 'status': proc.status, 'timestamp': timestamp()}
        mem_info = proc.get_memory_info()
        cpu_info = proc.get_cpu_times()
        for field in activity:
            field = field.strip()
            if field == 'cpu':
                data[field] = percent_value(proc.get_cpu_percent(interval=1.0))
            elif field == 'mem':
                data[field] = percent_value(proc.get_memory_percent())
            elif field == 'user':
                data[field] = float_value(cpu_info.user)
            elif field == 'system':
                data[field] = float_value(cpu_info.system)
            elif field == 'rss':
                data[field] = mem_info.rss
            elif field == 'vms':
                data[field] = mem_info.vms
            elif field == 'threads':
                data[field] = safe_value(proc.get_num_threads())
            elif field == 'connections':
                con_dict = {}
                for con in proc.get_connections():
                    con_dict.setdefault(con.status, []).append(con)
                for key, val in con_dict.items():
                    item = "%s.%s" % (field, key)
                    data[item] = len(val)
            elif field == 'io':
                try:
                    data[field] = safe_value(proc.get_io_counters())
                except:
                    data[field] = None
            elif field == 'files':
                data[field] = len([f for f in proc.get_open_files()])
        yield data
        time.sleep(sleep)

def monitor_system(sleep=5):
    "Monitor system activity"
    while True:
        data = {'timestamp':timestamp()}
        data['cpu'] = psutil.cpu_percent(interval=1)
        data.update(get_object_data('vmem', psutil.virtual_memory()))
        data.update(get_object_data('swap', psutil.swap_memory()))
        yield data
        time.sleep(sleep)

def monitor_network(sleep=5):
    "Monitor network activity"
    while True:
        data = {'timestamp': timestamp()}
        net  = psutil.network_io_counters(pernic=True)
        data.update(get_srv_data(net))
        yield data
        time.sleep(sleep)

def output(gen):
    "Yield results from given generator"
    columns  = ''
    for data in gen:
        if  not columns:
            columns = data.keys()
            columns.sort()
            yield ', '.join(columns)
        values = [str(data.get(c, 0)) for c in columns]
        yield ', '.join(values)

def main():
    "Main function"
    mgr      = TestOptionParser()
    opts, _  = mgr.get_opt()
    activity = opts.activity.split(',')
    sleep    = int(opts.sleep)
    pid      = int(opts.pid) if opts.pid else 0
    if  pid:
        gen = monitor_process(pid, activity, sleep)
    elif opts.network:
        gen = monitor_network(sleep)
    else:
        gen = monitor_system(sleep)
    if  opts.out:
        with open(opts.out, 'w') as stream:
            for row in output(gen):
                stream.write(row)
    else:
        for row in output(gen):
            print row

if __name__ == '__main__':
    main()
