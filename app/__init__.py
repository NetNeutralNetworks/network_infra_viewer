import logging
from .ncubed_security_manager import MySecurityManager
from .views.overview import MapOverview
from .views.devices import DevicesOverview
from .views.connections import ConnectionOverview,CustomConnectionGraph,CEInterConnect
from .views.device_path import L2PathOverview
from .views.single_device import DeviceView
from .views.services import ServiceView
from .views.locations import LocationView
from .views.hardware import HardwareView
from .views.object_types import ObjectTypeView
from .views.recommendations import RecommendationView
from .views.generate_fake_score import GenerateFakeScores
from .views.empty import EmptyView
from .views.dataquality import LijnbenamingMissingPort, DeviceMissingLocation, DeviceMissingPort, NonConsecutiveLine
from .views.abnomalies import DualHoming, Redundancy, LineRedundancy, LineRedundancyMap
from .views.specific_requests import CVRFibers, WKSImport, InterfacesDevices, DevicesSerial, WirelessUplinks, RegexTest
from .views.abbreviations import Abbreviations
from .views.location_plotting import MatchDeviceToLocation

from .api.location import LocationAPI
from .api.span import SpanAPI

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA, IndexView


"""
 Logging configuration
"""
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)


class MyIndexView(IndexView):
    index_template = 'home.html'

appbuilder = AppBuilder(app, db.session, indexview=MyIndexView)

# appbuilder.add_view(ConnectionOverview, "Layer2", category='Network')

appbuilder.add_view(MapOverview, "Overview", category='Network Components', category_icon='fa-network-wired', icon='fa-map')
appbuilder.add_view(DevicesOverview, "All devices", category='Network Components', icon='fa-display')
appbuilder.add_view(ServiceView, "All services", category='Network Components', icon='fa-circle-nodes')
appbuilder.add_view(LocationView, "All locations", category='Network Components', icon='fa-location-dot')
appbuilder.add_view(HardwareView, "All hardware", category='Network Components', icon='fa-server')
appbuilder.add_view(ObjectTypeView, "All object types", category='Network Components', icon='fa-layer-group')
appbuilder.add_view(RecommendationView, "Recommendations", category='Network Components', icon='fa-lightbulb')

appbuilder.add_view(DualHoming, "Dualhoming mistakes", category='Anomalies', category_icon='fa-triangle-exclamation')
appbuilder.add_view(Redundancy, "Redundancy mistakes", category='Anomalies')
appbuilder.add_view(LineRedundancy, "Redundant uplink overlap", category='Anomalies')
appbuilder.add_view(LineRedundancyMap, "Line redundancy mistakes plotted on a map", category='Anomalies')

appbuilder.add_view(LijnbenamingMissingPort, "Lijnbenaming zonder L1 koppeling", category='Data quality', category_icon='fa-ranking-star')
appbuilder.add_view(DeviceMissingLocation, "Devices zonder locatie", category='Data quality')
appbuilder.add_view(DeviceMissingPort, "Devices zonder Port/Interface", category='Data quality')
appbuilder.add_view(NonConsecutiveLine, "Niet-doorlopende lijnen", category='Data quality')

# appbuilder.add_view(CustomConnectionGraph, "Connections", category='Testing')
# appbuilder.add_view(L2PathOverview, "Path", category='Testing')
# appbuilder.add_view(EmptyView, "Empty page", category='Testing')
# appbuilder.add_view(MatchDeviceToLocation, "Location plotting", category='Testing')

appbuilder.add_view(CVRFibers, "CVR Fibers", category='Specific requests', category_icon='fa-bell-concierge')
appbuilder.add_view(WKSImport, "WKS", category='Specific requests')
appbuilder.add_view(InterfacesDevices, "Cellular devices", category='Specific requests')
appbuilder.add_view(WirelessUplinks, "Wireless connected devices", category='Specific requests')
appbuilder.add_view(CEInterConnect, "Interconnect", category='Specific requests')
appbuilder.add_view(DevicesSerial, "Serial numbers", category='Specific requests')
appbuilder.add_view(RegexTest, "Regex test", category='Specific requests')

appbuilder.add_view(Abbreviations, "Afkortingen", category='Info', category_icon='fa-circle-info')

appbuilder.add_view_no_menu(DeviceView)
appbuilder.add_view_no_menu(GenerateFakeScores)

appbuilder.add_view_no_menu(LocationAPI)
appbuilder.add_view_no_menu(SpanAPI)