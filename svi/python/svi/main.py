# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import netaddr

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        svi = {'vlan-id': "",
               'svi-device': "",
               'ip-prefix': "",
               'ip-addr': "",
               'netmask': ""}

        svi['vlan-id'] = service.vlan_id

        for device in service.device:
            self.log.info('Entering /device list = ' , device.name)
            if device.ip_prefix:
                self.log.info('SVI device = ' , device.name)

                ip_net = netaddr.IPNetwork(device.ip_prefix)
                svi['svi-device'] = device.name
                svi['ip-prefix'] = \
                    str(ip_net[2])+"/"+str(ip_net.prefixlen)
                svi['ip-addr'] = str(ip_net[1])
                svi['netmask'] = str(ip_net.netmask)

                svi_tvars = ncs.template.Variables()
                svi_tvars.add('VLAN-ID' , svi['vlan-id'])
                svi_tvars.add('SVI-DEVICE' , svi['svi-device'])
                svi_tvars.add('IP-PREFIX' , svi['ip-prefix'])
                svi_tvars.add('IP-ADDR' , svi['ip-addr'])
                svi_tvars.add('NETMASK' , svi['netmask'])
                svi_template = ncs.template.Template(service)
                svi_template.apply('svi-intf-template' , svi_tvars)

        vlan_tvars = ncs.template.Variables()
        vlan_tvars.add('VLAN-ID' , svi['vlan-id'])
        vlan_template = ncs.template.Template(service)
        vlan_template.apply('svi-vlan-template' , vlan_tvars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('svi-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
