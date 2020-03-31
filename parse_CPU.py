import os
from lib import G16Log

import pandas as pd

cpus = {}
for dir in [x for x in os.listdir('neutral') if os.path.isdir(x)]:
    for log in [x for x in os.listdir(os.path.join('neutral', dir))
                   if '.log' in log]:
        name = log.split('_')[0]
        log = os.path.join('neutral', dir, log)
        g16_log = G16Log(log)

        if g16_log.termination:
            day, hour, min, sec = g16_log.CPU
            cpu_s = day*24*3600 + hour*3600 + min*60 + sec
            cpus[name] = [cpu_s]

for dir in [x for x in os.listdir('minus1') if os.path.isdir(x)]:
    for log in [x for x in os.listdir(os.path.join('minus1', dir))
                if '.log' in log]:
        name = log.split('_')[0]
        if name not in cpus:
            continue

        log = os.path.join('neutral', dir, log)
        g16_log = G16Log(log)

        if g16_log.termination:
            day, hour, min, sec = g16_log.CPU
            cpu_s = day * 24 * 3600 + hour * 3600 + min * 60 + sec
            cpus[name].append(cpu_s)

for dir in [x for x in os.listdir('plus1') if os.path.isdir(x)]:
    for log in [x for x in os.listdir(os.path.join('plus1', dir))
                if '.log' in log]:
        name = log.split('_')[0]
        if name not in cpus:
            continue

        log = os.path.join('neutral', dir, log)
        g16_log = G16Log(log)

        if g16_log.termination:
            day, hour, min, sec = g16_log.CPU
            cpu_s = day * 24 * 3600 + hour * 3600 + min * 60 + sec
            cpus[name].append(cpu_s)

cpus = {k:v for k,v in cpus.items() if len(v) == 3}
cpus = pd.DataFrame.from_dict(cpus, columns=['neutral', 'minus1', 'plus1'], orient='index')
cpus.to_csv('cpu_collected.csv')

