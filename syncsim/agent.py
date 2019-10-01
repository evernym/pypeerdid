import copy
import random
import re
import threading
import time

valid_spec = r'[A-Za-z]\.[1-9](?:@([a-z]+))?(?:-([A-Za-z]\.[1-9](?:,[A-Za-z]\.[1-9])*))?'
valid_spec_pat = re.compile(r'^%s$' % valid_spec)
m_of_n_of_group_pat = re.compile(r'^(.*?)(?: by {(.*?)}/)?([1-9])@([a-z])$')
simple_pat = re.compile(r'simple(?:\s+by\s+([1-9]@[a-z]))?$')
add_rem_pat = re.compile(r'([a-z]+)\s+(%s)(?:\s+by\s+([1-9]@[a-z]))?$' % valid_spec)


def split_spec(spec):
    m = valid_spec_pat.match(spec)
    return spec[0], spec[2], m.group(1), m.group(2)


def norm_spec(spec):
    party, num, groups, cant_reach = split_spec(spec)
    return party.upper(), num, \
           groups.lower() if groups else '', \
           cant_reach.upper().split(',') if cant_reach else []


class Agent:

    all_lock = threading.Lock()
    all = []
    thread_main = None
    stdout = None
    cmds_lock = threading.Lock()
    cmds = []

    def __init__(self, spec, initial_state=None):
        self.party, self.num, self.groups, self.cant_reach = norm_spec(spec)
        self.cmd_idx = 0
        if not initial_state:
            initial_state = {}
        self.deltas_lock = threading.Lock()
        self.deltas = initial_state
        self.thread = threading.Thread(target=Agent.thread_main, args=(self,), daemon=True)
        with Agent.all_lock:
            Agent.all.append(self)
        self.thread.start()

    def next(self):
        handled = True
        cmd = self.cmds[self.cmd_idx]
        if cmd.startswith(self.id):
            rest = cmd[4:].lstrip()
            m = simple_pat.match(rest)
            if m:
                self.simple(m.group(1))
            elif rest.startswith('state'):
                self.state()
            elif rest.startswith('gossip'):
                self.say('Gossipping.')
                self.gossip()
            else:
                m = add_rem_pat.match(rest)
                if m:
                    if m.group(1) == 'add':
                        self.add(m.group(2), m.group(5))
                    elif m.group(1) == 'rem':
                        self.rem(m.group(2), m.group(5))
                    else:
                        handled = False
                else:
                    handled = False
        if not handled:
                self.say('Huh? Try "help".')
        self.cmd_idx += 1

    def init_parties(self, parties):
        for p in parties:
            self.deltas[p] = ['#']

    def simple(self, auth=None):
        """
        A.2: simple [by N@M]  -- simulate a simple delta that doesn't change active agents
                             (key rotate, add/remove rule, add/remove endpoint), optionally
                             requiring N signatures from group M
        """
        delta = '#' + hex(random.randint(4096, 256*256))[2:]
        if auth:
            delta += ' by ' + auth
        delta = self.append_delta(delta)
        self.say('Created delta %s. I now see %s.' % (delta, self.all_deltas))
        self.broadcast(self.party + '+' + delta)

    def add(self, spec, auth=None):
        """
        A.8: add A.9 [by N@M] -- simulate a delta that adds an active agent, optionally
                             requiring N signatures from group M
        """
        try:
            party, num, groups, subtracted = norm_spec(spec)
        except:
            self.say('Bad spec "%s".' % spec)
            return
        if party != self.party:
            self.say("I'm in %s; I can't add a key for %s." % (self.party, party))
            return
        with Agent.all_lock:
            for a in Agent.all:
                if a.party == party and a.num == num:
                    self.say('Agent %s already exists.' % spec)
                    return

        delta = '#add-%s.%s' % (party, num)
        if auth:
            delta += ' by {}/' + auth
        delta = self.append_delta(delta)
        new_agent = Agent(spec, copy.deepcopy(self.deltas))
        self.broadcast(self.party + '+' + delta)

    def rem(self, spec, suffix=None):
        """
        A.2: rem A.4 [by N@M] -- simulate a delta that removes an active agent, optionally
                             requiring N signatures from group M
        """
        pass

    def say(self, msg):
        Agent.stdout.say(self.id + ' -- ' + msg)

    @property
    def all_deltas(self):
        with self.deltas_lock:
            return '; '.join([x + '=' + self.get_state(x) for x in sorted(self.deltas.keys())])

    @property
    def description(self):
        d = self.full_id
        if self.cant_reach:
            d += '-' + ','.join(self.cant_reach)
        d += ' => ' + self.all_deltas
        return d

    def state(self):
        """
        B.3: state            -- report my state
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
        self.say('Received delta. I now see ' + self.all_deltas)
        # Introduce some randomness so order of events from other agents
        # can vary.
        time.sleep(random.random() / 8)

    def append_delta(self, delta, party=None):
        if party is None:
            party = self.party
        lst = self.deltas[party]
        with self.deltas_lock:
            # Disregard deltas that we already know about.
            if delta not in lst:
                # Is this an m-of-n change?
                match = m_of_n_of_group_pat.match(delta)
                if match:
                    # Figure out endorsers, n, and group name.
                    endorsers = match.group(2).split(',') if match.group(2) else []
                    n = int(match.group(3))
                    group = match.group(4)
                    # Do we already know about this delta, but with different
                    # endorsers?
                    old_idx = -1
                    i = 0
                    for old in lst:
                        if old.startswith(match.group(1)):
                            old_match = m_of_n_of_group_pat.match(old)
                            old_endorsers = old_match.group(2).split(',') if old_match.group(2) else []
                            endorsers = sorted(list(set(endorsers + old_endorsers)))
                            old_idx = i
                            break
                        i += 1
                    # Can we endorse this change?
                    if len(endorsers) < n and (party == self.party) and (group in self.groups) and self.id not in endorsers:
                        # A newly added agent can't endorse the txn that adds itself.
                        if not delta.startswith('add-' + self.id):
                            endorsers.append(self.id)
                            endorsers.sort()
                            delta = '%s by {%s}/%s@%s' % (match.group(1), ','.join(endorsers), n, group)
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
        self.say('Broadcasting to agents I can reach.')
        targets = self.reachable
        if targets:
            for a in targets:
                a.receive(delta)

    def gossip(self, targets=None):
        """
        A.1: gossip           -- talk to any agents that A.1 can reach
        """
        if targets is None:
            targets = self.reachable
        if targets:
            def sync(s, t):
                for key in s.deltas:
                    for delta in s.deltas[key]:
                        if delta not in t.deltas[key]:
                            s.say('%s+%s--> %s' % (key, delta, t.id))
                            t.receive(key + '+' + delta)
            for t in targets:
                sync(self, t)
                sync(t, self)

    def autogossip(self):
        if random.random() < 0.05:
            target = random.choice(self.reachable)
            self.gossip([target])

    commands = ['simple', 'add', 'rem', 'state', 'gossip']