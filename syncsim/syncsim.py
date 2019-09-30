import argparse
import os
import re
import sys
import time
import traceback
import types

import agent
import console
import cmdlog


agent_cmd_pat = re.compile(r'\s*([a-z]\.[1-9])\s*:\s*(.+)', re.I)
should_autogossip = False


def quit():
    """
    quit              -- exit simulation
    """
    sys.exit(0)


def autogossip(*args):
    """
    autogossip on|off -- simulate background conversation
    """
    mode = 'on' if (args and args[0].lower() == 'on') else 'off'
    stdout.say('Turning autogossip %s.' % mode)
    global should_autogossip
    should_autogossip = bool(mode == 'on')


def check(*args):
    """
    check             -- see whether all agents have synchronized state
    """
    agents_by_state = {}
    for a in agent.Agent.all:
        this_state = a.all_states
        if this_state not in agents_by_state:
            agents_by_state[this_state] = [a]
        else:
            agents_by_state[this_state].append(a)
    if len(agents_by_state) == 1:
        stdout.say('All agents agree that state is %s.' % this_state)
    else:
        report = 'Agents are not fully synchronized.'
        for key, agents in agents_by_state.items():
            report += '\n   %d agents see state as: %s  (%s)' % (len(agents), key, ', '.join([a.id for a in agents]))
        stdout.say(report)


def help(*args):
    func_docs = [globals()[x].__doc__.strip() for x in funcs if x != 'help']
    method_docs = [agent.Agent.__dict__[x].__doc__.strip() for x in agent.Agent.commands]
    stdout.say("""General Commands
    %s

Agent-specific Commands
    %s""" % ('\n    '.join(func_docs), '\n    '.join(method_docs)))


funcs = [x for x in globals().keys() if type(globals()[x]) == types.FunctionType]


stdout = console.Console()

            
def abort(msg):
    stdout.say('Error: ' + msg)
    sys.exit(1)


def thread_main(agent):
    global should_autogossip
    try:
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
        stdout.say('Huh? Try "help".')
    else:
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
            elif ':' in cmd:
                stdout.say('No such agent.')
            else:
                dispatch(cmd)
            time.sleep(1)
    except KeyboardInterrupt:
        stdout.say('')


if __name__ == '__main__':
    syntax = argparse.ArgumentParser(description='Simulate the peer DID sync protocol.')
    syntax.add_argument('participants', nargs=argparse.REMAINDER, help="""
Specs for participants, such as: "A.1 A.2@x A.3-A.1 B.1@yz B.2-A.2,A.3". A and B are agent identifiers
for Alice and Bob; use any letters you like. They are not case-sensitive. Dotted notation (.1, .2, etc)
identifies specific agents. @letters notation puts the agents into one or more permission group, each
identified by a letter--so B.1@yz puts B.1 into the 'y' and the 'z' permission groups. The minus
notation says that a particular agent cannot talk to the agents that are subtracted.""")
    args = syntax.parse_args()
    cmds = cmdlog.CmdLog()
    all_agents = get_agents(args.participants, cmds)
    main(cmds)