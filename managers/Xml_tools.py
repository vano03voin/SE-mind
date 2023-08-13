import xml.etree.ElementTree as ET
import os


class XmlNanure:
    """Methods for xml family obj's"""

    @staticmethod
    def to_log(where, what):
        with open(where, 'a', encoding="utf-8", newline='') as f:
            print(what)
            f.write(what)

    @staticmethod
    def get_xsi(element):
        return element.get('{http://www.w3.org/2001/XMLSchema-instance}type')

    @staticmethod
    def get_text(element):
        try:
            return element.text
        except AttributeError:
            return None


class ElementTree:
    """ElementTree manager"""

    def __init__(self, file_path):
        self.path = file_path
        self.tree = ET.parse(self.path)

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

