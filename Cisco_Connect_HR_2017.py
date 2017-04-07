import logging
from ncclient import manager
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_ifmgr_cfg, Cisco_IOS_XR_ipv4_bgp_cfg, Cisco_IOS_XR_ipv4_bgp_datatypes
from ydk.models.openconfig.openconfig_interfaces import Interfaces as OpenConfig_Interfaces
from ydk.models.openconfig.openconfig_bgp import Bgp as OpenConfig_Bgp
from ydk.models.openconfig.openconfig_bgp_types import Ipv4UnicastIdentity as OpenConfig_Ipv4UnicastIdentity
from ydk.models.ietf.iana_if_type import SoftwareloopbackIdentity
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_ipv4_bgp_datatypes as xr_ipv4_bgp_datatypes
from ydk.services.crud_service import CRUDService
from ydk.providers.netconf_provider import NetconfServiceProvider
import ydk.types
from  ydk.models.ietf.ietf_interfaces import InterfaceTypeIdentity
############################################################################
class dvulovic_NETCONF_Device:

    def __init__(self, host, port, username, password):

        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.m = manager.connect(host=self.host, port=self.port, username=self.username, password=self.password, hostkey_verify=False)

        self.ydk_provider = NetconfServiceProvider(address=self.host, port=self.port, username=self.username, password=self.password, protocol='ssh')

        self.ydk_crud = CRUDService()

class dvulovic_IOSXR(dvulovic_NETCONF_Device):

    def __init__(self, host, port, username, password):

        dvulovic_NETCONF_Device.__init__(self, host, port, username, password)

    def get_running_config(self, filter_string=None):
        if (filter_string is None):
            return self.m.get_config(source='running').data_xml
        else:
            return self.m.get_config(source='running',filter=filter_string).data_xml
############################################################################
class dvulovic_Generic_IOSXR_Model:

    def __init__(self, xr_device):
            self.xr = xr_device
############################################################################
class dvulovic_Native_IOSXR_Model_YDK(dvulovic_Generic_IOSXR_Model):

    def __init__(self, xr_device):
        dvulovic_Generic_IOSXR_Model.__init__(self, xr_device)

    def create_loopback(self, arg_loopbacknum, arg_ip, arg_mask):
        interface_configurations = Cisco_IOS_XR_ifmgr_cfg.InterfaceConfigurations()

        interface_configuration = interface_configurations.InterfaceConfiguration()

        interface_configuration.active = "act"
        interface_configuration.interface_name = "Loopback" + arg_loopbacknum
        interface_configuration.interface_virtual = ydk.types.Empty()

        primary_address = interface_configuration.ipv4_network.addresses.Primary()
        primary_address.address = arg_ip
        primary_address.netmask = arg_mask

        interface_configuration.ipv4_network.addresses.primary = primary_address

        interface_configurations.interface_configuration.append(interface_configuration)

        self.xr.ydk_crud.create(self.xr.ydk_provider, interface_configurations)

    def create_bgp_process(self, arg_asnum):
        bgp = Cisco_IOS_XR_ipv4_bgp_cfg.Bgp()

        instance = bgp.Instance()
        instance.instance_name = "default"

        instance_as = instance.InstanceAs()
        instance_as.as_ = 0

        instance_as_four_byte_as = instance_as.FourByteAs()
        instance_as_four_byte_as.bgp_running = ydk.types.Empty()
        instance_as_four_byte_as.as_ = arg_asnum
        instance_as.four_byte_as.append(instance_as_four_byte_as)

        instance.instance_as.append(instance_as)

        bgp.instance.append(instance)

        self.xr.ydk_crud.create(self.xr.ydk_provider, bgp)

    def add_bgp_neighbor(self, arg_asnumber, arg_neighbor_ip, arg_remote_as, arg_update_source = None):
        bgp = Cisco_IOS_XR_ipv4_bgp_cfg.Bgp()

        instance = bgp.Instance()
        instance.instance_name = "default"

        instance_as = instance.InstanceAs()
        instance_as.as_ = 0

        instance_as_four_byte_as = instance_as.FourByteAs()
        instance_as_four_byte_as.bgp_running = ydk.types.Empty()
        instance_as_four_byte_as.as_ = arg_asnumber

        neighbor = instance_as_four_byte_as.default_vrf.bgp_entity.neighbors.Neighbor()
        neighbor.neighbor_address = arg_neighbor_ip
        neighbor.remote_as.as_xx = 0
        neighbor.remote_as.as_yy = arg_remote_as
        if(arg_update_source):
            neighbor.update_source_interface = arg_update_source

        instance_as_four_byte_as.default_vrf.bgp_entity.neighbors.neighbor.append(neighbor)

        instance_as.four_byte_as.append(instance_as_four_byte_as)

        instance.instance_as.append(instance_as)

        bgp.instance.append(instance)

        self.xr.ydk_crud.create(self.xr.ydk_provider, bgp)

    def add_ipv4_unicast_SAFI_to_bgp_neighbor(self, arg_asnumber, arg_neighbor_ip):
        bgp = Cisco_IOS_XR_ipv4_bgp_cfg.Bgp()

        instance = bgp.Instance()
        instance.instance_name = "default"

        instance_as = instance.InstanceAs()
        instance_as.as_ = 0

        instance_as_four_byte_as = instance_as.FourByteAs()
        instance_as_four_byte_as.bgp_running = ydk.types.Empty()
        instance_as_four_byte_as.as_ = arg_asnumber

        neighbor = instance_as_four_byte_as.default_vrf.bgp_entity.neighbors.Neighbor()
        neighbor.neighbor_address = arg_neighbor_ip

        neighbor_af = neighbor.neighbor_afs.NeighborAf()
        neighbor_af.af_name = Cisco_IOS_XR_ipv4_bgp_datatypes.BgpAddressFamilyEnum.ipv4_unicast
        neighbor_af.activate = ydk.types.Empty()
        neighbor.neighbor_afs.neighbor_af.append(neighbor_af)

        instance_as_four_byte_as.default_vrf.bgp_entity.neighbors.neighbor.append(neighbor)

        instance_as.four_byte_as.append(instance_as_four_byte_as)

        instance.instance_as.append(instance_as)

        bgp.instance.append(instance)

        self.xr.ydk_crud.create(self.xr.ydk_provider, bgp)

    def add_bgp_ipv4_unicast_network(self, arg_asnum, arg_ip, arg_prefixlen):
        bgp = Cisco_IOS_XR_ipv4_bgp_cfg.Bgp()

        instance = bgp.Instance()
        instance.instance_name = "default"

        instance_as = instance.InstanceAs()
        instance_as.as_ = 0

        instance_as_four_byte_as = instance_as.FourByteAs()
        instance_as_four_byte_as.bgp_running = ydk.types.Empty()
        instance_as_four_byte_as.as_ = arg_asnum

        global_af = instance_as_four_byte_as.default_vrf.global_.global_afs.GlobalAf()
        global_af.af_name = xr_ipv4_bgp_datatypes.BgpAddressFamilyEnum.ipv4_unicast
        global_af.enable = ydk.types.Empty()

        sourced_network = global_af.sourced_networks.SourcedNetwork()
        sourced_network.network_addr = arg_ip
        sourced_network.network_prefix = arg_prefixlen

        global_af.sourced_networks.sourced_network.append(sourced_network)

        instance_as_four_byte_as.default_vrf.global_.global_afs.global_af.append(global_af)

        instance_as.four_byte_as.append(instance_as_four_byte_as)

        instance.instance_as.append(instance_as)

        bgp.instance.append(instance)

        self.xr.ydk_crud.create(self.xr.ydk_provider, bgp)

############################################################################
class dvulovic_OpenConfig_IOSXR_Model_YDK(dvulovic_Generic_IOSXR_Model):

    def __init__(self, xr_device):
        dvulovic_Generic_IOSXR_Model.__init__(self, xr_device)

    def create_loopback(self, arg_loopbacknum, arg_ip, arg_prefixlen):
            oc_interface = OpenConfig_Interfaces.Interface()

            oc_interface.name = "Loopback" + arg_loopbacknum
            oc_interface.config.name = "Loopback" + arg_loopbacknum
            oc_interface.config.type = SoftwareloopbackIdentity()
            oc_interface.config.enabled = True

            oc_subinterface = oc_interface.subinterfaces.Subinterface()
            oc_subinterface.index = 0

            oc_subinterface_ipv4 = oc_subinterface.Ipv4()

            oc_subinterface_ipv4_address = oc_subinterface_ipv4.Address()
            oc_subinterface_ipv4_address.ip = arg_ip
            oc_subinterface_ipv4_address.config.ip = arg_ip
            oc_subinterface_ipv4_address.config.prefix_length = arg_prefixlen
            oc_subinterface_ipv4.address.append(oc_subinterface_ipv4_address)

            oc_subinterface.ipv4 = oc_subinterface_ipv4

            oc_interface.subinterfaces.subinterface.append(oc_subinterface)

            self.xr.ydk_crud.create(self.xr.ydk_provider, oc_interface)

    def create_bgp_procces(self, arg_asnumber):

        oc_bgp = OpenConfig_Bgp()
        oc_bgp.global_.config.as_ = arg_asnumber

        self.xr.ydk_crud.create(self.xr.ydk_provider, oc_bgp)

    def add_bgp_neighbor(self, arg_asnumber, arg_neighbor_ip, arg_remote_as, arg_update_source = None):
        oc_bgp = OpenConfig_Bgp()

        oc_neighor = oc_bgp.neighbors.Neighbor()
        oc_neighor.neighbor_address = arg_neighbor_ip
        oc_neighor.config.neighbor_address = arg_neighbor_ip
        oc_neighor.config.peer_as = arg_remote_as

        if(arg_update_source):
            oc_neighor.transport.config.local_address = arg_update_source

        oc_bgp.neighbors.neighbor.append(oc_neighor)

        self.xr.ydk_crud.create(self.xr.ydk_provider, oc_bgp)

    def add_ipv4_unicast_SAFI_to_bgp_neighbor(self, arg_asnumber, arg_neighbor_ip):
        oc_bgp = OpenConfig_Bgp()

        oc_neighor = oc_bgp.neighbors.Neighbor()
        oc_neighor.neighbor_address = arg_neighbor_ip

        oc_safi = oc_neighor.afi_safis
        oc_safi = oc_neighor.afi_safis.AfiSafi()
        oc_safi.afi_safi_name = OpenConfig_Ipv4UnicastIdentity()
        oc_safi.config.enabled = True
        oc_safi.config.afi_safi_name = OpenConfig_Ipv4UnicastIdentity()

        oc_neighor.afi_safis.afi_safi.append(oc_safi)

        oc_bgp.neighbors.neighbor.append(oc_neighor)

        self.xr.ydk_crud.create(self.xr.ydk_provider, oc_bgp)
############################################################################
## Remove/comment this sectionif you do not want extensive logging
##
log = logging.getLogger('ydk')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
log.addHandler(ch)
##
############################################################################
r1 = dvulovic_IOSXR('198.18.1.11', 830, 'admin','admin')
xr_native_model_r1 = dvulovic_Native_IOSXR_Model_YDK(r1)

r2 = dvulovic_IOSXR('198.18.1.12', 830, 'admin','admin')
xr_oc_model_r2 = dvulovic_OpenConfig_IOSXR_Model_YDK(r2)
xr_native_model_r2 = dvulovic_Native_IOSXR_Model_YDK(r2)
############################################################################
# step 1 - create loopback interface
xr_native_model_r1.create_loopback("1111", "1.1.1.1", "255.255.255.0")
xr_oc_model_r2.create_loopback("2222","2.2.2.2", 24)

# step 2 - create BGP process
xr_native_model_r1.create_bgp_process(65000)
xr_oc_model_r2.create_bgp_procces(65000)

# step 3 - create bgp neighbor
xr_native_model_r1.add_bgp_neighbor(65000,"172.16.255.2",65000, "Loopback0")
xr_oc_model_r2.add_bgp_neighbor(65000,"172.16.255.1",65000,"Loopback0")

# step 4 - advertise network
xr_native_model_r1.add_bgp_ipv4_unicast_network(65000,"1.1.1.0",24)
xr_native_model_r2.add_bgp_ipv4_unicast_network(65000,"2.2.2.0",24)

# step 5 - add IPv4 Unicast SAFI to BGP neighbor
xr_native_model_r1.add_ipv4_unicast_SAFI_to_bgp_neighbor(65000, "172.16.255.2")
xr_oc_model_r2.add_ipv4_unicast_SAFI_to_bgp_neighbor(65000,"172.16.255.1")



