import datetime
import json
import os
import time

import psutil
from psutil._common import bytes2human


def get_cpu_data():
    cpu = {}  # json object

    pid = os.getpid()  # gets current process id for this file

    # Formatting on console when run
    templ = "%-6s %5s %6s %7s %7s %10s %20s %20s"
    print(templ % ("PID", "%MEM", "VSZ", "RSS", "NICE", "STATUS", "START", "TIME"))

    # list of CPU metrics needed
    attrs = ['pid', 'memory_percent', 'name', 'cmdline', 'cpu_times',
             'create_time', 'memory_info', 'status', 'nice']

    # Iterate all CPU running processes, checks if pid is same as current pid
    for proc in psutil.process_iter(attrs):
        if proc.info['pid'] == pid:
            # Process memory utilization correct to 1 d.p. (0.10944972% -> 0.1%)
            memp = round(proc.info['memory_percent'], 1) if \
                proc.info['memory_percent'] is not None else ''
            cpu['memoryPercent'] = memp  # Store process memory utilization in json object 'memoryPercent'

            # Virtual memory size from bytes to human readable string based on format (12406784 -> 11.8M)
            vms = bytes2human(proc.info['memory_info'].vms) if \
                proc.info['memory_info'] is not None else ''
            cpu['vsz'] = vms  # Store virtual memory size in json object 'vsz'

            # Resident set size from bytes to human readable string based on format (18546688 -> 17.7M)
            rss = bytes2human(proc.info['memory_info'].rss) if \
                proc.info['memory_info'] is not None else ''
            cpu['rss'] = rss  # Store resident set size in json object 'rss'

            # Checks if current process has nice value, else nice is ''
            nice = int(proc.info['nice']) if proc.info['nice'] else ''
            cpu['nice'] = nice  # Store nice in json object 'nice'

            # Checks if current process has status value, else status is ''
            status = proc.info['status'] if proc.info['status'] else ''
            cpu['status'] = status  # Store status in json object 'status'

            cpu['pid'] = pid  # Store process id in json object 'pid'

            # Process start time from floating point to readable datetime format -> 2021-10-28 13:03:27.182989
            if proc.info['create_time']:
                ctime = datetime.datetime.fromtimestamp(proc.info['create_time'])
                ctime = ctime.strftime("%d/%m/%Y %H:%M:%S")  # Customise datetime format -> 28/10/2021 13:03:27
                cpu['startTime'] = ctime  # Store datetime in json object 'startTime'
            else:
                ctime = ''
                cpu['startTime'] = ''

            # Process runtime formatted to min and sec -> 00min 01seconds
            if proc.info['cpu_times']:
                cputime = time.strftime("%Mmin %Sseconds", time.localtime(sum(proc.info['cpu_times'])))
                cpu['runTime'] = cputime  # Store cputime in json object 'runTime'
            else:
                cputime = ''
                cpu['runTime'] = ''

            # Print out the CPU metrics of current process
            print(templ % (proc.info['pid'], memp, vms, rss, nice, status, ctime, cputime))
    return (json.dumps(cpu))


if __name__ == "__main__":
    get_cpu_data()
