import random
import re
import threading
import time

valid_spec_pat = re.compile('[A-Z][1-9](-[A-Z][1-9](,[A-Z][1-9])*)?')


class Agent:
    all = []
    def __init__(self, spec, cmds, main, stdout):
        self.stdout = stdout
        spec = spec.upper()
        m = valid_spec_pat.match(spec)
        if not m:
            raise Exception('Bad spec.')
        self.cmds = cmds
        self.party = spec[0]
        self.num = spec[1]
        self.cant_reach = m.group(1)[1:].split(',') if m.group(1) else []
        self.cmd_idx = 0
        self.states = {}
        self.thread = threading.Thread(target=main, args=(self,), daemon=True)
        self.thread.start()
        Agent.all.append(self)

    def init_parties(self, parties):
        for p in parties:
            self.states[p] = ['!' + p]

    def simulate_change(self):
        change = hex(random.randint(256, 256*256))[2:]
        self.append_state(change)
        self.say('Created delta ' + change)
        return change

    def next(self):
        cmd = self.cmds.items[self.cmd_idx]
        if cmd.startswith(self.id):
            rest = cmd[3:].lstrip()
            if rest.startswith('change'):
                change = self.simulate_change()
                self.say('OK, added change. I now see ' + self.all_states)
                self.broadcast(self.party + '+' + change)
            elif rest.startswith('state'):
                self.say('OK; I see ' + self.all_states)
            elif rest.startswith('gossip'):
                self.say('OK, gossipping.')
                self.gossip()
            else:
                self.say('Huh?')
        self.cmd_idx += 1

    def say(self, msg):
        self.stdout.say(self.id + ' -- ' + msg)

    @property
    def all_states(self):
        return '; '.join([x + '=' + self.state(x) for x in sorted(self.states.keys())])

    def state(self, party=None):
        if party is None:
            party = self.party
        return '.'.join(self.states[party])

    @property
    def id(self):
        return self.party + self.num

    def __str__(self):
        return self.id

    def receive(self, msg):
        party = msg[0]
        self.append_state(msg[2:], party)
        self.say('Received change. I now see ' + self.all_states)
        time.sleep(random.random() / 4)

    def append_state(self, x, party=None):
        if party is None:
            party = self.party
        lst = self.states[party]
        lst.append(x)
        lst.sort()

    @property
    def reachable(self):
        return [a for a in Agent.all if a != self and a.id not in self.cant_reach]

    def broadcast(self, msg):
        targets = self.reachable
        if targets:
            for a in targets:
                a.receive(msg)

    def gossip(self, targets=None):
        if targets is None:
            targets = self.reachable
        if targets:
            def sync(s, t):
                for key in s.states:
                    for delta in s.states[key]:
                        if delta not in t.states[key]:
                            t.receive(key + '+' + delta)
            for t in targets:
                sync(self, t)
                sync(t, self)

    def autogossip(self):
        if random.random() < 0.05:
            target = random.choice(self.reachable)
            self.say('Talking to ' + target.id)
            self.gossip([target])
