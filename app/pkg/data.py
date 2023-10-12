import xml.etree.ElementTree as ET


class EntityBuilder:
    @classmethod
    def create_from_xml(cls, xml_parent: ET.Element, xml_sourse: ET.Element):
        match e_type:
            case 'MyObjectBuilder_Character':
                pass
            case 'MyObjectBuilder_CubeGrid':
                pass
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
                print(f'for entity {e_type} life dont prepare me')


block_invnt = ['MyObjectBuilder_Assembler',  # 24
               'MyObjectBuilder_CargoContainer',
               'MyObjectBuilder_Cockpit',
               'MyObjectBuilder_Collector',
               'MyObjectBuilder_ConveyorSorter',
               'MyObjectBuilder_CryoChamber',
               'MyObjectBuilder_CubeBlock',
               'MyObjectBuilder_Drill',
               'MyObjectBuilder_InteriorTurret',
               'MyObjectBuilder_LargeGatlingTurret',
               'MyObjectBuilder_LargeMissileTurret',
               'MyObjectBuilder_OxygenGenerator',
               'MyObjectBuilder_OxygenTank',
               'MyObjectBuilder_Parachute',
               'MyObjectBuilder_Reactor',
               'MyObjectBuilder_Refinery',
               'MyObjectBuilder_SafeZoneBlock',
               'MyObjectBuilder_ShipConnector',
               'MyObjectBuilder_ShipGrinder',
               'MyObjectBuilder_ShipWelder',
               'MyObjectBuilder_SmallGatlingGun',
               'MyObjectBuilder_SmallMissileLauncher',
               'MyObjectBuilder_SmallMissileLauncherReload',
               'MyObjectBuilder_StoreBlock',
               'MyObjectBuilder_SurvivalKit']

block_types = ['MyObjectBuilder_AirVent',  # 90 шт.
               'MyObjectBuilder_AirtightHangarDoor',
               'MyObjectBuilder_AirtightSlideDoor',
               'MyObjectBuilder_Assembler',
               'MyObjectBuilder_BasicMissionBlock',
               'MyObjectBuilder_BatteryBlock',
               'MyObjectBuilder_Beacon',
               'MyObjectBuilder_ButtonPanel',
               'MyObjectBuilder_CameraBlock',
               'MyObjectBuilder_CargoContainer',
               'MyObjectBuilder_Cockpit',
               'MyObjectBuilder_Collector',
               'MyObjectBuilder_ContractBlock',
               'MyObjectBuilder_Conveyor',
               'MyObjectBuilder_ConveyorConnector',
               'MyObjectBuilder_ConveyorSorter',
               'MyObjectBuilder_CryoChamber',
               'MyObjectBuilder_CubeBlock',
               'MyObjectBuilder_Decoy',
               'MyObjectBuilder_DefensiveCombatBlock',
               'MyObjectBuilder_Door',
               'MyObjectBuilder_Drill',
               'MyObjectBuilder_EmissiveBlock',
               'MyObjectBuilder_EventControllerBlock',
               'MyObjectBuilder_ExhaustBlock',
               'MyObjectBuilder_ExtendedPistonBase',
               'MyObjectBuilder_FlightMovementBlock',
               'MyObjectBuilder_GravityGenerator',
               'MyObjectBuilder_Gyro',
               'MyObjectBuilder_HeatVentBlock',
               'MyObjectBuilder_HydrogenEngine',
               'MyObjectBuilder_InteriorLight',
               'MyObjectBuilder_InteriorTurret',
               'MyObjectBuilder_Jukebox',
               'MyObjectBuilder_JumpDrive',
               'MyObjectBuilder_Kitchen',
               'MyObjectBuilder_LCDPanelsBlock',
               'MyObjectBuilder_Ladder2',
               'MyObjectBuilder_LandingGear',
               'MyObjectBuilder_LargeGatlingTurret',
               'MyObjectBuilder_LargeMissileTurret',
               'MyObjectBuilder_LaserAntenna',
               'MyObjectBuilder_MedicalRoom',
               'MyObjectBuilder_MergeBlock',
               'MyObjectBuilder_MotorAdvancedRotor',
               'MyObjectBuilder_MotorAdvancedStator',
               'MyObjectBuilder_MotorRotor',
               'MyObjectBuilder_MotorStator',
               'MyObjectBuilder_MotorSuspension',
               'MyObjectBuilder_MyProgrammableBlock',
               'MyObjectBuilder_OffensiveCombatBlock',
               'MyObjectBuilder_OreDetector',
               'MyObjectBuilder_OxygenFarm',
               'MyObjectBuilder_OxygenGenerator',
               'MyObjectBuilder_OxygenTank',
               'MyObjectBuilder_Parachute',
               'MyObjectBuilder_Passage',
               'MyObjectBuilder_PathRecorderBlock',
               'MyObjectBuilder_PistonTop',
               'MyObjectBuilder_Planter',
               'MyObjectBuilder_Projector',
               'MyObjectBuilder_RadioAntenna',
               'MyObjectBuilder_Reactor',
               'MyObjectBuilder_Refinery',
               'MyObjectBuilder_ReflectorLight',
               'MyObjectBuilder_RemoteControl',
               'MyObjectBuilder_SafeZoneBlock',
               'MyObjectBuilder_Searchlight',
               'MyObjectBuilder_SensorBlock',
               'MyObjectBuilder_ShipConnector',
               'MyObjectBuilder_ShipGrinder',
               'MyObjectBuilder_ShipWelder',
               'MyObjectBuilder_SmallGatlingGun',
               'MyObjectBuilder_SmallMissileLauncher',
               'MyObjectBuilder_SmallMissileLauncherReload',
               'MyObjectBuilder_SolarPanel',
               'MyObjectBuilder_SoundBlock',
               'MyObjectBuilder_SpaceBall',
               'MyObjectBuilder_StoreBlock',
               'MyObjectBuilder_SurvivalKit',
               'MyObjectBuilder_TerminalBlock',
               'MyObjectBuilder_TextPanel',
               'MyObjectBuilder_Thrust',
               'MyObjectBuilder_TimerBlock',
               'MyObjectBuilder_TurretControlBlock',
               'MyObjectBuilder_UpgradeModule',
               'MyObjectBuilder_VendingMachine',
               'MyObjectBuilder_Warhead',
               'MyObjectBuilder_Wheel',
               'MyObjectBuilder_WindTurbine']
