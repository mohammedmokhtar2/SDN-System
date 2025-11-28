from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel

class SDNProjectTopo(Topo):
    "Project Topology: 6 Switches, 6 Hosts, Multiple Paths"

    def build(self):
        # 1. Create Switches (S1 to S6)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        # 2. Create Hosts (H1 to H6)
        # We set IP addresses explicitly to match the project PDF
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')
        h5 = self.addHost('h5', ip='10.0.0.5')
        h6 = self.addHost('h6', ip='10.0.0.6')

        # 3. Connect Hosts to Switches (Access Layer)
        self.addLink(h1, s1)
        self.addLink(h3, s2)
        self.addLink(h5, s3)
        self.addLink(h4, s4)
        # Note: H2 and H6 both connect to S6 based on the diagram structure
        self.addLink(h2, s6) 
        self.addLink(h6, s6)

        # 4. Create Internal Links (The Core Network)
        # Primary Path: S1 -> S2 -> S3 -> S6
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s6)

        # Alternate Path 1: S1 -> S4 -> S5 -> S6
        self.addLink(s1, s4)
        self.addLink(s4, s5)
        self.addLink(s5, s6)

        # Alternate Path 2: S4 -> S6 (Direct link for redundancy)
        self.addLink(s4, s6)

def run_topology():
    # Initialize the topology
    topo = SDNProjectTopo()
    
    # Create the network with a REMOTE controller (POX)
    # autoSetMacs=True makes IP 10.0.0.1 have MAC 00:00:00:00:00:01 (Easier debugging)
    net = Mininet(topo=topo, controller=None, autoSetMacs=True)
    
    # Add the controller (Connecting to your POX script running on port 6633)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Start the network
    net.start()
    print("*** Network Started. Testing Connectivity...")
    
    # Open the Mininet CLI so you can type commands like 'h1 ping h2'
    CLI(net)
    
    # Stop the network when you exit
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_topology()
