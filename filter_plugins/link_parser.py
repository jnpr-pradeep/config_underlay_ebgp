
ASN_CONFIG = """
delete groups ebgp_grp
delete apply-groups ebgp_grp
set apply-groups ebgp_grp
set groups ebgp_grp protocols bgp group IPCLOS_eBGP local-as {asn}
"""

PEER_CONFIG = """
set groups ebgp_grp protocols bgp group IPCLOS_eBGP neighbor {peer_ip} description "{peer_device_name}"
set groups ebgp_grp protocols bgp group IPCLOS_eBGP neighbor {peer_ip} peer-as {peer_asn}
"""

IFC_CONFIG = """
set groups ebgp_grp interfaces {ifc_name} unit 0 family inet address {ifc_ip}
"""

COMMON_EBGP_CONFIG = """
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_EXP term loopback from protocol direct
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_EXP term loopback from protocol bgp
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_EXP term loopback then accept
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_EXP term default then reject
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_IMP term loopback from protocol bgp
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_IMP term loopback from protocol direct
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_IMP term loopback then accept
set groups ebgp_grp policy-options policy-statement IPCLOS_BGP_IMP term default then reject

set groups ebgp_grp protocols bgp group IPCLOS_eBGP type external
set groups ebgp_grp protocols bgp group IPCLOS_eBGP mtu-discovery
set groups ebgp_grp protocols bgp group IPCLOS_eBGP import IPCLOS_BGP_IMP
set groups ebgp_grp protocols bgp group IPCLOS_eBGP export IPCLOS_BGP_EXP
set groups ebgp_grp protocols bgp group IPCLOS_eBGP multipath multiple-as
set groups ebgp_grp protocols bgp group IPCLOS_eBGP bfd-liveness-detection minimum-interval 350
set groups ebgp_grp protocols bgp group IPCLOS_eBGP bfd-liveness-detection multiplier 3
set groups ebgp_grp protocols bgp group IPCLOS_eBGP bfd-liveness-detection session-mode automatic
set groups ebgp_grp protocols bgp group IPCLOS_eBGP vpn-apply-export
set groups ebgp_grp protocols bgp log-updown
set groups ebgp_grp protocols bgp graceful-restart
"""

device_2_asn_map = {}
device_config = {}


class FilterModule(object):
    def filters(self):
        return {
            'parse_links':
                self.parse_links
        }
    # end filters

    @staticmethod
    def _generate_device_link_config(local_dict, peer_dict):
        peer_config = PEER_CONFIG.format(peer_ip=str(peer_dict[
                                                         'ifc_ip']).split(
            "/")[0],
                                         peer_device_name=peer_dict['device'],
                                         peer_asn=
                                         device_2_asn_map[peer_dict['device']])
        ifc_config = IFC_CONFIG.format(ifc_name=str(local_dict[
                                                        'ifc_name']),
                                       ifc_ip=str(local_dict['ifc_ip']))

        return peer_config.strip() + "\n" + ifc_config.strip()

    def parse_links(self, links_details):

        if links_details:
            links = links_details['links']
            asns = links_details['asns']

            for asn_dict in asns:
                device = str(asn_dict['device'])
                asn = str(asn_dict['asn'])
                device_config[device] = ASN_CONFIG.format(asn=asn).strip() +\
                                        "\n" + COMMON_EBGP_CONFIG.strip()
                device_2_asn_map[device] = asn

            # print device_2_asn_map

            for link in links:
                from_dict = link['from']
                to_dict = link['to']
                from_device = str(from_dict['device'])
                to_device = str(to_dict['device'])

                from_config = self._generate_device_link_config(from_dict,
                                                             to_dict)
                to_config = self._generate_device_link_config(to_dict,
                                                             from_dict)

                device_config[to_device] = device_config[to_device] + \
                                           "\n" + to_config
                device_config[from_device] = device_config[from_device] + \
                                             "\n" + from_config
            return device_config
    # end parse_links
# end FilterModule

