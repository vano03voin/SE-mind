import xml.etree.ElementTree as ET
import os


def main():  # its for me, i will delete this soon..
    path = 'C:\\hard-serwer\\Instance\\Saves\\VanillaHard\\Backup\\'
    #path = ''
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


class XmlLike:
    """Useful things"""

    @staticmethod
    def get_xsi(element):
        return element.get('{http://www.w3.org/2001/XMLSchema-instance}type')

    @staticmethod
    def get_text(element):
        try:
            return element.text
        except AttributeError:
            return None

    @staticmethod
    def to_log(where, what):
        with open(where, 'a', encoding="utf-8", newline='') as f:
            print(what)
            f.write(what)


class WorldManager(XmlLike):
    """reed gamesave. Edit sandbox и SANDBOX worker , had high-levl functions"""

    Sandbox_path = 'Sandbox.sbc'
    SANDBOX_path = 'SANDBOX_0_0_0_.sbs'

    def __init__(self, folder_path, rw='r'):
        self.path = folder_path
        self.rw = rw

    def execute_commands(self, commands):
        self.sandbox = SandboxWorker(self.path + self.Sandbox_path)
        self.SANDBOX = SANDBOXWorker(self.path + self.SANDBOX_path)
        
        # Prepare useful data before ur's custom code
        self.sandbox.go_through()
        self.SANDBOX.go_through()
        self.id_trade = self.sandbox.id_trade + self.SANDBOX.id_trade

        for command in commands:
            match command:
                case 'get_grid_names':
                    self.get_grid_names()
                case 'get_inventory':
                    self.get_inventory()
                case 'fix_world':
                    if self.rw == 'w':
                        self.fix_world()
                case 'update_trade':
                    if self.rw == 'w':
                        self.update_trade()
                case 'check_security':
                    if self.rw == 'w':
                        self.check_security()
                case _:
                    print(f'команды {command} не существует')

        # PART WHEN WE SAVE CHANGES
        if self.rw == 'w':
            self.save_changes()

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
        print(keys)

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
        self.sandbox.tree.write(self.path + "Sandbox_New.sbc", xml_declaration=True)
        try:
            os.remove(self.path + 'Sandbox_Old.sbc')
        except:
            pass
        os.rename(self.path + 'Sandbox.sbc', self.path + 'Sandbox_Old.sbc')
        os.rename(self.path + 'Sandbox_New.sbc', self.path + 'Sandbox.sbc')

        # Now save SANDBOX
        self.SANDBOX.tree.write(self.path + "SANDBOX_0_0_0__New.sbs", xml_declaration=True)
        try:
            os.remove(self.path + 'SANDBOX_0_0_0__Old.sbs')
        except:
            pass
        os.rename(self.path + 'SANDBOX_0_0_0_.sbs', self.path + "SANDBOX_0_0_0__Old.sbs")
        os.rename(self.path + "SANDBOX_0_0_0__New.sbs", self.path + 'SANDBOX_0_0_0_.sbs')
        try:
            os.remove(self.path + 'SANDBOX_0_0_0_.sbsB5')
        except:
            pass


class Worker(XmlLike):
    """Put DRY code in single obj"""

    def __init__(self, path):
        self.path = path
        self.tree = ET.parse(path)
        self.sector = self.tree.getroot()

    def get_id_trade(self):
        """Sometime when u do on restart custom trade offers, u need to know all existing id to not repeet it"""
        id_trade = []
        for item in self.sector.findall('.//MyObjectBuilder_StoreItem'):
            id_trade.append(item.find('Id').text)
        return list(set(id_trade))


class SandboxWorker(Worker):
    """work with raw xml Sandbox.sbc"""

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


class SANDBOXWorker(Worker):
    """work with raw xml SANDBOX_0_0_0_.sbc"""

    def go_through(self):
        self.id_trade = self.get_id_trade()
        self.cubegrids = []

        sector_objects = self.sector.find('SectorObjects')
        for SectorObject in sector_objects:
            match SectorObject.get('{http://www.w3.org/2001/XMLSchema-instance}type'):
                case 'MyObjectBuilder_Character':
                    pass
                case 'MyObjectBuilder_CubeGrid':
                    self.cubegrids.append(self.CubeGrid(sector_objects, SectorObject))
                case 'MyObjectBuilder_FloatingObject':
                    pass
                case 'MyObjectBuilder_Planet':
                    pass
                case 'MyObjectBuilder_SafeZone':
                    pass
                case 'MyObjectBuilder_VoxelMap':
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

    class CubeGrid(XmlLike):
        def __init__(self, parent, grid):
            self.parent = parent
            self.grid_obj = grid
            self.id = self.get_text(grid.find('EntityId'))
            self.gps = self.get_gps()
            self.size = self.get_text(grid.find('GridSizeEnum'))
            self.name = self.get_text(grid.find('DisplayName'))
            self.killable = grid.find('DestructibleBlocks').text == 'true'
            self.blocks = self.get_blocks(self.grid_obj.find('CubeBlocks'))

        def get_gps(self):
            """Get GPS"""
            tmp = list(self.grid_obj.find('PositionAndOrientation').find("Position").attrib.items())
            x, y, z = tmp[0][1], tmp[1][1], tmp[2][1]
            # gps=[Names[int(f.find("Owner").text)],x.split(".")[0],y.split(".")[0],z.split(".")[0]]
            return x, y, z

        def get_blocks(self, parent):
            blocks = []
            for block in parent:
                blocks.append(self.CubeBlock(parent, block))
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
            return []

        class CubeBlock(XmlLike):
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
                                items.append(self.InventoryItem(inventories, item))
                return items

            class InventoryItem(XmlLike):
                def __init__(self, parent, item):
                    self.parent = parent
                    self.item = item
                    self.amount = int(float(item.find('Amount').text))
                    self.type = self.get_xsi(item.find('PhysicalContent'))
                    self.subtype = self.get_text(item.find('PhysicalContent').find('SubtypeName'))


if __name__ == "__main__":
    main()
