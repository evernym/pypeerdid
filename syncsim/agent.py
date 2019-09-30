import random
import re
import threading
import time

valid_spec_pat = re.compile(r'^[A-Z]\.[1-9](?:@([A-Z]+))?(-[A-Z]\.[1-9](,[A-Z]\.[1-9])*)?$')
m_of_n_of_group_pat = re.compile(r'^(.*),(?:([1-9])/)?([1-9])@([a-z])$')


class Agent:
    all = []

    def __init__(self, spec, cmds, main, stdout):
        spec = spec.upper()
        m = valid_spec_pat.match(spec)
        if not m:
            raise Exception('Bad spec "%s".' % spec)
        self.party = spec[0]
        self.num = spec[2]
        self.groups = m.group(1).lower() if m.group(1) else ''
        self.cant_reach = m.group(2)[1:].split(',') if m.group(2) else []
        self.cmd_idx = 0
        self.deltas = {}
        self.stdout = stdout
        self.cmds = cmds
        self.thread = threading.Thread(target=main, args=(self,), daemon=True)
        self.thread.start()
        Agent.all.append(self)

    def next(self):
        cmd = self.cmds.items[self.cmd_idx]
        if cmd.startswith(self.id):
            rest = cmd[4:].lstrip()
            if rest.startswith('simple'):
                self.simple(rest[6:].lstrip())
            elif rest.startswith('add'):
                self.add(rest[3:].lstrip())
            elif rest.startswith('rem'):
                self.rem(rest[3:].lstrip())
            elif rest.startswith('state'):
                self.state()
            elif rest.startswith('gossip'):
                self.say('Gossipping.')
                self.gossip()
            else:
                self.say('Huh? Try "help".')
        self.cmd_idx += 1

    def init_parties(self, parties):
        for p in parties:
            self.deltas[p] = ['#']

    def simple(self, suffix=None):
        """
        X9: simple [N@M]  -- generate a simple state change that doesn't change active agents
                         (key rotate, add/remove rule, add/remove endpoint), optionally
                         requiring N signatures from group M
        """
        ch = '#' + hex(random.randint(4096, 256*256))[2:]
        if suffix:
            ch += ',' + suffix
        ch = self.append_delta(ch)
        self.say('Created delta %s. I now see %s.' % (ch, self.all_deltas))
        self.broadcast(self.party + '+' + ch)

    def add(self, spec, suffix=None):
        """
        X9: add [N@M]     -- generate a state change that adds an active agent, optionally
                         requiring N signatures from group M
        """
        pass

    def rem(self, spec, suffix=None):
        """
        X9: rem [N@M]     -- generate a state change that removes an active agent, optionally
                         requiring N signatures from group M
        """
        pass

    def say(self, msg):
        self.stdout.say(self.id + ' -- ' + msg)

    @property
    def all_deltas(self):
        return '; '.join([x + '=' + self.get_state(x) for x in sorted(self.deltas.keys())])

    def state(self):
        """
        X9: state         -- report my state
        """
        self.say('OK; I see ' + self.all_deltas)

    def get_state(self, party=None):
        if party is None:
            party = self.party
        return '+'.join(self.deltas[party])

    @property
    def full_id(self):
        id = self.id
        if self.groups:
            id += '@' + self.groups
        return id


    @property
    def id(self):
        return self.party + '.' + self.num


    def __str__(self):
        return self.id

    def receive(self, msg):
        party = msg[0]
        self.append_delta(msg[2:], party)
        self.say('Received change. I now see ' + self.all_deltas)
        # Introduce some randomness so order of events from other agents
        # can vary.
        time.sleep(random.random() / 8)

    def append_delta(self, delta, party=None):
        if party is None:
            party = self.party
        lst = self.deltas[party]
        # Disregard deltas that we already know about.
        if delta not in lst:
            # Is this an m-of-n change?
            match = m_of_n_of_group_pat.match(delta)
            if match:
                # Figure out m, n, and group name.
                m = int(match.group(2)) if match.group(2) else 0
                n = int(match.group(3))
                group = match.group(4)
                # Do we already know about this delta, but with a different
                # number of endorsements?
                old_idx = -1
                i = 0
                for old in lst:
                    if old.startswith(match.group(1)):
                        old_idx = i
                        break
                    i += 1
                # Can we endorse this change, increasing m by 1?
                if (m < n) and (old_idx == -1) and (party == self.party) and (group in self.groups):
                    m += 1
                    delta = '%s,%s/%s@%s' % (match.group(1), m, n, group)
                if old_idx > -1:
                    lst[old_idx] = delta
                else:
                    lst.append(delta)
            else:
                lst.append(delta)
            lst.sort()
        return delta

    @property
    def reachable(self):
        return [a for a in Agent.all if a != self and a.id not in self.cant_reach]

    def broadcast(self, delta):
        targets = self.reachable
        if targets:
            for a in targets:
                a.receive(delta)

    def gossip(self, targets=None):
        """
        X9: gossip        -- talk to any agents that X9 can reach
        """
        if targets is None:
            targets = self.reachable
        if targets:
            def sync(s, t):
                for key in s.deltas:
                    for delta in s.deltas[key]:
                        if delta not in t.deltas[key]:
                            s.say('Gossipped %s --%s+%s--> %s' % (s.id, key, delta, t.id))
                            t.receive(key + '+' + delta)
            for t in targets:
                sync(self, t)
                sync(t, self)

    def autogossip(self):
        if random.random() < 0.05:
            target = random.choice(self.reachable)
            self.gossip([target])

    commands = ['simple', 'add', 'rem', 'state', 'gossip']