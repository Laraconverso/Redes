from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel


class LinearLossTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        self.addLink(h1, s1)
        self.addLink(s1, s2, loss=10)
        self.addLink(h2, s2)


if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=LinearLossTopo())
    net.start()
    CLI(net)
    net.stop()
