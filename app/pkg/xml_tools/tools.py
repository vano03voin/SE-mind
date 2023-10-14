import xml.etree.cElementTree as ET
import os


class ElementTree:
    """ElementTree manager"""

    def __init__(self, file_path):
        self.path = file_path
        self.tree = ET.parse(self.path)
        self.create_time = os.path.getctime(file_path)

    def save_tree(self):
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        self.tree.getroot().attrib[f'{{{xsi}}}:xsd'] = "http://www.w3.org/2001/XMLSchema"
        if len(self.path.split('.')) != 2:
            raise ValueError(f'path to file {self.path} and file have to had 1 "."')
        rel_name = self.path
        new_name = self.path.split('.')[-2]+'_new'+'.'+self.path.split('.')[-1]
        old_name = self.path.split('.')[-2]+'_old'+'.'+self.path.split('.')[-1]

        self.tree.write(new_name, encoding='utf-8', xml_declaration=True)
        try:
            os.remove(old_name)
        except:
            pass
        os.rename(rel_name, old_name)
        os.rename(new_name, rel_name)

    @staticmethod
    def remove_file(file_path):
        try:
            os.remove(file_path)
        except:
            pass
