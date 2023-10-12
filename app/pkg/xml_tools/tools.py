import xml.etree.cElementTree as ET
import os


class ElementTree:
    """ElementTree manager"""

    def __init__(self, file_path):
        self.path = file_path
        self.tree = ET.parse(self.path)
        self.create_time = os.path.getctime(file_path)

    def save_tree(self):
        if len(self.path.split('.')) != 2:
            raise ValueError(f'path to file {self.path} and file have to had 1 "."')
        rel_name = self.path
        new_name = self.path.split('.')[-2]+'_new'+'.'+self.path.split('.')[-1]
        old_name = self.path.split('.')[-2]+'_old'+'.'+self.path.split('.')[-1]

        self.tree.write(new_name)
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
