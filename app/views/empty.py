import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

class EmptyView(BaseView):
    default_view = 'main_page'

    @expose('/overview/', methods=['GET','POST'])
    @has_access
    def main_page(self):
        
        return self.render_template('empty.html')
    
    
class UITestView(BaseView):
    default_view = 'ui_test'
    @expose('/ui_test/', methods=['GET'])
    @has_access
    def ui_test(self):
        
        return self.render_template('ui_test.html', page_category='Info')
    
   