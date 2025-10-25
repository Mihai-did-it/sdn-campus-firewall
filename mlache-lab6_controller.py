#Mihai Lache
#CSR150 /// PARSA
##citations: Chat gpt debugging and understadning problem
# looked at stack overflow for IPNetwork library






from pox.core import core
import pox.openflow.libopenflow_01 as of
from netaddr import IPNetwork




log = core.getLogger()




class Routing (object):
 


  def __init__(self, connection):
      self.connection = connection
      connection.addListeners(self)
      self.arp_table = {}  # Store ARP mappings






  def _handle_PacketIn(self, event):
      packet = event.parsed
           #get the packets type
      self.do_routing(packet, event.ofp, event.port, event.dpid)




  def do_routing(self, packet, packet_in, port_on_switch, switch_id):
   # this is the logic called for each packet


   #ARP first
   #[ping] cant work without handlign ARP aswell
   #im assuming that the rule 1 allows for arp handling (otherwise it wont ever reach prot
   if packet.type == packet.ARP_TYPE:
       self.process_arp(packet, packet_in, port_on_switch)
       return
    # done with ARP


   #


   elif packet.type == packet.IP_TYPE:
       ip_packet = packet.find("ipv4")
       if ip_packet:
           if ip_packet.protocol == ip_packet.ICMP_PROTOCOL:
               self.handle_icmp(packet, packet_in, ip_packet, switch_id)


           elif ip_packet.protocol == ip_packet.TCP_PROTOCOL:
               self.handle_tcp(packet, packet_in, ip_packet, switch_id)


           elif ip_packet.protocol == ip_packet.UDP_PROTOCOL:
               self.handle_udp(packet, packet_in, ip_packet, switch_id)
       return


   # not handling it here)
   self.drop(packet, packet_in)




# ARP packet.---- MAC addresses
  def process_arp(self, packet, packet_in, port_on_switch):
   arp_packet = packet.find('arp')
   src_ip = str(arp_packet.protosrc)
   src_mac = str(packet.src)
  


   self.arp_table[src_ip] = (src_mac, port_on_switch)


   if arp_packet.opcode == arp_packet.REQUEST:


       self.accept(packet_in, of.OFPP_FLOOD)




   elif arp_packet.opcode == arp_packet.REPLY:
       # get it to the right port




       dst_ip = str(arp_packet.protodst)
       if dst_ip in self.arp_table:


           _, dst_port = self.arp_table[dst_ip]
           self.accept(packet_in, dst_port)




       else:
           # just flood it ---- destinations unknown here
           self.accept(packet_in, of.OFPP_FLOOD)




# ICMP traffic handler ----- PINGER
  def handle_icmp(self, packet, packet_in, ip_packet, switch_id):
   src_ip, dst_ip = str(ip_packet.srcip), str(ip_packet.dstip)


   faculty_lan = IPNetwork("10.0.1.0/24")
   student_housing_lan = IPNetwork("10.0.2.0/24")
   it_department_lan = IPNetwork("10.40.3.0/24")


   if (
       any(src_ip in subnet and dst_ip in subnet for subnet in [faculty_lan, student_housing_lan, it_department_lan]) or
       (src_ip in faculty_lan and dst_ip in student_housing_lan) or
       (src_ip in student_housing_lan and dst_ip in faculty_lan) or
       (src_ip in faculty_lan and dst_ip in it_department_lan) or
       (src_ip in it_department_lan and dst_ip in faculty_lan) or
       (src_ip in student_housing_lan and dst_ip in it_department_lan) or
       (src_ip in it_department_lan and dst_ip in student_housing_lan)
   ):
       end_port = self.get_output_port(dst_ip, switch_id)
       if end_port is not None:
           self.add_flow(packet, packet_in, end_port)
           self.accept(packet_in, end_port)
       else:
           self.drop(packet, packet_in)
         
   else:
       self.drop(packet, packet_in)
      




  def handle_tcp(self, packet, packet_in, ip_packet, switch_id):
   src_ip, dst_ip = str(ip_packet.srcip), str(ip_packet.dstip)
   log.info(f"[tcp-routing] TCP from {src_ip} to {dst_ip}")
  
   if not self.rule_2_tcp_handler(packet, packet_in, src_ip, dst_ip, switch_id):
       log.info(f"[rule-check] TCP dropped: {src_ip} to {dst_ip}")




# UDP traffic handler
  def handle_udp(self, packet, packet_in, ip_packet, switch_id):
   src_ip, dst_ip = str(ip_packet.srcip), str(ip_packet.dstip)
   log.info(f"[udp-route  UDP from {src_ip} to {dst_ip}")
  
   if not self.rule_3_udp_handler(packet, packet_in, src_ip, dst_ip, switch_id):
       log.info(f"UDP dropped: {src_ip} to {dst_ip}")




















  def rule_2_tcp_handler(self, packet, packet_in, src_ip, dst_ip, switch_id):
   # allowed subnets here
   faculty_subnet = IPNetwork("10.0.1.0/24")
   student_housing_subnet = IPNetwork("10.0.2.0/24")
   it_department_subnet = IPNetwork("10.40.3.0/24")
   data_center_subnet = IPNetwork("10.100.100.0/24")
  
   #hardcode (u)
   if (src_ip == "10.0.203.6" and dst_ip == "10.40.3.254") or (src_ip == "10.40.3.254" and dst_ip == "10.0.203.6"):
       destination_port = self.get_output_port(dst_ip, switch_id)
      
       if destination_port is not None:
           self.add_flow(packet, packet_in, destination_port)
           self.accept(packet_in, destination_port)
           return True
       else:
           self.drop(packet, packet_in)
           return False


   # tuple for allowed connections
   allowed_inter_subnet_pairs = [
       (faculty_subnet, student_housing_subnet),
       (student_housing_subnet, faculty_subnet),
       (faculty_subnet, it_department_subnet),
       (it_department_subnet, faculty_subnet),
       (student_housing_subnet, it_department_subnet),
       (it_department_subnet, student_housing_subnet),
       (faculty_subnet, data_center_subnet)  # faculty can access data center, but with restrictions
   ]


   # first check if the -y in the same subnet
   same_subnet = False
   for subnet in [faculty_subnet, student_housing_subnet, it_department_subnet, data_center_subnet]:
       if src_ip in subnet and dst_ip in subnet:
           same_subnet = True
           break


   # if source and destination ips are part of an allowed inter pair
   inter_subnet_allowed = False
   for src_subnet, dst_subnet in allowed_inter_subnet_pairs:
       if src_ip in src_subnet and dst_ip in dst_subnet:
           if src_subnet == faculty_subnet and dst_subnet == data_center_subnet:
               # only for Faculty subnet
               if dst_ip == "10.100.100.2":
                   inter_subnet_allowed = True
                   break
           else:
               inter_subnet_allowed = True
               break


   #check based on the subnet checks
   if same_subnet or inter_subnet_allowed:
       # find the output port for the destination ip
       destination_port = self.get_output_port(dst_ip, switch_id)
      
       if destination_port is not None:
           #flow for accepted packet
           self.add_flow(packet, packet_in, destination_port)
           self.accept(packet_in, destination_port)
           return True
       else:


           self.drop(packet, packet_in)
           return False
   else:
       self.drop(packet, packet_in)
       return False


  






  def rule_3_udp_handler(self, packet, packet_in, src_ip, dst_ip, switch_id):
   #  the allowed subnets
   faculty_lan = IPNetwork("10.0.1.0/24")
   student_housing_lan = IPNetwork("10.0.2.0/24")
   it_department_lan = IPNetwork("10.40.3.0/24")
   data_center_lan = IPNetwork("10.100.100.0/24")


   # are allowed for crosssubnet
   allowed_pairs = [
       (faculty_lan, student_housing_lan),
       (student_housing_lan, faculty_lan),
       (faculty_lan, it_department_lan),
       (it_department_lan, faculty_lan),
       (student_housing_lan, it_department_lan),
       (it_department_lan, student_housing_lan),
       (data_center_lan, it_department_lan),
       (it_department_lan, data_center_lan)
   ]


   # source and destination are within the same subnet
   same_subnet = any(src_ip in subnet and dst_ip in subnet for subnet in [faculty_lan, student_housing_lan, it_department_lan, data_center_lan])


   #  source and destination are in an allowed crossing the subnet pair
   cross_subnet = any(src_ip in src_subnet and dst_ip in dst_subnet for src_subnet, dst_subnet in allowed_pairs)


   if same_subnet or cross_subnet:
       end_port = self.get_output_port(dst_ip, switch_id)
       if end_port is not None:
           self.add_flow(packet, packet_in, end_port)
           self.accept(packet_in, end_port)
           return True
       else:
           self.drop(packet, packet_in)
           return False
   else:
       self.drop(packet, packet_in)
       return False








  def add_flow(self, packet, packet_in, out_port):
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet, packet_in.in_port)
      msg.actions.append(of.ofp_action_output(port=out_port))
      self.connection.send(msg)




  def accept(self, packet_in, out_port):
   msg = of.ofp_packet_out()
   msg.data = packet_in
   msg.actions.append(of.ofp_action_output(port=out_port))
   self.connection.send(msg)






  def drop(self, packet, packet_in):
      msg = of.ofp_packet_out()
      msg.data = packet_in
      self.connection.send(msg)
     




  def get_output_port(self, dst_ip, switch_id):
    switch_port_map = {
       "core": {
           2: ["10.0.1.2", "10.0.1.4", "10.0.1.3"],
           3: ["10.0.2.2", "10.0.2.40", "10.0.2.3"], 
           4: ["10.40.3.30", "10.40.3.254"],           
           5: ["10.100.100.2", "10.100.100.20", "10.100.100.56"], 
           6: ["10.0.203.6"],                            
           7: ["10.0.198.6"],                            
           8: ["10.0.198.10"]                          
       },
       "faculty_switch": {
           1: ["10.0.1.2"],                              
           3: ["10.0.1.4"],                             
           4: ["10.0.1.3"],                             
           2: ["10.0.2.2", "10.0.2.40", "10.0.2.3", "10.40.3.30", "10.40.3.254",
               "10.100.100.2", "10.100.100.20", "10.100.100.56", "10.0.203.6",
               "10.0.198.6", "10.0.198.10"]              
       },
       "student_switch": {
           1: ["10.0.2.2"],                             
           2: ["10.0.2.40"],                            
           4: ["10.0.2.3"],                             
           3: ["10.0.1.2", "10.0.1.4", "10.0.1.3", "10.40.3.30", "10.40.3.254",
               "10.100.100.2", "10.100.100.20", "10.100.100.56", "10.0.203.6",
               "10.0.198.6", "10.0.198.10"]              
       },
       "it_switch": {
           1: ["10.40.3.30"],            
           2: ["10.40.3.254"],      
           4: ["10.0.1.2", "10.0.1.4", "10.0.1.3", "10.0.2.2", "10.0.2.40",
               "10.0.2.3", "10.100.100.2", "10.100.100.20", "10.100.100.56",
               "10.0.203.6", "10.0.198.6", "10.0.198.10"]
       },
       "data_center_switch": {
           1: ["10.100.100.2"],                          
           2: ["10.100.100.20"],                      
           3: ["10.100.100.56"],                         
           5: ["10.0.1.2", "10.0.1.4", "10.0.1.3", "10.0.2.2", "10.0.2.40",
               "10.0.2.3", "10.40.3.30", "10.40.3.254", "10.0.203.6",
               "10.0.198.6", "10.0.198.10"]            
       }
   }


 
   switch_name_map = {
       1: "core",
       2: "faculty_switch",
       3: "student_switch",
       4: "it_switch",
       5: "data_center_switch"
   }




   switch_name = switch_name_map.get(switch_id)
   if switch_name and switch_name in switch_port_map:
       for port, ip_list in switch_port_map[switch_name].items():
           if dst_ip in ip_list:
               return port
   return None






def launch():
  def start_switch(event):
      log.info(f"[launch] Starting switch connection for {event.connection}")
      Routing (event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)










