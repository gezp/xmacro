#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import xml.dom.minidom
import xmacro.xml_format
from xmacro.xmacro import XMLMacro

xmacro_paths = []
if os.getenv("IGN_GAZEBO_RESOURCE_PATH") is not None:
    xmacro_paths = xmacro_paths+os.getenv("IGN_GAZEBO_RESOURCE_PATH").split(":")
if os.getenv("GAZEBO_MODEL_PATH") is not None:
    xmacro_paths = xmacro_paths+os.getenv("GAZEBO_MODEL_PATH").split(":")

def parse_model_uri(uri):
    result = ""
    splited_str=uri.split("://")
    if len(splited_str)!=2:
        return result
    # get absolute path according to uri
    if splited_str[0]  == "model":
        for tmp_path in xmacro_paths:
            tmp_path = os.path.join(tmp_path,splited_str[1])
            if(os.path.isfile(tmp_path)):
                result = tmp_path
                break
    return result

class XMLMacro4sdf(XMLMacro):
    def __init__(self):
        super().__init__()
        self.parse_uri_fn = parse_model_uri
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'common.sdf.xmacro')
        self.common_xmacro_paths.append(filepath)

    def set_static(self,is_static):
        if self.out_doc is None:
            return False
        root=self.out_doc.documentElement
        # model node
        nodes=root.getElementsByTagName('model')
        if len(nodes)==0:
            return False
        model=nodes[0]
        nodes=model.getElementsByTagName('static')
        # static node
        static = None
        if len(nodes)==0:
            static=self.out_doc.createElement('static')
            model.insertBefore(static,model.firstChild)
            static.appendChild(self.out_doc.createTextNode('false'))
        else:
            static=nodes[0]
        # set value
        static.firstChild.data = "true" if is_static else "false"
        return True

def xmacro4sdf_main():
    if(len(sys.argv) < 2):
        print("Usage: xmacro4sdf <inputfile> (the name of inputfile must be xxx.xmacro)")
        return -1
    inputfile = sys.argv[1]
    outputfile = os.path.splitext(inputfile)[0]
    # check
    if os.path.splitext(inputfile)[1] != '.xmacro':
        print("Error: the name of inputfile must be xxx.xmacro")
        return -2  
    # process 
    xmacro=XMLMacro4sdf()
    xmacro.set_xml_file(inputfile)
    try:
        xmacro.generate()
        print(xmacro.to_string())
    except Exception as e:
        print("Error:",e)
    return 0

if __name__ == '__main__':
    xmacro4sdf_main()