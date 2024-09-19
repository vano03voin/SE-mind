import sys
import xml.etree.ElementTree as ET
from pprint import pprint

import datetime
import json
import pickle
import time
import zlib
import gzip

from app.pkg.xml_tools.tools import ElementTree
from app.pkg.world_tools.entities_subtool import *
from app.pkg.world_tools.players_subtool import *
from app.pkg.world_tools.logs_subtool import OwnershipLog


class WorldManager:
    """Reed gamesave. Edit sandbox and SANDBOX, had high-levl tools"""

    Sandbox_path = 'Sandbox.sbc'
    SANDBOX_path = 'SANDBOX_0_0_0_.sbs'

    def __init__(self, folder_path: str, rw='r'):
        print(f'init world edit {folder_path}')
        self.path = folder_path
        self.rw = rw

    def execute_commands(self, commands: list[str]):
        #reed save
        start_time = time.time()
        self.sandbox = SandboxWorker(self.path + self.Sandbox_path)
        self.SANDBOX = SANDBOXWorker(self.path + self.SANDBOX_path)
        print(f'reed save take {time.time() - start_time}')
        start_time = time.time()

        #edit save
        self.id_trade = self.sandbox.id_trade + self.SANDBOX.id_trade

        for command in commands:
            match command:
                case 'get_grid_names':
                    self.get_grid_names()
                case 'get_inventory':
                    self.get_inventory()
                case 'fix_world':
                    self.fix_world()
                case 'update_trade':
                    #self.update_trade()
                    pass
                case 'check_security':
                    self.check_security()
                case 'test_manager_command':
                    self.test_manager_command()
                case 'send_dump_to_server':
                    self.send_dump_to_server()
                case 'get_faction_resourses':
                    self.get_faction_resourses()
                case 'get_factions_stations_gps':
                    pprint(Faction.get_factions_stations_gps(self.sandbox.sector))
                case 'dump_data':
                    self.dump_data()
                case _:
                    print(f'команды {command} не существует')

        print(f'commands take {time.time() - start_time}')
        # PART WHEN WE SAVE CHANGES
        if self.rw == 'w':
            start_time = time.time()
            self.save_changes()
            print(f'save world take {time.time() - start_time}')

    def dump_data(self):
        data_to_send = self
        print(1)

    def get_grid_names(self):
        """Return custom grids names"""
        for grid in self.SANDBOX.get_grids():
            if 'Grid' not in i.name:
                print(i.name)

    def get_inventory(self):
        """I use to check where wealth flow to another person"""
        #for entiti in self.SANDBOX.ENTITIES:
        s_time = time.time()
        keys = {}
        for grid in self.SANDBOX.get_grids():
            for block in grid.get_blocks():
                if block.get_builder_id() == '144115188075867343' or block.get_builder_id() == '144115188075857675':
                    for name, amount in block.get_inventory().items():
                        if 'Uranium' in name:
                            keys.setdefault(block.get_builder_id(), {})
                            keys[block.get_builder_id()].setdefault(name, 0)
                            keys[block.get_builder_id()][name] += amount
        pprint(keys)
        print(f'get inventory take {time.time() - s_time}s')

    def fix_world(self):
        """Fixing most common but noise things"""
        self.sandbox.fix_strongs()
        self.SANDBOX.fix_huv()

    def update_trade(self):  # IN PROGRES
        for grid in self.SANDBOX.get_grids():
            if '[SIMP]' in grid.get_name():
                self.id_trade += grid.update_store(self.id_trade)

    def check_security(self):
        """Check who or what play ower ur server laws"""
        self.SANDBOX.check_volume(self.sandbox.id_name)

    def save_changes(self):
        """Save changes"""
        self.sandbox.element_tree.save_tree()
        self.SANDBOX.element_tree.save_tree()
        ElementTree.remove_file(self.path + 'SANDBOX_0_0_0_.sbsB5')

    def get_faction_resourses(self):
        members = []
        factions_balance = {}
        for faction in Faction.get_factions(self.sandbox.sector):
            factions_balance[faction] = {}
            #if faction.get_tag() == 'OIS':
            #    members = [memb.get_id() for memb in faction.get_members()]

        for grid in self.SANDBOX.get_grids():
            for p_id, p_inv in grid.get_inventory_and_owners().items():
                for tag, inv in factions_balance.items():
                    if p_id in [member.get_id() for member in tag.get_members()]:
                        #if p_id in members:
                        InventoryItem.merge_inv(inv, p_inv)
        #pprint(faction_balance)
        self.faction_balance = {fac.get_tag(): it for fac, it in factions_balance.items()}

        maxim = [0, 0]
        for fac, inv in self.faction_balance.items():
            if inv.get('MyObjectBuilder_Component EngineerPlushie', 0) > maxim[0]:
                maxim=[inv['MyObjectBuilder_Component EngineerPlushie'], fac]
        self.top_fac = maxim
        print(maxim[1], maxim[0])
        #pprint({fac.get_tag(): it for fac, it in factions_balance.items()})
        #pprint(self.faction_balance)
        #g = {}
        #for name, value in faction_balance.items():
        #    if 'MyObjectBuilder_Ingot' in name:
        #        g[name] = value
        #self.get_best_pl(g)
        #return faction_balance

    def send_dump_to_server(self):
        # entities = {
        #     'grids': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is CubeGrid],
        #     'characters': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is Character],
        #     'floating_objects': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is FloatingObject],
        #     'inventory_bags': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is InventoryBagEntity]
        # }
        save_date = datetime.datetime.fromtimestamp(int(self.sandbox.element_tree.create_time))

        gamesave_dict = {
            # 'world_id': self.sandbox.sector.find('WorldId').text,
            'save_date': str(datetime.datetime.fromtimestamp(int(self.sandbox.element_tree.create_time))).replace(' ', 'T') + '.28Z',
            # 'session_name': self.sandbox.sector.find('SessionName').text,

            'grids': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is CubeGrid],
            'characters': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is Character],
            'floating_objects': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is FloatingObject],
            'inventory_bags': [ent.to_json() for ent in self.SANDBOX.ENTITIES if type(ent) is InventoryBagEntity],

            'factions': [faction.to_json() for faction in Faction.get_factions(self.sandbox.sector)],
            'players': [player.to_json() for player in Player.get_players(self.sandbox.sector)],

            'ownership_log': OwnershipLog.get_json_for_sending(save_date, self.path, int(self.sandbox.sector.find("Settings/AutoSaveInMinutes").text))
        }
        # {'grids': [], 'characters': [], 'floating_objects': [], 'planets':[], 'safezones':[], 'voxel_maps':[], 'inventory_bags':[]}

        self.gamesave_dict = gamesave_dict

    def test_manager_command(self):
        #self.get_faction_resourses()
        #raise

        self.send_dump_to_server()

        #self.check_security()
        lst = []
        for grid in self.SANDBOX.get_grids():
            grid.get_size()
            grid.get_static()
            grid.get_killable()
            grid.get_xyz()
            #pprint(grid.to_json())
            for block in grid.get_blocks():
                block.get_inventory().items()
                block.get_share_mode()
                block.get_who_own()
                if False and block.get_type() == 'MyObjectBuilder_CubeBlock':
                    a = 0
                    shit = ['Catwalk', 'Armor', 'Window', 'Stairs', 'Column', 'Pillar', 'Ramp']
                    for i in shit:
                        if i in block.get_subtype():
                            a = 1
                    if a == 0:
                        print(block.get_id())

                #FilledRatio
                if False and block.xml_source.find('Capacity') is not None:
                    lst.append(block.get_type())
        #pprint(sorted(list(set(lst))))
        #raise
        for char in [ent for ent in self.SANDBOX.ENTITIES if type(ent) is Character]:
            char.get_model()
            char.get_inventory()
            #pprint(char.to_json())

        for zone in [ent for ent in self.SANDBOX.ENTITIES if type(ent) is SafeZone]:
            zone.get_shape()
            zone.get_size()
            zone.get_is_enabled()
            #pprint(zone.to_json())

        for p in Player.get_players(self.sandbox.sector):
            p.get_id()
            p.get_name()
            p.get_balance()
            p.get_gps()
            p.get_is_admin()
            p.get_connected()
            p.get_death_xyz()
            p.get_is_wildlife()
            #pprint(p.to_json())

        for f in Faction.get_factions(self.sandbox.sector):
            #pprint(f.to_json())

            f.get_id()
            f.get_name()
            f.get_balance()
            f.get_tag()
            for m in f.get_members():
                m.get_id()
                m.get_is_leader()
                m.get_is_founder()
        #raise


class SandboxWorker:
    """work with raw xml Sandbox.sbc"""

    def __init__(self, path):
        self.element_tree = ElementTree(path)
        self.sector = self.element_tree.tree.getroot()

        self.id_name = self.get_id_name()
        self.id_trade = self.get_id_trade()

    def get_id_name(self):
        """Return shit person_id: person_name. Useful in high-lvl output"""
        #persons = self.sector.find('AllPlayersData').findall('.//item')
        id_name = {}
        for person in Player.get_players(self.sector):
            id_name[person.get_id()] = person.get_name()
        return id_name

    def fix_strongs(self):
        """fix unknow signals undrop i guess)"""
        for strong in self.sector.findall('.//PlayerContainerData'):
            strong.find('Active').text = 'true'
            strong.find('Competetive').text = 'true'

    def get_id_trade(self):
        """Sometime when u do on restart custom trade offers, u need to know all existing block_id to not repeet it"""
        id_trade = []
        for item in self.sector.findall('.//MyObjectBuilder_StoreItem'):
            id_trade.append(item.find('Id').text)
        return list(set(id_trade))


class SANDBOXWorker:
    """work with raw xml SANDBOX_0_0_0_.sbc"""

    def __init__(self, path):
        # Prepare data for main module
        self.element_tree = ElementTree(path)
        self.sector = self.element_tree.tree.getroot()

        self.id_trade = self.get_id_trade()

        self.ENTITIES = self.get_entities()

    def get_entities(self):
        entities = []
        for sector_object in self.sector.find('SectorObjects'):
            entities.append(Entity.create_entity(sector_object))
        return entities

    def get_grids(self):
        grids = []
        for sector_object in self.sector.find('SectorObjects'):
            if sector_object.get('{http://www.w3.org/2001/XMLSchema-instance}type') == 'MyObjectBuilder_CubeGrid':
                grids.append(CubeGrid(sector_object))
        return grids

    def get_all_blocks(self):
        blocks = []
        for grid in self.get_grids():
            blocks += grid.get_blocks()
        return blocks

    def fix_huv(self):
        """If ur world broke, I first check HUV in save. Bad cheaters broke HUV to make ur life bad("""
        for block in self.get_all_blocks():
            try:
                huv = block.xml_source.find('ColorMaskHSV')
                huvdat = list(block.xml_source.find('ColorMaskHSV').attrib.items())
                if huvdat[0][1] == 'NaN' or huvdat[1][1] == 'NaN' or huvdat[2][1] == 'NaN':
                    for i in huvdat:
                        huv.set(i[0], '0.1')
            except AttributeError:
                pass

    def check_volume(self, id_name):
        """On my server ZERG and NECR spam by this infinity volume shit. Now they cant do that silently"""
        for grid in self.get_grids():
            for block in grid.get_blocks():
                path = 'ComponentContainer/Components/ComponentData/Component/'
                if ((volume := block.xml_source.find(path + 'Volume')) is not None) and float(volume.text) > 500:
                    try:
                        owner = f'Player {id_name[block.get_who_own()]}'
                    except KeyError:
                        owner = f'NPC    {block.get_who_own()}'
                    msg = f'{owner} stretch {block.get_type()} id {block.get_id()} on {volume.text}k liters \n'
                    self.to_log('Log.txt', msg)
                    #grid.remove(block)

    def get_id_trade(self):
        """Sometime when u do on restart custom trade offers, u need to know all existing block_id to not repeet it"""
        id_trade = []
        for item in self.sector.findall('.//MyObjectBuilder_StoreItem'):
            id_trade.append(item.find('Id').text)
        return list(set(id_trade))

    @staticmethod
    def to_log(where, what):
        with open(where, 'a', encoding="utf-8", newline='') as f:
            print(what[:-2])
            f.write(what)


class CubeGridOld:
    def update_store(self, id_trade):  # IN PROGRES
        to_update = {'stores': 0, 'resources': {}}
        stores = []
        for block in self.blocks:
            if block.block_type == 'MyObjectBuilder_CargoContainer':
                for item in block.get_inventory():
                    to_update['resources'][item.subtype] = to_update['resources'].setdefault(item.subtype,
                                                                                             0) + item.amount
            elif block.block_type == 'MyObjectBuilder_StoreBlock' and block.subtype == 'StoreBlock':
                to_update['stores'] = to_update['stores'] + 1
                stores.append(block)
        # afterUpdate=setstore(to_update)
        # pprint(to_update)
        calculated = setshop.main_economic_function(toUpdate)
        pp.pprint(calculated)
        storenum = 0
        for block in blocks:
            if str(block.get(
                    '{http://www.w3.org/2001/XMLSchema-instance}type')) == 'MyObjectBuilder_StoreBlock' and str(
                    block.find('.//SubtypeName').text) == 'StoreBlock':
                store = calculated[storenum]
                storenum = storenum + 1
                setstore(block, store)
        return []
        #return shitemsids

    @staticmethod
    def setstore(block, store, shitemsids):  # IN PROGRES
        block.find('AnyoneCanUse').text = 'true'

        block.remove(block.find('PlayerItems'))
        # print(block.find("EntityId").text)
        storeitlist = ET.SubElement(block, 'PlayerItems')
        tmp = None
        for item in store[2:]:
            for i in shitemsids:
                if str(tmp := int(i) + 1) not in shitemsids:
                    shitemsids.append(str(tmp))
                    break
            bstore = ET.SubElement(storeitlist, 'MyObjectBuilder_StoreItem')
            s_id = ET.SubElement(bstore, 'Id')  # block_id
            s_id.text = str(tmp)
            s_item = ET.SubElement(bstore, 'Item')
            s_item.set('Type', 'MyObjectBuilder_' + item[1])
            s_item.set('Subtype', item[2].replace('Gravity', 'GravityGenerator').replace('Thruster', 'Thrust'))
            s_item_type = ET.SubElement(bstore, 'ItemType')
            s_item_type.text = 'PhysicalItem'
            s_amount = ET.SubElement(bstore, 'Amount')
            s_amount.text = str(item[3])
            s_removed_amount = ET.SubElement(bstore, 'RemovedAmount')
            s_removed_amount.text = '0'
            s_price_per_unit = ET.SubElement(bstore, 'PricePerUnit')
            s_price_per_unit.text = str(item[4])
            s_store_item_type = ET.SubElement(bstore, 'StoreItemType')
            s_store_item_type.text = 'Offer' if item[0] == 'sell' else 'Order'
            s_update_count = ET.SubElement(bstore, 'UpdateCount')
            s_update_count.text = '0'
            s_prefab_total_pcu = ET.SubElement(bstore, 'PrefabTotalPcu')
            s_prefab_total_pcu.text = '0'
            s_price_per_unit_discount = ET.SubElement(bstore, 'PricePerUnitDiscount')
            s_price_per_unit_discount.text = '0'
        # Надписи
        data = block.find('TextPanelsNew').findall('MySerializedTextPanelData')

        data[0].find('FontSize').text = '3'
        if (tmp := data[0].find('Text')) is not None:
            tmp.text = store[1]
        else:
            tmp = ET.SubElement(data[0], 'Text')
            tmp.text = store[1]
        if (tmp := data[0].find('ContentType')) is not None:
            tmp.text = 'TEXT_AND_IMAGE'
        else:
            tmp = ET.SubElement(data[0], 'ContentType')
            tmp.text = 'TEXT_AND_IMAGE'

        data[1].find('FontSize').text = '10'
        if (tmp := data[1].find('Text')) is not None:
            tmp.text = (store[0] + ' 2 U' if store[0] == 'sell' else store[0] + ' fr U')
        else:
            tmp = ET.SubElement(data[1], 'Text')
            tmp.text = (store[0] + ' 2 U' if store[0] == 'sell' else store[0] + ' fr U')
        if (tmp := data[1].find('ContentType')) is not None:
            tmp.text = 'TEXT_AND_IMAGE'
        else:
            tmp = ET.SubElement(data[1], 'ContentType')
            tmp.text = 'TEXT_AND_IMAGE'
        return shitemsids
