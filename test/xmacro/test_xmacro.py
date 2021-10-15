import unittest
import os
from xmacro.xmacro import XMLMacro

def test_by_file(filename):
    macro=XMLMacro()
    macro.set_xml_file(filename)
    macro.generate()
    xml_str = macro.to_string()
    flag =False
    with open(os.path.splitext(filename)[0], 'r') as f:
        xml_str_gt = f.read()
        flag = (xml_str.strip() == xml_str_gt.strip()) 
    return flag

class TestXMLMacro(unittest.TestCase):
    def test_xmacro_value(self):
        flag = test_by_file("test_xmacro_value.xml.xmacro")
        self.assertEqual(flag, True)
    def test_xmacro_block(self):
        flag = test_by_file("test_xmacro_block.xml.xmacro")
        self.assertEqual(flag, True)
    def test_xmacro_include(self):
        flag = test_by_file("test_xmacro_include.xml.xmacro")
        self.assertEqual(flag, True)
    def test_xmacro_condition(self):
        flag = test_by_file("test_xmacro_condition.xml.xmacro")
        self.assertEqual(flag, True)
if __name__ == '__main__':
    unittest.main()