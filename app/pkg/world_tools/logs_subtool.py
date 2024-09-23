import re

from datetime import datetime, timedelta

logs = [
    "02:00:03.5372 [INFO]   Cerber [On][КОС]          with CharacterTool  changed owner on block MotorAdvancedStator  from Cerber [On][КОС]          to Nobody               on grid: Cerber_База_Лед Location: -165,686.1, -2,356,796.7, 415,166.8",
    "02:00:24.1283 [INFO]   Cerber [On][КОС]          with CharacterTool  changed owner on block Cockpit              from Max [On][KEK]          to Nobody               on grid: Cerber_База_Лед Location: -165,672.1, -2,356,793.6, 415,162.6"
]

class OwnershipLog:
    ownership_path = 'Logs/'

    @staticmethod
    def get_json_for_sending(date: datetime, raw_path: str, previous_save_minutes: min):
        a = timedelta(minutes=previous_save_minutes)
        #with open(raw_path[:]) as file:
        if True:
            final = []
            #for line in file.readlines():
            return (None, )
            for line in logs:
                log_time = line[:8].split(':')
                time = datetime(year=date.year, month=date.month, day=date.day, hour=int(log_time[0]), minute=int(log_time[1]), second=int(log_time[2]))
                if (date - time) < a and time < date and 'with' in line:
                    pattern = r"(\d{2}:\d{2}:\d{2})\.\d+\s+\[INFO\]\s+(\w+)\s+\[On\]\[([\wА-Яа-я]+)\].+with\s(\w+)\s+changed owner on block (\w+)\s+from\s+(\w+)\s+\[On\]\[([\wА-Яа-я]+)\]\s+to\s+(\w+)\s+on grid:\s+([\wА-Яа-я_]+)\s+Location:\s+([-?\d,\.]+),\s+([-?\d,\.]+),\s+([-?\d,\.]+)"

                    match = re.search(pattern, line)
                    print(match)

                    if match:
                        time_2 = match.group(1)
                        name1 = match.group(2)
                        faction1 = match.group(3)
                        by = match.group(4)
                        block = match.group(5)
                        name2 = match.group(6)
                        faction2 = match.group(7)
                        grid_name = match.group(9)
                        x = match.group(10).replace(",", "").split('.')[0]
                        y = match.group(11).replace(",", "").split('.')[0]
                        z = match.group(12).replace(",", "").split('.')[0]

                        if name1 != name2 and 'Planet' not in name1 and faction2 != faction1 and 'Nobody' not in name1 and 'Nobody' not in name2 and 'Space Pirates [Off][SPRT]' not in name1 and 'Space Pirates [Off][SPRT]' not in name2:
                            final.append({
                                'date': time,
                                'actor': name1,
                                'by': by,
                                'block': block,
                                'victim': name2,
                                'grid': grid_name,
                                'gps': {'x': int(x),'y': int(y), 'z': int(z)}
                            })
        return final

    # Пример использования
#print(OwnershipLog.get_json_for_sending(datetime.now().replace(hour=2, minute=5), r'C:\Users\lena0\OneDrive\Рабочий стол\ownerships-2023-05-21.log', 15))

