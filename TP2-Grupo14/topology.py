# -*- coding: utf-8 -*-
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import sys
from mininet.node import RemoteController


class LinearMultipleSwitchesTopo(Topo):
    def build(self, n_switches):

        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:10')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:20')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:30')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:40')

        switches = []
        for i in range(n_switches):
            # Format DPID as a 16-character hex string, starting at 1
            dpid = format(i + 1, '016x')
            switch = self.addSwitch('s{}'.format(i), dpid=dpid)
            switches.append(switch)

        self.addLink(h1, switches[0])
        self.addLink(h2, switches[0])
        self.addLink(h3, switches[-1])
        self.addLink(h4, switches[-1])

        for i in range(1, n_switches):
            self.addLink(switches[i-1], switches[i])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: sudo python topology.py <n_switches>")
        sys.exit(1)

    n_switches = int(sys.argv[1])

    setLogLevel('info')
    net = Mininet(
        topo=LinearMultipleSwitchesTopo(n_switches=n_switches),
        controller=lambda name:
        RemoteController(name, ip='127.0.0.1', port=6633)
        )
    net.start()
    CLI(net)
    net.stop()
