import argparse
import os
import re
import sys
import threading
import time
import traceback
import types

import agent
import console

agent_cmd_pat = re.compile(r'([a-z][1-9]):\s*(.+)', re.I)
should_autogossip = False
all_agents = []


def quit():
    sys.exit(0)


def autogossip(*args):
    mode = 'on' if (args and args[0].lower() == 'on') else 'off'
    stdout.say('Turning autogossip ' + mode)
    global should_autogossip
    should_autogossip = True if mode == 'on' else 'off'


def check():
    pass


def help():
    print('Commands = ' + ', '.join(funcs) + ' OR A1: change')


funcs = [x for x in globals().keys() if type(globals()[x]) == types.FunctionType]


stdout = console.Console()

            
class Commands:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.lock.release()


def abort(msg):
    stdout.say('Error: ' + msg)
    sys.exit(1)


def thread_main(agent):
    try:
        agent.say('Started.')
        while True:
            time.sleep(0.33)
            with agent.cmds:
                n = len(agent.cmds.items)
            while agent.cmd_idx < n:
                agent.next()
            if should_autogossip:
                agent.autogossip()
    except:
        agent.say(traceback.format_exc())
        os._exit(1)


def get_agents(participants, cmds):
    if len(participants) < 2:
        abort('Must have at least 2 participants.')
    agents = []
    for p in participants:
        agents.append(agent.Agent(p, cmds, thread_main, stdout))
    parties = set([a.party for a in agents])
    if len(parties) < 2:
        abort('Must have at least two parties.')
    for a in agents:
        a.init_parties(parties)
    return agents


def get_next_command():
    stdout.prompt()
    x = input().strip()
    with stdout:
        stdout.prompting = False
    return x


def dispatch(cmd):
    args = re.split(r'\s+', cmd)
    cmd = args[0].replace('()', '')
    args = args[1:]
    if cmd not in funcs:
        abort('No such function ("' + cmd + '").')
    func = globals()[cmd]
    func(*args)


def main(cmds):
    try:
        while True:
            cmd = get_next_command()
            m = agent_cmd_pat.match(cmd)
            if m:
                with cmds:
                    cmds.items.append(m.group(1).upper() + ': ' + m.group(2))
            else:
                dispatch(cmd)
            time.sleep(1)
    except KeyboardInterrupt:
        stdout.say('')


if __name__ == '__main__':
    syntax = argparse.ArgumentParser(description='Simulate the peer DID sync protocol.')
    syntax.add_argument('participants', nargs=argparse.REMAINDER, help="""
Specs for participants, such as: "A1 A2 A3-A1 B1 B2-A2,A3". A and B are agent identifiers for Alice and Bob.
Digits are agent numbers. The minus notation says that a particular agent cannot talk to the agents that are
subtracted.""")
    args = syntax.parse_args()
    cmds = Commands()
    all_agents = get_agents(args.participants, cmds)
    main(cmds)