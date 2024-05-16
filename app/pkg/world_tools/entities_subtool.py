import copy
from functools import cache


class XYZ:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_gps_mark(self, gps_name):
        return str(f'GPS:{gps_name}:{self.x}:{self.y}:{self.z}:')

    def get_like_list(self):
        return {'x': self.x, 'y': self.y, 'z': self.z}


class IAmXML:
    def __init__(self, xml_source):
        self.xml_source = xml_source


class Entity(IAmXML):
    @classmethod
    def create_entity(cls, xml_source):
        entity_type = xml_source.get('{http://www.w3.org/2001/XMLSchema-instance}type')
        match entity_type:
            case 'MyObjectBuilder_Character':
                return Character(xml_source)
            case 'MyObjectBuilder_CubeGrid':
                return CubeGrid(xml_source)
            case 'MyObjectBuilder_FloatingObject':
                return FloatingObject(xml_source)
            case 'MyObjectBuilder_Planet':
                return Planet(xml_source)
            case 'MyObjectBuilder_SafeZone':
                return SafeZone(xml_source)
            case 'MyObjectBuilder_VoxelMap':
                return VoxelMap(xml_source)
            case 'MyObjectBuilder_InventoryBagEntity':
                return InventoryBagEntity(xml_source)
            case _:
                print(f'for entity {entity_type} life dont prepare me')

    def get_type(self):
        return self.xml_source.get('{http://www.w3.org/2001/XMLSchema-instance}type')

    def get_subtype(self):
        if (subtype := self.xml_source.find('SubtypeName')) is not None:
            return subtype.text

    def get_id(self) -> str | None:
        if (e_id := self.xml_source.find('EntityId')) is not None:
            return e_id.text

    def get_xyz(self):
        if (gps_sourse := self.xml_source.find('PositionAndOrientation')) is not None:
            tmp = list(gps_sourse.find("Position").attrib.items())
            x, y, z = float(tmp[0][1]), float(tmp[1][1]), float(tmp[2][1])
            return XYZ(int(x), int(y), int(z))

    def get_name(self):
        if (e_name := self.xml_source.find('DisplayName')) is not None:
            return str(e_name.text)
        if (e_name := self.xml_source.find('CustomName')) is not None:
            return str(e_name.text)
        if (e_name := self.xml_source.find('Name')) is not None:
            return str(e_name.text)
        if (e_name := self.xml_source.find('EntityId')) is not None:
            return str(e_name.text)


class CubeBlock(Entity):
    def get_builder_id(self):
        if (b_builder_id := self.xml_source.find('BuiltBy')) is not None:
            return b_builder_id.text

    def get_owner_id(self):
        if (b_owner_id := self.xml_source.find('Owner')) is not None:
            return b_owner_id.text

    def get_share_mode(self):
        if (share_mode := self.xml_source.find('ShareMode')) is not None:
            return share_mode.text

    def get_inventory(self) -> dict:
        items = {}
        components_path = 'ComponentContainer/Components/ComponentData/Component/'
        if (items_source := self.xml_source.find(components_path + 'Items')) is not None:
            for item in items_source:
                InventoryItem.merge_inv(items, InventoryItem.get_name_amount(item))
        if (items_source := self.xml_source.find(components_path + 'Inventories')) is not None:
            for inventory in items_source:
                for item in inventory.find('Items'):
                    InventoryItem.merge_inv(items, InventoryItem.get_name_amount(item))
        return items

    def get_who_own(self):
        if self.get_builder_id():
            return self.get_builder_id()
        if self.get_owner_id():
            return self.get_owner_id()

    def is_inventory(self):
        components_path = 'ComponentContainer/Components/ComponentData/Component/'
        if self.xml_source.find(components_path + 'Items') or self.xml_source.find(components_path + 'Inventories'):
            return True


class CubeGrid(Entity):
    def get_size(self):
        return self.xml_source.find('GridSizeEnum').text

    def get_static(self):
        if (g_static := self.xml_source.find('IsStatic')) is not None:
            return True if g_static.text == 'true' else False
        return False

    def get_killable(self):
        return True if self.xml_source.find('DestructibleBlocks').text else False

    def get_blocks(self) -> list[CubeBlock]:
        blocks = []
        blocks_source = self.xml_source.find('CubeBlocks')
        for block in blocks_source:
            blocks.append(CubeBlock(block))
        return blocks

    def get_inventory(self):
        items = {}
        for inventory in [block.get_inventory() for block in self.get_blocks()]:
            InventoryItem.merge_inv(items, inventory)
        return items

    def get_inventory_and_owners(self):
        owner_inventory = {}
        for block in self.get_blocks():
            if block.is_inventory():
                InventoryItem.merge_inv(owner_inventory.setdefault(block.get_who_own(), {}), block.get_inventory())
        return copy.deepcopy(owner_inventory)

    def get_ownership(self) -> dict[str: int]:
        owners = {}
        for block in self.get_blocks():
            owners[block.get_who_own()] = owners.get(block.get_who_own(), 0) + 1
        return owners

    def get_hydrogen(self) -> dict[str:]:
        hydrogen_types = {
            'large_grid': {
                'large_tank': 0,
                'small_tank': 0
            },
            'small_grid': {
                'large_tank': 0,
                'small_tank': 0
            },
            'liters': 0
        }

        grid_type = 'large_grid' if self.get_size() == 'Large' else 'small_grid'

        def get_block_size(block: CubeBlock) -> str:
            if 'Large' in block.get_subtype():
                return 'large_tank'
            return 'small_tank'

        for block in self.get_blocks():
            if block.get_type() == 'MyObjectBuilder_OxygenTank' and 'Hydrogen' in str(block.get_subtype()):
                hydrogen_types[grid_type][get_block_size(block)] += float(block.xml_source.find('FilledRatio').text)
            if block.get_type() == 'MyObjectBuilder_HydrogenEngine':
                hydrogen_types['liters'] += float(block.xml_source.find('Capacity').text)
        return hydrogen_types

    def to_json(self):
        blocks = {}
        for block in self.get_blocks():
            block_name = f'{block.get_type()} {block.get_subtype()}'
            blocks[block_name] = blocks.setdefault(block_name, 0) + 1

        grid_dict = {'id': self.get_id(),
                     'gps': self.get_xyz().get_like_list(),
                     'name': self.get_name(),
                     'inventory': self.get_inventory_and_owners(),
                     'grid_size': self.get_size(),
                     'is_static': self.get_static(),
                     'killable': self.get_killable(),
                     'owners': self.get_ownership(),
                     # 'hydrogen': self.get_hydrogen()
                     # 'blocks': blocks
                     }
        return grid_dict


class InventoryItem:
    @classmethod
    def get_name_amount(cls, xml_source) -> dict:
        i_type = xml_source.find('PhysicalContent').get('{http://www.w3.org/2001/XMLSchema-instance}type')
        i_subtype = xml_source.find('PhysicalContent').find('SubtypeName').text
        amount = int(float(xml_source.find('Amount').text))
        name = f'{i_type} {i_subtype}'
        return {name: amount}

    @classmethod
    def get_type_subtype_amount(cls, xml_source):
        i_type = xml_source.find('PhysicalContent').get('{http://www.w3.org/2001/XMLSchema-instance}type')
        i_subtype = xml_source.find('PhysicalContent').find('SubtypeName').text
        amount = int(float(xml_source.find('Amount').text))
        return i_type, i_subtype, amount

    @classmethod
    def merge_inv(cls, inv_main: dict, inv_sub: dict):
        for name, amount in inv_sub.items():
            inv_main[name] = inv_main.get(name, 0) + amount


class SafeZone(Entity):
    def get_block_id(self):
        return self.xml_source.find('SafeZoneBlockId').text

    def get_shape(self):
        return self.xml_source.find('Shape').text

    def get_size(self):
        if self.get_shape() == 'Sphere':
            return float(self.xml_source.find('Radius').text)
        else:
            size = self.xml_source.find('Size')
            return float(size.find('X').text), float(size.find('Y').text), float(size.find('Z').text)

    def get_is_enabled(self):
        return self.xml_source.find('Enabled').text

    def to_json(self):
        zone_dict = {
            'id': self.get_id(),
            'gps': self.get_xyz().get_like_list(),
            'name': self.get_name(),
            'shape': self.get_shape(),
            'size': self.get_size(),
            'enabled': self.get_is_enabled()
        }
        return zone_dict


class VoxelMap(Entity):
    def get_voxel_type(self):
        return self.xml_source.find('StorageName').text

    def get_by_user(self):
        return self.xml_source.find('CreatedByUser').text != 'false'

    def to_json(self):
        voxel_dict = {
            'id': self.get_id(),
            'gps': self.get_xyz().get_like_list(),
            'name': self.get_name(),
            'voxel_type': self.get_voxel_type(),
            'by_user': self.get_by_user()
        }
        return voxel_dict


class Character(Entity):
    def get_model(self):
        return self.xml_source.find('CharacterModel').text

    def get_owner_id(self):
        return self.xml_source.find('OwningPlayerIdentityId').text

    def get_inventory(self):
        items = {}
        for item in self.xml_source.find('Inventory/Items'):
            InventoryItem.merge_inv(items, InventoryItem.get_name_amount(item))
        return items

    def to_json(self):
        character_dict = {
            'id': self.get_id(),
            'gps': self.get_xyz().get_like_list(),
            'name': self.get_name() if r'\ue030' in self.get_name() else self.get_name()[1:],
            'model': self.get_model(),
            'owner_id': self.get_owner_id(),
            'inventory': self.get_inventory()
        }
        return character_dict


class FloatingObject(Entity):
    def get_inventory(self):
        items = {}
        return InventoryItem.get_name_amount(self.xml_source.find('Item'))

    def to_json(self):
        float_dict = {
            'id': self.get_id(),
            'gps': self.get_xyz().get_like_list(),
            'name': self.get_name(),
            'inventory': self.get_inventory()
        }
        return float_dict


class Planet(Entity):
    def get_radius(self):
        return float(self.xml_source.find('Radius').text)

    def get_min_hieght(self):
        return int(float(self.xml_source.find('MinimumSurfaceRadius').text))

    def get_max_hieght(self):
        return int(float(self.xml_source.find('MinimumSurfaceRadius').text))

    def to_json(self):
        planet_dict = {
            'id': self.get_id(),
            'gps': self.get_xyz().get_like_list(),
            'name': self.get_name(),
            'radius': self.get_radius(),
            'min_hieght': self.get_min_hieght(),
            'max_hieght': self.get_max_hieght()
        }
        return planet_dict


class InventoryBagEntity(Entity):
    def get_owner(self):
        return self.xml_source.find('OwnerIdentityId').text

    def get_inventory(self):
        items = {}
        components_path = 'ComponentContainer/Components/ComponentData/Component/'
        if (items_source := self.xml_source.find(components_path + 'Items')) is not None:
            for item in items_source:
                InventoryItem.merge_inv(items, InventoryItem.get_name_amount(item))
        return items

    def to_json(self):
        bag_dict = {
            'id': self.get_id(),
            'gps': self.get_xyz().get_like_list(),
            'name': self.get_name(),
            'owner_id': self.get_owner(),
            'inventory': self.get_inventory()
        }
        return bag_dict
