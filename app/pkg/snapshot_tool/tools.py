import asyncio
import datetime
import os

from typing import Set

from app.pkg.server_tools.tools import Server
from app.pkg.network_tools.tools import ServerHerald
from app.pkg.world_tools.tools import WorldManager


from datetime import datetime
from pydantic import BaseModel, BaseConfig
from typing import Tuple, Literal, Optional


class XYZ(BaseModel):
    x: float
    y: float
    z: float

    def get_gps_mark(self, gps_name):
        return str(f'GPS:{gps_name}:{self.x}:{self.y}:{self.z}:')

    def get_like_list(self):
        return [self.x, self.y, self.z]


class Entity(BaseModel):

    id: int
    gps: XYZ
    name: str


class Grid(Entity):

    inventory: dict
    grid_size: Literal['Large', 'Small']
    is_static: bool
    killable: bool
    owners: dict


class Character(Entity):

    model: str
    owner_id: int
    inventory: dict


class FloatingObject(Entity):

    inventory: dict


class InventoryBagEntity(Entity):

    owner_id: int
    inventory: dict


# Sandbox schemes
class FactionMember(BaseModel):

    id: int
    leader: bool
    founder: bool


class Faction(BaseModel):

    id: int
    tag: str
    name: str
    balance: int
    members: list[FactionMember]


class GPS(BaseModel):

    name: str
    coordinates: XYZ


class Player(BaseModel):

    id: int
    name: str
    last_deth_gps: Optional[XYZ]
    get_connected: bool
    admin: bool
    balance: int
    gps_list: list[Optional[GPS]]


from pydantic import BaseModel

class GameSaveModel(BaseModel):

    save_date: datetime
    session_name: str

    grids: Tuple[Optional[Grid], ...]
    characters: Tuple[Optional[Character], ...]
    floating_objects: Tuple[Optional[FloatingObject], ...]
    inventory_bags: Tuple[Optional[InventoryBagEntity], ...]

    factions: Tuple[Optional[Faction], ...]
    players: Tuple[Optional[Player], ...]

    class ConfigDict(BaseConfig):
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


from datetime import datetime
from typing import Tuple, Optional, List

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()
class GameSave(Base):
    __tablename__ = 'game_save'

    id: Mapped[int] = mapped_column(primary_key=True)
    server_id: Mapped[int] = mapped_column(default=1)
    world_id: Mapped[str]
    save_date: Mapped[datetime] = mapped_column(unique=True)
    session_name: Mapped[str]

    grids: Mapped[Tuple[Optional[Grid], ...]] = mapped_column(JSONB)
    characters: Mapped[Tuple[Optional[Character], ...]] = mapped_column(JSONB)
    floating_objects: Mapped[Tuple[Optional[FloatingObject], ...]] = mapped_column(JSONB)
    inventory_bags: Mapped[Tuple[Optional[InventoryBagEntity], ...]] = mapped_column(JSONB)

    factions: Mapped[Tuple[Optional[Faction], ...]] = mapped_column(JSONB)
    players: Mapped[Tuple[Optional[Player], ...]] = mapped_column(JSONB)


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres"
DATABASE_URL = "sqlite+aiosqlite:///./SQLite.db"

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError


engine = create_async_engine(url=DATABASE_URL, echo=True)
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async_session_for_tests_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_call_file(session: AsyncSession, data: GameSaveModel):
    call_file = GameSave(**data)

    #engine = create_engine("postgresql://postgres:postgres@localhost/postgres")
    engine = create_engine("sqlite+aiosqlite:///./SQLite.db")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            session.add(call_file)
            session.commit()
            print('комит прошол')
    except IntegrityError:
        print('такой файл есть уже')

    return call_file

async def snapshots_loop(servers: Set[Server], api_key: str):
    while True:
        for server in servers:
            world_master = WorldManager(server.get_save_path(), rw='r')
            world_master.execute_commands(commands=['send_dump_to_server'])
            # print(world_master.gamesave_dict)
            with open('example.txt', mode='w', encoding='utf-8') as f:
                f.write(world_master.gamesave_dict)
            await asyncio.sleep(0)
        # for server in servers:
        #     last_save_on_server = await ServerHerald.get_last_save(server.world_id)
        #     for save in server.get_backup_path_list():
        #         if datetime.datetime.fromtimestamp(os.path.getctime(save + 'Sandbox.sbc')) > last_save_on_server:
        #             world_master = WorldManager(save, rw='r')
        #             world_master.execute_commands(commands=['send_dump_to_server'])
        #             await ServerHerald.send_save(world_master.gamesave_dict)
        #             del world_master
        #         await asyncio.sleep(0)
        await asyncio.sleep(60 * 2)

async def snapshots_loop(servers: Set[Server], api_key: str):
    while True:
        for server in servers:
            for save in server.get_backup_path_list():
                world_master = WorldManager(save, rw='r')
                world_master.execute_commands(commands=['send_dump_to_server'])
                import json
                with open('example.txt', mode='w', encoding='utf-8') as f:
                    f.write(json.dumps(world_master.gamesave_dict))

                #orm_model = GameSaveModel(**world_master.gamesave_dict)

                await create_call_file(async_session_for_tests_maker(), world_master.gamesave_dict)

            a = 1/0