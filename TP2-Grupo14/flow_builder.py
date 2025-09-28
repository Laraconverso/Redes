import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
import pox.lib.packet as pkt


class FlowBuilder:
    @staticmethod
    def build_blocking_flow(rule):
        """
        Build a blocking flow message from a rule.

        Args:
            rule: Dictionary containing rule criteria

        Returns:
            of.ofp_flow_mod: OpenFlow flow modification message
        """
        match = FlowBuilder.build_match(rule)

        msg = of.ofp_flow_mod()
        msg.match = match
        # No actions = drop the packet
        msg.priority = 100
        return msg

    @staticmethod
    def build_match(rule):
        """
        Build match criteria from rule.

        Args:
            rule: Dictionary containing rule criteria

        Returns:
            of.ofp_match: OpenFlow match object
        """
        match = of.ofp_match()

        # IP type
        if rule.get('ip_tipo') == 'ipv6':
            match.dl_type = pkt.ethernet.IPV6_TYPE
        else:
            match.dl_type = pkt.ethernet.IP_TYPE

        # Protocol
        if rule.get('protocolo') == 'udp':
            match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        elif rule.get('protocolo') == 'tcp':
            match.nw_proto = pkt.ipv4.TCP_PROTOCOL
        elif 'puerto_origen' in rule or 'puerto_destino' in rule:
            match.nw_proto = pkt.ipv4.TCP_PROTOCOL

        # IP addresses
        if 'ip_origen' in rule:
            match.nw_src = IPAddr(rule['ip_origen'])
        if 'ip_destino' in rule:
            match.nw_dst = IPAddr(rule['ip_destino'])

        # Ports
        if match.nw_proto in [pkt.ipv4.TCP_PROTOCOL, pkt.ipv4.UDP_PROTOCOL]:
            if 'puerto_origen' in rule:
                match.tp_src = rule['puerto_origen']
            if 'puerto_destino' in rule:
                match.tp_dst = rule['puerto_destino']

        # MAC addresses
        if 'mac_origen' in rule:
            match.dl_src = EthAddr(rule['mac_origen'])
        if 'mac_destino' in rule:
            match.dl_dst = EthAddr(rule['mac_destino'])

        return match
