import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

definitions = {
    'AAA': 'Authentication,Authorization and Accounting',
    'ACL': 'Access Control List',
    'ACS': 'Access Control Service',
    'ARP': 'Adress Resolution Protocol',
    'ABB': 'Architectural building blocks',
    'BB': 'Backbone (Netwerkbackbone, de logische en fysieke verbindingen tussen de PE routers. Deze maken samen de kerninfrastructuur van het netwerk. backbone wordt ook gebruikt als aanduiding voor de hoofd-glasvezelkabels langs weg- en waterkant.)',
    'BO': 'Break-out (Een afsplitsing vanaf de hoofd glasvezelkabels, veelal 4 of 8 vezels vanuit een GKP met GAB naar een object of wegkant toepassing.)',
    'BPDU': 'Bridge Protocol Data Unit',
    'BPS': 'Beschrijvende Plaatsbepaling Systematiek (Beschrijvende Plaatsaanduiding Systematiek waarmee een exacte geografische locatie op rijkswegen kan worden weergegeven. Deze code te gebruiken bij b.v. het labelen van kabels, GAB en panelen.)',
    'BYZ': 'Bijzondere locatie',
    'LB': 'Limburg',
    'NB': 'Noord-Brabant',
    'NH': 'Noord-Holland',
    'ZH': 'Zuid-Holland',
    'NN': 'Noord Nederland',
    'ON': 'Oost Nederland',
    'UT': 'Utrecht',
    'MN': 'Midden Nederland',
    'YG': 'Ijselmeergebied',
    'ZH': 'Zuid-Holland',
    'ZL': 'Zeeland',
    'BYZ': 'Bijzondere locatie',
    'CVR': 'Centrale VICnet ruimte',
    'REM': 'Remote locatie',
    'VOR': 'VICnet object ruimte',
    'VSR': 'VICnet systeem ruimte',
    'CAM': 'Camera',
    'DS': '<a href="https://www.wegenwiki.nl/Detectorstation">Detector station (Weglussen)</a>',
    'DOV': 'Dynamische openbare verlichting',
    'DID': 'Data informatiedienst (Locatie type)',
    'DRIP': '<a href="https://www.wegenwiki.nl/Dynamisch_route-informatiepaneel">Dynamisch route-informatie paneel</a>',
    'GMS': '<a href="https://www.wegenwiki.nl/Gladheidmeldsysteem">Gladheid meldsysteem</a>',
    'TCS': 'Traject controle systeem',
    'TDI': '<a href="https://www.wegenwiki.nl/Toeritdoseerinstallatie">Toerit doseerinstallatie</a>',
    'VAD': 'Vluchthaven aanwezigheids detectie',
    'VRI': 'Verkeers regel instalatie',
    'WIM': '<a href="https://www.wegenwiki.nl/Weegpunt">Weigh in motion</a>',
    'BHK': 'Beheerkast',
    'MNK': 'Monitoringkast',
    'MPK': 'Multiplexerkast',
    'RSK': 'Reservekast',
    'RTK': 'Routerkast',
    'SAK': 'Secure Access Kast',
    'SMK': 'Storingsmeldkast',
    'SPK': 'Sterpuntkast',
    'SVK': 'Serverkast',
    'SWK': 'Switchkast',
    'TLK': 'Telecomkast',
    'TRK': 'Transmissiekast',
    'CIV': 'Centrale informatievoorziening (Afdeling RWS)',
    'IRN': 'Infrastructuur rijkswaterstaat netwerken',
    'LKK': '<a href="https://www.wegenwiki.nl/Luskoppelkast">Luskoppelkast</a>',
    'OS': '<a href="https://www.wegenwiki.nl/Wegkantstation">Onderstation</a>',
    'WKS': '<a href="https://www.wegenwiki.nl/Wegkantstation">Wegkant station/systeem</a>',
    'VICnet': 'Verkeersinformatie- en communicatienetwerk',
    'EFTM': 'Elekronische Fysieke Toegang en Monitoring (VRF/VPN/Dienst)',
    'CCM': 'Control Centre MKO',
    'DVM': 'Dynamisch verkeersmanagemnt',
    'DVR': 'Digitale Video Recorder',
    'ELS': 'Event Logging System',
    'GKP': 'Glasvezelkabelput',
    'HWN': 'Hoofdwegennet',
    'IV': 'Informatie voorziening',
    'KA': 'Kantoor Automatisering',
    'KMS': 'Kwaliteitmanagementsysteem',
    'KNMI': 'Koninklijk Nederlands Metereologish Instituut',
    'LIV': 'Locatie Informatie Viewer (RWS tool waar toegangsprocedures zijn beschreven)',
    'NNV': 'Nieuwe Netwerkvoorzieningen',
    'ODC': 'OverheidsDataCenter',
    'PID': 'Project Initiatie Document'


}

class Abbreviations(BaseView):
    default_view = 'main_page'

    @expose('/overview/', methods=['GET','POST'])
    @has_access
    def main_page(self):
        help = f"""
        
        """
        entries = []
        for key, value in definitions.items():
            entries.append(f"""{key}</td><td>{value}""")
        return self.render_template('multi_column_table.html', table_header="Afkorting</td><td>Betekenis", entries=entries, page_info=help)
    
   