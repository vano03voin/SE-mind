from app.pkg.world_tools.entities_subtool import XYZ


class GPS:
    def __init__(self, name='', coordinates=XYZ(x=0, y=0, z=0)):
        self.name = name
        self.coordinates = coordinates

    def to_json(self):
        gps_dict = {
            'name': str(self.name),
            'coordinates': self.coordinates.get_like_list()
        }
        return gps_dict


class Player:
    def __init__(self, xml_sector, xml_identity):
        self.xml_sector = xml_sector
        self.xml_identity = xml_identity
        self.xml_item = self.xml_sector.find(f"AllPlayersData/dictionary/item/Value[IdentityId='{self.get_id()}']")

    @classmethod
    def get_players(cls, xml_sector):
        return [Player(xml_sector, identity) for identity in xml_sector.find("Identities")]

    @classmethod
    def get_players_ids(cls, xml_sector):
        return [identity.find('IdentityId').text for identity in xml_sector.find("Identities")]

    def get_id(self):
        return self.xml_identity.find('IdentityId').text

    def get_name(self):
        if (name := self.xml_identity.find('DisplayName').text) is not None:
            pass
        elif (name := self.xml_identity.find('Model')) is not None:
            name = name.text
        if '' in str(name):
            name = name[1:]
        #print(name, self.get_id())
        return str(name)

    def get_death_xyz(self):
        try:
            return XYZ(
                x=float(self.xml_identity.find('LastDeathPosition').find('X').text),
                y=float(self.xml_identity.find('LastDeathPosition').find('Y').text),
                z=float(self.xml_identity.find('LastDeathPosition').find('Z').text)
            )
        except AttributeError:
            return XYZ(x=0, y=0, z=0)

    def get_connected(self):
        if not self.xml_item:
            return False
        return self.xml_item.find('Connected').text

    def get_is_admin(self):
        if not self.xml_item:
            return False
        creative = self.xml_item.find('CreativeToolsEnabled').text != 'false'
        admin = self.xml_item.find('RemoteAdminSettings').text != '0'
        promoted = self.xml_item.find('PromoteLevel').text != 'None'
        return creative or admin or promoted

    def get_is_wildlife(self):
        if not self.xml_item:
            return False
        return self.xml_item.find('IsWildlifeAgent').text

    def get_gps(self) -> list[GPS]:
        gps_stash = self.xml_sector.find(f"Gps/dictionary/item[Key='{self.get_id()}']")
        gps_list = []
        if gps_stash:
            for value in gps_stash.find('Value/Entries'):
                coords = value.find('coords')
                gps_list.append(
                    GPS(
                        name=value.find('name').text,
                        coordinates=XYZ(
                            x=float(coords.find('X').text),
                            y=float(coords.find('Y').text),
                            z=float(coords.find('Z').text),
                        )
                    )
                )
        return gps_list

    def get_balance(self):
        for session_comp in self.xml_sector.find('SessionComponents'):
            if session_comp.get('{http://www.w3.org/2001/XMLSchema-instance}type') == 'MyObjectBuilder_BankingSystem':
                account = session_comp.find(f'Accounts/MyObjectBuilder_AccountEntry[OwnerIdentifier="{self.get_id()}"]')
                try:
                    return account.find('Account/Balance').text
                except AttributeError:
                    return '0'

    def to_json(self):
        player_dict = {
            'id': self.get_id(),
            'name': self.get_name(),
            'last_deth_gps': self.get_death_xyz().get_like_list(),
            'get_connected': self.get_connected(),
            'admin': self.get_is_admin(),
            'wildlife': self.get_is_wildlife(),
            'balance': self.get_balance(),
            'gps_list': [gps.to_json() for gps in self.get_gps()]
        }
        return player_dict


class FactionMember:
    def __init__(self, xml_source):
        self.xml_source = xml_source

    def get_id(self) -> str:
        return self.xml_source.find('PlayerId').text

    def get_is_leader(self):
        return self.xml_source.find('IsLeader').text

    def get_is_founder(self):
        return self.xml_source.find('IsFounder').text

    def to_json(self):
        faction_dict = {
            'id': self.get_id(),
            'leader': self.get_is_leader(),
            'founder': self.get_is_founder()
        }
        return faction_dict


class Faction:
    def __init__(self, xml_sector, xml_source):
        self.xml_sector = xml_sector
        self.xml_source = xml_source

    @classmethod
    def get_factions(cls, xml_sector):
        return [Faction(xml_sector, f) for f in xml_sector.find('Factions/Factions')]

    @classmethod
    def get_factions_stations_gps(cls, xml_sector):
        station_gps = []
        for faction in [Faction(xml_sector, f) for f in xml_sector.find('Factions/Factions')]:
            for station in faction.xml_source.find('Stations'):
                tmp = list(station.find("Position").attrib.items())
                x, y, z = float(tmp[0][1]), float(tmp[1][1]), float(tmp[2][1])
                station_gps.append(XYZ(int(x), int(y), int(z)).get_gps_mark(faction.get_tag()))
        return station_gps

    def get_id(self):
        return self.xml_source.find('FactionId').text

    def get_tag(self):
        return self.xml_source.find('Tag').text

    def get_name(self):
        return self.xml_source.find('Name').text

    def get_members(self):
        return [FactionMember(member) for member in self.xml_source.find('Members')]

    def get_faction_type(self):
        return self.xml_source.find('FactionType').text

    def get_balance(self):
        for session_comp in self.xml_sector.find('SessionComponents'):
            if session_comp.get('{http://www.w3.org/2001/XMLSchema-instance}type') == 'MyObjectBuilder_BankingSystem':
                account = session_comp.find(f'Accounts/MyObjectBuilder_AccountEntry[OwnerIdentifier="{self.get_id()}"]')
                return account.find('Account/Balance').text

    def to_json(self):
        faction_dict = {
            'id': self.get_id(),
            'tag': self.get_tag(),
            'name': self.get_name(),
            'balance': self.get_balance(),
            'members': [member.to_json() for member in self.get_members()]
        }
        return faction_dict
