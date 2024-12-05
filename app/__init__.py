import logging
from .cache import appCache
from .views.overview import MapOverview
from .views.devices import DevicesOverview
from .views.connections import ConnectionOverview,CustomConnectionGraph,CEInterConnect
from .views.device_path import L2PathOverview
from .views.single_device import DeviceView
from .views.services import ServiceView
from .views.locations import LocationView
from .views.hardware import HardwareView
from .views.object_types import ObjectTypeView
from .views.empty import EmptyView
from .views.dataquality import CircuitMissingPort, DeviceMissingLocation, DeviceMissingPort, NonConsecutiveLine
from .views.dataimport import ImportSiteView, ImportDeviceView, ImportSpanView

from .api.location import LocationAPI
from .api.span import SpanAPI
from .api.line_name import LineNameAPI

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


appCache.init_app(app)

class MyIndexView(IndexView):
    index_template = 'home.html'

appbuilder = AppBuilder(app, db.session, indexview=MyIndexView)

appbuilder.add_view(MapOverview, "Overview", category='Network Components', category_icon='fa-network-wired', icon='fa-map')
appbuilder.add_view(DevicesOverview, "All devices", category='Network Components', icon='fa-display')
appbuilder.add_view(ServiceView, "All services", category='Network Components', icon='fa-circle-nodes')
appbuilder.add_view(LocationView, "All locations", category='Network Components', icon='fa-location-dot')
appbuilder.add_view(HardwareView, "All hardware", category='Network Components', icon='fa-server')
appbuilder.add_view(ObjectTypeView, "All object types", category='Network Components', icon='fa-list')

appbuilder.add_view(ImportSiteView, "Add site", category='Import', icon='fa-location-dot', category_icon='fa-download')
appbuilder.add_view(ImportDeviceView, "Add device", category='Import', icon='fa-server')
appbuilder.add_view(ImportSpanView, "Add span", category='Import', icon='fa-route')

appbuilder.add_view(CircuitMissingPort, "Circuit zonder L1 koppeling", category='Data quality', category_icon='fa-ranking-star')
appbuilder.add_view(DeviceMissingLocation, "Devices zonder locatie", category='Data quality')
appbuilder.add_view(DeviceMissingPort, "Devices zonder Port/Interface", category='Data quality')
appbuilder.add_view(NonConsecutiveLine, "Niet-doorlopende lijnen", category='Data quality')


appbuilder.add_view_no_menu(DeviceView)

appbuilder.add_view_no_menu(LocationAPI)
appbuilder.add_view_no_menu(SpanAPI)
appbuilder.add_view_no_menu(LineNameAPI)