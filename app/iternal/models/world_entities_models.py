from dataclasses import dataclass

from datetime import datetime
from typing import Tuple, Optional
import xml.etree.ElementTree as ET


@dataclass
class XML:

    xml_parent: Optional[ET.Element]
    xml_sourse: Optional[ET.Element]


@dataclass
class XYZ:

    x: int
    y: int
    z: int


@dataclass
class InventoryItem:

    item_type: str
    item_subtype: str
    amount: int


@dataclass
class CubeBlock:

    xml_parent: Optional[ET.Element]
    xml_sourse: Optional[ET.Element]

    b_id: Optional[int]
    b_type: str
    b_subtype: Optional[str]
    b_builder_id: Optional[int]
    b_owner_id: Optional[int]
    b_share_mode: Optional[str]
    b_logic_components: dict

    def __getstate__(self):
        attributes = self.__dict__.copy()

        key_to_send = [
            'block_id',
            'block_type',
            'subtype',
            'build_by',
            'owner_id',
            'share_mode',
            'components'
        ]
        #print(attributes)
        return attributes

    def get_inventory(self):
        #print(self.b_logic_components)
        return self.b_logic_components.get('MyInventoryBase', {}).get('items', [])


@dataclass
class Entity(XML):

    e_type: str
    e_subtype: Optional[str] = None
    e_id: Optional[int] = None
    e_gps: XYZ = XYZ(0, 0, 0)
    e_name: Optional[str] = None


@dataclass
class Grid(Entity):

    g_size: Optional[str]
    g_static: Optional[bool]
    g_killable: Optional[bool]
    g_blocks: list[CubeBlock]


@dataclass
class SafeZone(Entity):

    safe_zone_block_id: Optional[int]
    shape: str
    radius: int
    size: XYZ
    enabled: bool


class VoxelMap(Entity):

    voxel_type: str
    by_user: bool


class Character(Entity):

    model: str
    owner_id: int
    components: dict


class FloatingObject(Entity):

    components: dict


class Planet(Entity):

    radius: int
    min: int


class InventoryBagEntity(Entity):

    inventory_type: str
    owner_id: int
    components: dict


# Sandbox schemes


class FactionMember:

    member_id: int
    is_leader: bool
    is_founder: bool


class Faction:

    faction_id: int
    tag: str
    name: str
    members: list[FactionMember]
    faction_type: str
    balance: int


class GPS:

    name: str
    coordinates: XYZ
