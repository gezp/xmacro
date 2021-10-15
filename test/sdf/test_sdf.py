import unittest
import os
from xmacro.xmacro4sdf import XMLMacro4sdf

def test_by_file(filename):
    macro=XMLMacro4sdf()
    macro.set_xml_file(filename)
    macro.generate()
    xml_str = macro.to_string()
    flag =False
    with open(os.path.splitext(filename)[0], 'r') as f:
        xml_str_gt = f.read()
        flag = (xml_str.strip() == xml_str_gt.strip()) 
    return flag

class TestXMLMacro(unittest.TestCase):
    def test_model(self):
        flag = test_by_file("model.sdf.xmacro")
        self.assertEqual(flag, True)
    def test_model2(self):
        flag = test_by_file("model2.sdf.xmacro")
        self.assertEqual(flag, True)
    def test_model3(self):
        flag = test_by_file("model3.sdf.xmacro")
        self.assertEqual(flag, True)
if __name__ == '__main__':
    unittest.main()