import argparse
import os
import re
import sys
import time
import traceback
import types

from agent import Agent
import console
import cmdlog


agent_cmd_pat = re.compile(r'\s*([a-z]\.[1-9])\s*:\s*(.+)', re.I)
should_autogossip = False


def quit():
    """
    quit                  -- exit simulation
    """
    sys.exit(0)


def autogossip(*args):
    """
    autogossip on|off     -- simulate background conversation
    """
    mode = 'on' if (args and args[0].lower() == 'on') else 'off'
    stdout.say('Turning autogossip %s.' % mode)
    global should_autogossip
    should_autogossip = bool(mode == 'on')


def check(*args):
    """
    check                 -- see whether all agents have synchronized state
    """
    agents_by_state = {}
    with Agent.all_lock:
        for a in Agent.all:
            this_state = a.all_deltas
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

def describe(*args):
    """
    describe [agentpat]   -- summarize all or some agents (wildcards ok).
    """
    pat = args[0] if args else '*'
    pat = re.compile(pat.replace('.', r'[.]').replace('*', '.*').replace('?', '.'), re.I)
    summary = []
    with Agent.all_lock:
        for a in Agent.all:
            if pat.match(a.id):
                summary.append(a.description)
    summary.append('(%d agents)' % len(summary))
    stdout.say('\n'.join(summary))


def help(*args):
    func_docs = [globals()[x].__doc__.strip() for x in funcs if x != 'help']
    method_docs = [Agent.__dict__[x].__doc__.strip() for x in Agent.commands]
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
            with Agent.cmds_lock:
                n = len(Agent.cmds)
            while agent.cmd_idx < n:
                agent.next()
            if should_autogossip:
                agent.autogossip()
    except:
        agent.say(traceback.format_exc())
        os._exit(1)


def get_agents(participants):
    if len(participants) < 2:
        abort('Must have at least 2 participants.')
    Agent.thread_main = thread_main
    Agent.stdout = stdout
    agents = []
    for p in participants:
        agents.append(Agent(p))
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
    found = False
    for f in funcs:
        if f.startswith(cmd):
            cmd = f
            found = True
    if not found:
        stdout.say('Huh? Try "help".')
    else:
        func = globals()[cmd]
        func(*args)


def main():
    try:
        while True:
            cmd = get_next_command()
            m = agent_cmd_pat.match(cmd)
            if m:
                with Agent.cmds_lock:
                    Agent.cmds.append(m.group(1).upper() + ': ' + m.group(2))
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
    all_agents = get_agents(args.participants)
    main()