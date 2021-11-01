#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
from ament_index_python.packages import get_package_share_directory
from xmacro.xmacro import XMLMacro

def parse_package_uri(uri):
    result = ""
    splited_str=uri.split("://")
    if len(splited_str)!=2:
        return result
    # get absolute path according to uri
    if splited_str[0]  == "package":
        path_arr = splited_str[1].split('/')
        path_arr[0] = get_package_share_directory(path_arr[0])
        result = os.path.join(*path_arr)
    return result

class XMLMacro4urdf(XMLMacro):
    def __init__(self):
        super().__init__()
        self.tool_name = "xmacro4urdf"
        self.parse_uri_fn = parse_package_uri
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'common.urdf.xmacro')
        self.common_xmacro_paths.append(filepath)

def xmacro4urdf_main():
    if(len(sys.argv) < 2):
        print("Usage: xmacro4urdf <inputfile> (the name of inputfile must be xxx.xmacro)")
        return -1
    inputfile = sys.argv[1]
    # check
    if os.path.splitext(inputfile)[1] != '.xmacro':
        print("Error: the name of inputfile must be xxx.xmacro")
        return -2  
    # process 
    xmacro=XMLMacro4urdf()
    xmacro.set_xml_file(inputfile)
    try:
        xmacro.generate()
        print(xmacro.to_string())
    except Exception as e:
        print("Error:",e)
    return 0

if __name__ == '__main__':
    xmacro4urdf_main()