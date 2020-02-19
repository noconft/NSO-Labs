# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        #..[setup stuff]..
        geoVars = ncs.template.Variables()
        template = ncs.template.Template(service)
        #..[initilize vars]..
        geoVars.add('DEV', '')
        geoVars.add('DOMNAME', '')
        geoVars.add('DNSIP', '')
        geoVars.add('NTPIP', '')
        geoVars.add('COMMUNITY', '')
        geoVars.add('ACCESS', '')
        #..
        #..[get the localTZ for the devices in this service instnce]..
        #..[all devices in this service instance are in this TZ]...
        localTZ=service.localTZ
        self.log.debug('localTZ: ' , localTZ)
        #..[now, read stuff from geo-catalog for this TZ]..
        #..[domain-name]..(leaf)..
        domName = root.GeoCatalog[localTZ].domainName
        self.log.debug('domName: ' , domName)
        #..[nameServers]..(leaf-list)..
        nameServers = root.GeoCatalog[localTZ].nameServer
        self.log.debug('nameServers: ' , nameServers)
        self.log.debug('num nameServers: ' , len(nameServers))
        #..[ntpServers]..(leaf-list)..
        ntpServers = root.GeoCatalog[localTZ].ntpServer
        self.log.debug('ntpServers: ' , ntpServers)
        self.log.debug('num ntpServers: ' , len(ntpServers))
        #..[snmpRO][snmpRW]..
        snmpRO = root.GeoCatalog[localTZ].snmpCommRO
        snmpRW = root.GeoCatalog[localTZ].snmpCommRW
        self.log.debug('snmpRO: ' , snmpRO , ' snmpRW: ' , snmpRW)
        #..
        #..ok, now we hve everyone, let's write data out to devices..
        #..walk through all the devices (leaf-list)..
        for i , dev in enumerate(service.device):
            self.log.debug('dev: ' , i , ' name: ' , dev)
            geoVars.add('DEV' , dev)
            geoVars.add('COMMUNITY' , snmpRO)
            geoVars.add('ACCESS' , 'ro')
            template.apply('geoPysnmp-template' , geoVars)
            geoVars.add('COMMUNITY' , snmpRW)
            geoVars.add('ACCESS' 'rw')
            template.apply('geoPysnmp-template' , geoVars)
            geoVars.add('DOMNME' , domName)
            template.apply('geoPysnmp-template' , geoVars)
            for dsrv in nameServers:
                geoVars.add('DNSIP' , dsrv)
                template.apply('geoPysnmp-template' , geoVars)
            for ntp in ntpServers:
                geoVars.add('NTPIP' , ntp)
                template.apply('geoPysnmp-template' , geoVars)

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
        self.register_service('geoPysnmp-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
