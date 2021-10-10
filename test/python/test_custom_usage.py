#!/bin/python3
from xmacro.xmacro import XMLMacro

xmacro=XMLMacro()
#case1 parse from file
xmacro.set_xml_file("../test_xmacro.xml.xmacro")
custom_kv={"v1":0.8}
xmacro.generate(custom_kv)
xmacro.to_file("custom.xml")