#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController




class MyTopology(Topo):
  def __init__(self):
      Topo.__init__(self)




      # core
      s1 = self.addSwitch('s1')




      # faculty LAN
      s2 = self.addSwitch('s2')
      facultyWS = self.addHost('facultyWS', ip='10.0.1.2/24', mac='00:00:00:00:01:02', defaultRoute="facultyWS-eth1")
      facultyPC = self.addHost('facultyPC', ip='10.0.1.4/24', mac='00:00:00:00:01:04', defaultRoute="facultyPC-eth1")
      printer = self.addHost('printer', ip='10.0.1.3/24', mac='00:00:00:00:01:03', defaultRoute="printer-eth1")




      #student Housing LAN
      s3 = self.addSwitch('s3')
      studentPC1 = self.addHost('studentPC1', ip='10.0.2.2/24', mac='00:00:00:00:02:02', defaultRoute="studentPC1-eth1")
      studentPC2 = self.addHost('studentPC2', ip='10.0.2.40/24', mac='00:00:00:00:02:28', defaultRoute="studentPC2-eth1")
      labWS = self.addHost('labWS', ip='10.0.2.3/24', mac='00:00:00:00:02:03', defaultRoute="labWS-eth1")




      # IT department LAN
      s4 = self.addSwitch('s4')
      itWS = self.addHost('itWS', ip='10.40.3.30/24', mac='00:00:00:00:03:1E', defaultRoute="itWS-eth1")
      itPC = self.addHost('itPC', ip='10.40.3.254/24', mac='00:00:00:00:03:FE', defaultRoute="itPC-eth1")




      # University data Center
      s5 = self.addSwitch('s5')
      examServer = self.addHost('examServer', ip='10.100.100.2/24', mac='00:00:00:00:05:02', defaultRoute="examServer-eth1")
      webServer = self.addHost('webServer', ip='10.100.100.20/24', mac='00:00:00:00:05:14', defaultRoute="webServer-eth1")
      dnsServer = self.addHost('dnsServer', ip='10.100.100.56/24', mac='00:00:00:00:05:38', defaultRoute="dnsServer-eth1")




      #Internet
      trustedPC = self.addHost('trustedPC', ip='10.0.203.6/32', mac='00:00:00:00:3F:3F', defaultRoute="trustedPC-eth1")
      guest1 = self.addHost('guest1', ip='10.0.198.6/32', mac='00:00:00:00:C6:06', defaultRoute="guest1-eth1")
      guest2 = self.addHost('guest2', ip='10.0.198.10/32', mac='00:00:00:00:C6:0A', defaultRoute="guest2-eth1")




      #links for Faculty LAN
      self.addLink(facultyWS, s2, port1=1, port2=1)
      self.addLink(facultyPC, s2, port1=1, port2=3)
      self.addLink(printer, s2, port1=1, port2=4)
      self.addLink(s2, s1, port1=2, port2=2)  # Faculty LAN to Core Switch




      # links for  Student Housing LAN
      self.addLink(studentPC1, s3, port1=1, port2=1)
      self.addLink(studentPC2, s3, port1=1, port2=2)
      self.addLink(labWS, s3, port1=1, port2=4)
      self.addLink(s3, s1, port1=3, port2=3)  # Student Housing LAN to Core Switch




      # links for IT Department LAN
      self.addLink(itWS, s4, port1=1, port2=1)
      self.addLink(itPC, s4, port1=1, port2=2)
      self.addLink(s4, s1, port1=4, port2=4)  # IT Department LAN to Core Switch




      #linksn forUDC
      self.addLink(examServer, s5, port1=1, port2=1)
      self.addLink(webServer, s5, port1=1, port2=2)
      self.addLink(dnsServer, s5, port1=1, port2=3)
      self.addLink(s5, s1, port1=5, port2=5)  # Data Center to Core Switch




      #internet going straight to switch
      self.addLink(trustedPC, s1, port1=1, port2=6)
      self.addLink(guest1, s1, port1=1, port2=7)
      self.addLink(guest2, s1, port1=1, port2=8)




if __name__ == '__main__':
  topo = MyTopology()
  c0 = RemoteController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633)
  net = Mininet(topo=topo, controller=c0)
  #net = Mininet(topo=topo) ///////testing
  net.start()
  CLI(net)
  net.stop()








