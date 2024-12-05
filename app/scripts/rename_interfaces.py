import re

renaming_table = {
    "mgmt": ['mgmt', ],
    "Ethernet": ['Ethernet', 'eth' ],
    "FastEthernet": ['FastEthernet', 'FA'],
    "GigabitEthernet": ['GigabitEthernet', 'Gi', 'GI'],
    "TenGigabitEthernet": ['TenGigabitEthernet', 'TenGigE', 'Te'],
    "TwentyFiveGigabitEthernet": ['TwentyFiveGigabitEthernet', 'TwentyFiveGigE', ],
    "HundredGigabitEthernet": ['HundredGigabitEthernet', 'HundredGigE', ],
}

def convert(interface_name):
    
    match = re.match(r"([a-z]+)([0-9\/]+)", interface_name, re.I)
    if match:
        items = match.groups()
        # print(items)
        for key, value in renaming_table.items():
            if items[0] in value:
                return f"{key}{items[1]}"
        raise Exception(f"{interface_name} not found in lookup table")
        