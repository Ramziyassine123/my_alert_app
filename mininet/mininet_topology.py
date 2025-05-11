from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel


def run():
    # Set log level to info
    setLogLevel('info')

    # Create the Mininet network
    net = Mininet()

    # Add a host and a switch
    h1 = net.addHost('h1', ip='10.0.0.1')
    s1 = net.addSwitch('s1')

    # Connect the host to the switch
    net.addLink(h1, s1)

    # Start the network
    net.start()

    # Start the Django server on the host
    h1.cmd('python3 /path/to/your/manage.py runserver 0.0.0.0:8000 &')  # Update this path

    # Open a CLI for interaction
    CLI(net)

    # Stop the network
    net.stop()


if __name__ == '__main__':
    run()
