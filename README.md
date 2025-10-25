# SDN Campus Firewall

This project implements a software-defined firewall and a custom multi-switch campus topology using POX and Mininet. The design separates different LANs (Student Housing, Faculty, IT Dept) and enforces controlled communication rules between them at Layer 2 / Layer 3 using OpenFlow.

## Overview
The system has two main pieces:
1. A POX controller (`mlache-lab6_controller.py`) that programs OpenFlow switches with firewall behavior.
2. A Mininet topology (`mlache-lab6_topo.py`) that builds a small campus-style network with multiple switches and hosts.

The controller decides which traffic is allowed to move between LANs and which is blocked. The topology script wires all hosts through a shared core switch.

This models how a campus network can centrally enforce policy instead of relying on each individual switch.

## Topology
The topology script creates:
- A core switch
- Access switches for each LAN (Student Housing, Faculty, IT Department)
- Multiple hosts per LAN, each on its own subnet

All access switches connect “northbound” to the single core switch. Cross-LAN traffic has to pass the core, so the firewall only needs to run in one place to control everything.

Example layout:
- Student Housing LAN → switch S2
- Faculty LAN → switch S3
- IT Department LAN → switch S4
- Core switch → S1 (acts as the choke point)

Each access switch uplinks to a dedicated port on the core:
- S2 ↔ core port 2
- S3 ↔ core port 3
- S4 ↔ core port 4

So any packet from Student Housing to Faculty must cross Student→Core→Faculty, where the controller can decide if it should be forwarded or dropped.

## Firewall Policy
The firewall logic is implemented in the controller and pushed to switches using OpenFlow rules. The important policy for this lab:

- ICMP (ping):
  - Allowed within the same subnet.
  - Allowed between Student Housing, Faculty, and IT Department.
  - Blocked for anything outside those allowed paths.
  - This means you can still test reachability with ping across the “approved” departments, but you don’t accidentally expose everything.

- TCP / UDP:
  - Only allowed on explicitly permitted paths.
  - All other inter-LAN TCP/UDP traffic is blocked by default.

- ARP:
  - ARP is forwarded so hosts can learn MAC addresses. Without this, nothing would work.

Behavior:
- Default stance is basically “deny unless allowed.”
- Approved communication gets an explicit flow rule.
- Disallowed communication never gets a forwarding rule, which means it dies at the switch.

## Controller Behavior
`mlache-lab6_controller.py`:
- Listens for `PacketIn` events from switches.
- Checks src subnet, dst subnet, and protocol (ICMP/TCP/UDP/ARP).
- Decides to:
  - install a flow that forwards the packet, or
  - drop it by not installing forwarding.
- Uses port mappings between switches so packets get forwarded out the correct interface toward the destination LAN via the core.

It also sets reasonable OpenFlow timeouts on rules so stale rules age out:
- `idle_timeout` so inactive flows expire
- `hard_timeout` to force cleanup

This stops the switches from filling up with old rules during testing.

## Topology Script Behavior
`mlache-lab6_topo.py`:
- Defines each host with an IP address in the correct subnet (ex: Student LAN is one subnet, Faculty LAN is another).
- Connects each host to the correct access switch.
- Connects each access switch to the core switch on a specific port so routing through the core is deterministic and testable.
- Launches the network in Mininet for direct testing with `ping`, `iperf`, and traceroute.

This guarantees that all inter-department communication passes through the policy chokepoint.

