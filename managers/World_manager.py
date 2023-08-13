import xml.etree.ElementTree as ET
import time

if __name__ == '__main__':
    from Xml_tools import XmlNanure, ElementTree
else:
    from managers.Xml_tools import XmlNanure, ElementTree


def main():  # It's for me, I will delete this soon..
    import os

    path = 'C:\\hard-serwer\\Instance\\Saves\\VanillaHard\\Backup\\'
    path = 'C:\\Users\\lena0\\OneDrive\\Рабочий стол\\test_server\\Instance\\Saves\\Gorila\\Backup\\'
    for i in [f.name for f in os.scandir(path) if f.is_dir()]:
        print(i)

        editor = WorldManager(path + str(i) + '/', rw='w')
        commands = [
            # 'get_grid_names',
            'get_inventory',
            'fix_world',
            'update_trade',
            'check_security']

        editor.execute_commands(commands)
        del editor

        a = 6 / 0


class WorldManager(XmlNanure):
    """reed gamesave. Edit sandbox и SANDBOX worker , had high-levl functions"""

    Sandbox_path = 'Sandbox.sbc'
    SANDBOX_path = 'SANDBOX_0_0_0_.sbs'

    def __init__(self, folder_path, rw='r'):
        print(f'init world edit {folder_path}')
        self.path = folder_path
        self.rw = rw

    def execute_commands(self, commands):
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
                case _:
                    print(f'команды {command} не существует')

        print(f'commands take {time.time() - start_time}')
        # PART WHEN WE SAVE CHANGES
        if self.rw == 'w':
            start_time = time.time()
            self.save_changes()
            print(f'save world take {time.time() - start_time}')

        #del self.SANDBOX.cubegrids
        #del self.SANDBOX
        #del self.sandbox

    def get_grid_names(self):
        """Return custom grids names"""
        for i in self.SANDBOX.cubegrids:
            if 'Grid' not in i.name:
                print(i.name)

    def get_inventory(self):
        """I use to check where wealth flow to another person"""
        keys = {}
        for grid in self.SANDBOX.cubegrids:
            for block in grid.blocks:
                # if block.built_by == '144115188075867343' or block.built_by == '144115188075857675':
                if True:
                    for item in block.get_inventory():
                        if item.subtype == 'Uranium' and item.type == 'MyObjectBuilder_Ingot':
                            keys[block.built_by] = keys.setdefault(block.built_by, 0) + item.amount
        #print(keys)

    def fix_world(self):
        """Fixing most common but noise things"""
        self.sandbox.fix_strongs()
        self.SANDBOX.fix_huv()

    def update_trade(self):  # IN PROGRES
        for grid in self.SANDBOX.cubegrids:
            if '[SIMP]' in grid.name:
                self.id_trade += grid.update_store(self.id_trade)

    def check_security(self):
        """Check who or what play ower ur server laws"""
        self.SANDBOX.check_volume(self.sandbox.id_name)

    def save_changes(self):
        # First save sandbox
        self.sandbox.element_tree.save_tree()
        self.SANDBOX.element_tree.save_tree()
        ElementTree.remove_file(self.path + 'SANDBOX_0_0_0_.sbsB5')

    def test_manager_command(self):
        self.check_security()
        self.get_inventory()


class SandboxWorker:
    """work with raw xml Sandbox.sbc"""

    def __init__(self, path):
        self.element_tree = ElementTree(path)
        self.sector = self.element_tree.tree.getroot()

        # Prepare data
        self.go_through()

    def go_through(self):
        self.id_name = self.get_id_name()
        self.id_trade = self.get_id_trade()

    def get_id_name(self):
        """Return shit person_id: person_name. Useful in high-lvl output"""
        persons = self.sector.find('AllPlayersData').findall('.//item')
        id_name = {}
        for person in persons:
            person_id = int(person.find('Value').find('IdentityId').text)
            person_name = str(person.find('Value').find('DisplayName').text)
            if '' in person_name:
                person_name = person_name[1:]
            id_name[person_id] = person_name
        return id_name

    def fix_strongs(self):
        """fix unknow signals undrop i guess)"""
        for strong in self.sector.findall('.//PlayerContainerData'):
            strong.find('Active').text = 'true'
            strong.find('Competetive').text = 'true'

    def get_id_trade(self):
        """Sometime when u do on restart custom trade offers, u need to know all existing id to not repeet it"""
        id_trade = []
        for item in self.sector.findall('.//MyObjectBuilder_StoreItem'):
            id_trade.append(item.find('Id').text)
        return list(set(id_trade))


class SANDBOXWorker:
    """work with raw xml SANDBOX_0_0_0_.sbc"""

    def __init__(self, path):
        self.element_tree = ElementTree(path)
        self.sector = self.element_tree.tree.getroot()
        # Prepare data
        self.go_through()

    def go_through(self):
        self.id_trade = self.get_id_trade()
        self.cubegrids = []

        sector_objects = self.sector.find('SectorObjects')
        for SectorObject in sector_objects:
            match SectorObject.get('{http://www.w3.org/2001/XMLSchema-instance}type'):
                case 'MyObjectBuilder_Character':
                    pass
                case 'MyObjectBuilder_CubeGrid':
                    self.cubegrids.append(CubeGrid(sector_objects, SectorObject))
                case 'MyObjectBuilder_FloatingObject':
                    if False:
                        try:
                            if SectorObject.find('Item').find('PhysicalContent').find('SubtypeName').text == 'Stone':
                                sector_objects.remove(SectorObject)
                        except TypeError:
                            pass
                case 'MyObjectBuilder_Planet':
                    pass
                case 'MyObjectBuilder_SafeZone':
                    pass
                case 'MyObjectBuilder_VoxelMap':
                    try:
                        if SectorObject.find('StorageName').text[:2] == 'P(':
                            sector_objects.remove(SectorObject)
                    except TypeError:
                        pass
                case 'MyObjectBuilder_InventoryBagEntity':
                    pass
                case _:
                    ex = SectorObject.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                    print(f'к {ex} жизнь меня не готовила')

    def fix_huv(self):
        """If ur world broke, I first check HUV in save. Bad cheaters broke HUV to make ur life bad("""
        for grid in self.cubegrids:
            for block in grid.blocks:
                try:
                    huv = block.block_obj.find('ColorMaskHSV')
                    huvdat = list(block.block_obj.find('ColorMaskHSV').attrib.items())
                    if huvdat[0][1] == 'NaN' or huvdat[1][1] == 'NaN' or huvdat[2][1] == 'NaN':
                        for i in huvdat:
                            huv.set(i[0], '0.1')
                except AttributeError:
                    pass

    def check_volume(self, id_name):
        """On my server ZERG and NECR spam by this infinity volume shit. Now they cant do that silently"""
        for grid in self.cubegrids:
            for block in grid.blocks:
                for component in block.get_components():
                    for volume in component.findall('Volume'):
                        if float(volume.text) > 500:
                            try:
                                owner = 'Player '
                                if block.built_by is not None:
                                    owner = owner + id_name[int(built_by)] + ' '
                                if block.owner is not None:
                                    owner = owner + id_name[int(owner)] + ' '
                                else:
                                    owner = 'IDK_who '
                            except KeyError:
                                owner = 'NPC '
                                if block.built_by is not None:
                                    owner = owner + block.built_by + ' '
                                if block.owner is not None:
                                    owner = owner + block.owner + ' '
                                else:
                                    owner = 'IDK_who '

                            self.to_log('Log.txt',
                                        f'{owner} expand {block.type} with id {block.id} on ' +
                                        f'{volume.text}k liters \n')
                            grid.remove(block)

    def get_id_trade(self):
        """Sometime when u do on restart custom trade offers, u need to know all existing id to not repeet it"""
        id_trade = []
        for item in self.sector.findall('.//MyObjectBuilder_StoreItem'):
            id_trade.append(item.find('Id').text)
        return list(set(id_trade))


class CubeGrid(XmlNanure):
    def __init__(self, parent, grid):
        self.parent = parent
        self.grid_obj = grid
        self.id = self.get_text(grid.find('EntityId'))
        self.gps = self.get_gps()
        self.size = self.get_text(grid.find('GridSizeEnum'))
        self.name = self.get_text(grid.find('DisplayName'))
        self.killable = grid.find('DestructibleBlocks').text == 'true'
        self.blocks = self.get_blocks()

    def get_gps(self):
        """Get GPS"""
        tmp = list(self.grid_obj.find('PositionAndOrientation').find("Position").attrib.items())
        x, y, z = tmp[0][1], tmp[1][1], tmp[2][1]
        # gps=[Names[int(f.find("Owner").text)],x.split(".")[0],y.split(".")[0],z.split(".")[0]]
        return x, y, z

    def get_blocks(self):
        blocks = []
        for block in self.grid_obj.find('CubeBlocks'):
            blocks.append(CubeBlock(self.grid_obj.find('CubeBlocks'), block))
        return blocks

    def update_store(self, id_trade):  # IN PROGRES
        to_update = {'stores': 0, 'resources': {}}
        stores = []
        for block in self.blocks:
            if block.type == 'MyObjectBuilder_CargoContainer':
                for item in block.get_inventory():
                    to_update['resources'][item.subtype] = to_update['resources'].setdefault(item.subtype,
                                                                                             0) + item.amount
            elif block.type == 'MyObjectBuilder_StoreBlock' and block.subtype == 'StoreBlock':
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

    def setstore(self, block, store, shitemsids):  # IN PROGRES
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
            sid = ET.SubElement(bstore, 'Id')  # id
            sid.text = str(tmp)
            sItem = ET.SubElement(bstore, 'Item')
            sItem.set('Type', 'MyObjectBuilder_' + item[1])
            sItem.set('Subtype', item[2].replace('Gravity', 'GravityGenerator').replace('Thruster', 'Thrust'))
            sItemType = ET.SubElement(bstore, 'ItemType')
            sItemType.text = 'PhysicalItem'
            sAmount = ET.SubElement(bstore, 'Amount')
            sAmount.text = str(item[3])
            sRemovedAmount = ET.SubElement(bstore, 'RemovedAmount')
            sRemovedAmount.text = '0'
            sPricePerUnit = ET.SubElement(bstore, 'PricePerUnit')
            sPricePerUnit.text = str(item[4])
            sStoreItemType = ET.SubElement(bstore, 'StoreItemType')
            sStoreItemType.text = 'Offer' if item[0] == 'sell' else 'Order'
            sUpdateCount = ET.SubElement(bstore, 'UpdateCount')
            sUpdateCount.text = '0'
            sPrefabTotalPcu = ET.SubElement(bstore, 'PrefabTotalPcu')
            sPrefabTotalPcu.text = '0'
            sPricePerUnitDiscount = ET.SubElement(bstore, 'PricePerUnitDiscount')
            sPricePerUnitDiscount.text = '0'
        # Надписи
        data = block.find('TextPanelsNew').findall('MySerializedTextPanelData')

        data[0].find('FontSize').text = '3'
        if (tmp := data[0].find('Text')) != None:
            tmp.text = store[1]
        else:
            tmp = ET.SubElement(data[0], 'Text')
            tmp.text = store[1]
        if (tmp := data[0].find('ContentType')) != None:
            tmp.text = 'TEXT_AND_IMAGE'
        else:
            tmp = ET.SubElement(data[0], 'ContentType')
            tmp.text = 'TEXT_AND_IMAGE'

        data[1].find('FontSize').text = '10'
        if (tmp := data[1].find('Text')) != None:
            tmp.text = (store[0] + ' 2 U' if store[0] == 'sell' else store[0] + ' fr U')
        else:
            tmp = ET.SubElement(data[1], 'Text')
            tmp.text = (store[0] + ' 2 U' if store[0] == 'sell' else store[0] + ' fr U')
        if (tmp := data[1].find('ContentType')) != None:
            tmp.text = 'TEXT_AND_IMAGE'
        else:
            tmp = ET.SubElement(data[1], 'ContentType')
            tmp.text = 'TEXT_AND_IMAGE'
        return shitemsids


class CubeBlock(XmlNanure):
    def __init__(self, parent, block):
        self.parent = parent
        self.block_obj = block
        self.type = self.get_xsi(block)
        self.subtype = self.get_text(block.find('SubtypeName'))
        self.id = self.get_text(block.find('EntityId'))
        self.owner = self.get_text(block.find('Owner'))
        self.built_by = self.get_text(block.find('BuiltBy'))
        self.sharemode = self.get_text(block.find('ShareMode'))
        self.name = self.get_text(block.find('CustomName'))

    def get_components(self):
        """Check in file how block looks like to understant what component is"""
        try:
            return self.block_obj.find('ComponentContainer').find('Components')
        except AttributeError:
            return []

    def get_inventory(self):
        items = []
        for component in self.get_components():
            if component.find('TypeId').text == 'MyInventoryBase':
                for inventories in component.findall('.//Items'):
                    for item in inventories.findall('.//MyObjectBuilder_InventoryItem'):
                        items.append(InventoryItem(inventories, item))
        return items


class InventoryItem(XmlNanure):
    def __init__(self, parent, item):
        self.parent = parent
        self.item = item
        self.amount = int(float(item.find('Amount').text))
        self.type = self.get_xsi(item.find('PhysicalContent'))
        self.subtype = self.get_text(item.find('PhysicalContent').find('SubtypeName'))


if __name__ == "__main__":
    main()
