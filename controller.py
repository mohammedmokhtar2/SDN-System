from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.revent import *
from pox.lib.recoco import Timer
import json

log = core.getLogger()

class SDNProjectController(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        log.info("--- Smart Controller Started (Bidirectional) ---")
        self.current_path = "primary" 
        self.congestion_count = 0
        # Increased threshold to 5MB to avoid false alarms from random noise
        self.BYTES_THRESHOLD = 5000000 
        Timer(3, self._monitor_traffic, recurring=True)
        self.stats = {}

    def _handle_ConnectionUp(self, event):
        # 1. Allow ARP to Flood (So hosts can find each other)
        msg_arp = of.ofp_flow_mod()
        msg_arp.match.dl_type = 0x0806 
        msg_arp.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        event.connection.send(msg_arp)

        # 2. Install Primary Path (Both Directions)
        if self.current_path == "primary":
            self._install_primary_path(event.connection)

    def _install_primary_path(self, connection):
        dpid = dpid_to_str(connection.dpid)
        
        # --- RULE 1: Forward (H1 -> H2) ---
        msg_fwd = of.ofp_flow_mod()
        msg_fwd.match.dl_type = 0x0800
        msg_fwd.match.nw_src = "10.0.0.1"
        msg_fwd.match.nw_dst = "10.0.0.2"
        
        if dpid.endswith("01"): msg_fwd.actions.append(of.ofp_action_output(port = 2)) # S1->S2
        elif dpid.endswith("02"): msg_fwd.actions.append(of.ofp_action_output(port = 3)) # S2->S3
        elif dpid.endswith("03"): msg_fwd.actions.append(of.ofp_action_output(port = 3)) # S3->S6
        elif dpid.endswith("06"): msg_fwd.actions.append(of.ofp_action_output(port = 1)) # S6->H2
        connection.send(msg_fwd)

        # --- RULE 2: Reverse (H2 -> H1) ---
        msg_rev = of.ofp_flow_mod()
        msg_rev.match.dl_type = 0x0800
        msg_rev.match.nw_src = "10.0.0.2"
        msg_rev.match.nw_dst = "10.0.0.1"
        
        if dpid.endswith("06"): msg_rev.actions.append(of.ofp_action_output(port = 3)) # S6->S3
        elif dpid.endswith("03"): msg_rev.actions.append(of.ofp_action_output(port = 2)) # S3->S2
        elif dpid.endswith("02"): msg_rev.actions.append(of.ofp_action_output(port = 2)) # S2->S1
        elif dpid.endswith("01"): msg_rev.actions.append(of.ofp_action_output(port = 1)) # S1->H1
        connection.send(msg_rev)

    def _install_alternate_path(self):
        log.info("!!! REROUTING TRAFFIC TO ALTERNATE PATH !!!")
        for connection in core.openflow.connections:
            dpid = dpid_to_str(connection.dpid)
            
            # --- RULE 1: Forward (H1 -> H2) ---
            msg_fwd = of.ofp_flow_mod()
            msg_fwd.match.dl_type = 0x0800
            msg_fwd.match.nw_src = "10.0.0.1"
            msg_fwd.match.nw_dst = "10.0.0.2"
            
            if dpid.endswith("01"): msg_fwd.actions.append(of.ofp_action_output(port = 3)) # S1->S4
            elif dpid.endswith("04"): msg_fwd.actions.append(of.ofp_action_output(port = 4)) # S4->S6
            elif dpid.endswith("06"): msg_fwd.actions.append(of.ofp_action_output(port = 1)) # S6->H2
            connection.send(msg_fwd)

            # --- RULE 2: Reverse (H2 -> H1) ---
            msg_rev = of.ofp_flow_mod()
            msg_rev.match.dl_type = 0x0800
            msg_rev.match.nw_src = "10.0.0.2"
            msg_rev.match.nw_dst = "10.0.0.1"
            
            if dpid.endswith("06"): msg_rev.actions.append(of.ofp_action_output(port = 4)) # S6->S4
            elif dpid.endswith("04"): msg_rev.actions.append(of.ofp_action_output(port = 2)) # S4->S1
            elif dpid.endswith("01"): msg_rev.actions.append(of.ofp_action_output(port = 1)) # S1->H1
            connection.send(msg_rev)

    def _monitor_traffic(self):
        for connection in core.openflow.connections:
            connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

    def _handle_PortStatsReceived(self, event):
        dpid = dpid_to_str(event.connection.dpid)
        for stat in event.stats:
            if dpid not in self.stats: self.stats[dpid] = {}
            self.stats[dpid][stat.port_no] = stat.tx_bytes + stat.rx_bytes

            # CONGESTION LOGIC
            if dpid.endswith("02") and stat.port_no == 3:
                if stat.tx_bytes > self.BYTES_THRESHOLD and self.current_path == "primary":
                    self.congestion_count += 1
                    log.info(f"Congestion on S2->S3 (Bytes: {stat.tx_bytes}) Count: {self.congestion_count}")
                    if self.congestion_count >= 2:
                        self._install_alternate_path()
                        self.current_path = "alternate"
        try:
            with open('/home/mokhtar/sdn_project/stats.json', 'w') as f:
                json.dump(self.stats, f)
        except: pass

def launch():
    core.registerNew(SDNProjectController)
