SMTools
=======

System Monitoring tools is a collection of tools to monitor system performance.

Requirements
------------

`system_monitor.py` script depends on psutil module.

Tools
-----

- `system_monitor.py` script provides similar functionality as top

```
Usage: system_monitor.py [options]

Options:
  -h, --help           show this help message and exit
  --pid=PID            pid of the process to monitor
  --sleep=SLEEP        sleep interval in sec for monitor activity
  --activity=ACTIVITY  activities: mem,cpu,threads
  --network            monitor network activity
```

- `analyzer_pid.R` script analyzes pid log data and produces standard set of plots
