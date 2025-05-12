from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel


class MyTopo(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1')
        s1 = self.addSwitch('s1')

        self.addLink(h1, s1)


def run():
    topo = MyTopo()
    net = Mininet(topo=topo)

    # Start the network
    net.start()

    # Open a CLI for interaction
    CLI(net)

    # Stop the network
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
