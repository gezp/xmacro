#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import xml.dom.minidom
import xmacro.xml_format
from math import *

def try2number(str):
    try:
        return float(str)
    except ValueError:
        return str

class XMLMacro:
    def __init__(self):
        # custom
        self.tool_name = "xmacro"
        self.parse_uri_fn = None
        self.common_xmacro_paths = []
        # variables for xml parse
        self.xmacro_values={}
        self.xmacro_block_params={}
        self.xmacro_block_texts={}
        # variables for xml info
        self.filename=""
        self.dirname=""
        self.in_doc=None
        self.out_doc=None
        self.parse_flag=False

#### private funtion 
    def __parse_uri(self,uri,current_dirname):
        # returh a absolute path.
        # current_dirname is needed for 'file://'
        result = ""
        splited_str=uri.split("://")
        if len(splited_str)!=2:
            return result
        #get absolute path according to uri
        if splited_str[0] == "file":
            #to absolute path
            if(not os.path.isabs(splited_str[1])):
                splited_str[1]=os.path.join(current_dirname,splited_str[1])
            if os.path.isfile(splited_str[1]):
                result = os.path.abspath(splited_str[1])
        else:
            if self.parse_uri_fn is not None:
                result = self.parse_uri_fn(uri)
        return result

    def __parse_xmacro_defination(self,doc):
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'xmacro_define_value':
                    name = node.getAttribute("name")
                    self.xmacro_values[name] = try2number(node.getAttribute("value"))
                elif node.tagName == 'xmacro_define_block':
                    name = node.getAttribute("name")
                    if node.hasAttribute("params"):
                        self.xmacro_block_params[name] = node.getAttribute("params").split(' ')
                    else:
                        self.xmacro_block_params[name] = []
                    self.xmacro_block_texts[name] = node.toxml()

    def __include_xmacro_defination_recursively(self,doc,dirname):
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'xmacro_include':
                    uri = node.getAttribute("uri")
                    filepath = self.__parse_uri(uri,dirname)
                    if filepath != "":
                        tmp_doc = xml.dom.minidom.parse(filepath)
                        # include xmacro from child recursively
                        self.__include_xmacro_defination_recursively(tmp_doc,os.path.dirname(filepath))
                        # parse xmacro from file
                        self.__parse_xmacro_defination(tmp_doc)
                    else:
                        raise Exception("not find xmacro_include uri：%s"%uri)
        
    def __remove_xmacro_definition(self,doc):
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'xmacro_define_value' \
                    or node.tagName == 'xmacro_define_block' \
                    or node.tagName == 'xmacro_include':
                    root.removeChild(node)

    def __replace_value(self,xml_str,value_dict):
        pattern = re.compile(r'[$][{](.*?)[}]', re.S)
        def eval_fn(obj):
            try:
                result = eval(obj.group(1), None, value_dict)
            except Exception as e:
                 raise Exception("failed to eval <%s>"%(obj.group(1))+","+str(e))
            return str(result)
        return re.sub(pattern, eval_fn, xml_str)
            
    def __replace_macro_block(self,node):
        parent = node.parentNode
        if not node.hasAttribute("name"):
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"xmacro_block attribute 'name' is not defined")
        name = node.getAttribute("name")
        # check name
        if name not in self.xmacro_block_texts.keys():
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"xmacro_block<%s> is not defined"%name)
        # check condition
        condition = True
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")
        if condition == 'False' or condition == '0':
            # remove xmacro node
            parent.removeChild(node)
            return
        # get block info: xml string and params
        xml_str = self.xmacro_block_texts[name]
        params = {}
        for k in self.xmacro_block_params[name]:
            if not node.hasAttribute(k):
                raise Exception("[line %d]"%(sys._getframe().f_lineno)+"<%s> attribute '%s' is not defined"%(name,k))
            params[k] = try2number(node.getAttribute(k))
        # replace params value
        try:
            xml_str = self.__replace_value(xml_str,params)
        except Exception as e:
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"<%s>"%name+str(e))
        # transform to doc and insert to parent doc
        new_node = xml.dom.minidom.parseString(xml_str).documentElement
        for cc in list(new_node.childNodes):
            parent.insertBefore(cc, node)
        # remove xmacro node
        parent.removeChild(node)

    def __parse(self):
        # parse xmacro defination from in_doc store macro's defination in dict:
        # xmacro_values, xmacro_block_params, xmacro_block_texts
        # step1. parse common xmacro (lowest priority,it can be overwrited)
        for xmacro_path in self.common_xmacro_paths:
            self.__parse_xmacro_defination(xml.dom.minidom.parse(xmacro_path))
        # step2. inlcude xmacro recursively (the priority depends on the order)
        self.__include_xmacro_defination_recursively(self.in_doc,self.dirname)
        # step3. parse current xmacro (highest priority)
        self.__parse_xmacro_defination(self.in_doc)
        # remove xmacro defination (<xmacro_define_value>,<xmacro_define_block>,<xmacro_include>)
        self.__remove_xmacro_definition(self.in_doc)
        self.parse_flag = True

#### public funtion
    def set_xml_file(self,filepath):
        self.filename=filepath
        self.dirname=os.path.dirname(os.path.abspath(filepath))
        self.in_doc = xml.dom.minidom.parse(filepath)
        self.parse_flag = False

    def set_xml_string(self,xml_str):
        self.dirname=os.path.dirname(os.path.abspath(__file__))
        self.in_doc = xml.dom.minidom.parse(xml_str)
        self.parse_flag = False

    def generate(self,custom_values:dict={}):
        if self.in_doc is None:
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"input doc is None")
        # parse xmacro defination (value and block)
        if not self.parse_flag:
            self.__parse()
        # add custom values which could overwrite xmacro values
        xmacro_values = self.xmacro_values.copy()
        for k in custom_values:
            xmacro_values[k] = custom_values[k]
        xml_str = self.in_doc.documentElement.toxml()
        # replace xmacro value (process by string regular expression operations)
        try:
            xml_str = self.__replace_value(xml_str,xmacro_values)
        except Exception as e:
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"process xmacro_value,"+str(e))
        self.out_doc = xml.dom.minidom.parseString(xml_str)
        # replace xmacro block (breadth-first)
        for _ in range(100):
            nodes = self.out_doc.getElementsByTagName("xmacro_block")
            if nodes.length != 0:
                for node in list(nodes):
                    self.__replace_macro_block(node)
            else:
                break
        # check
        if self.out_doc.getElementsByTagName("xmacro_block").length != 0:
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"recursion level too deep (must<=100).")

    def to_string(self):
        # auto-generated banner
        # reference: https://github.com/ros/xacro/blob/noetic-devel/src/xacro/__init__.py
        if self.out_doc is None:
            return ""
        src = "python script"
        if self.filename != "":
            src = self.filename 
        banner_line_len = 83
        if len(self.tool_name)+len(src)>34:
            banner_line_len = 49+len(self.tool_name)+len(src)
        banner = [xml.dom.minidom.Comment(c) for c in
              [" %s " % ('=' * banner_line_len),
               " |    This document was autogenerated by %s from %s%*s | " %(self.tool_name,src,banner_line_len-48-len(self.tool_name)-len(src)," "),
               " |    EDITING THIS FILE BY HAND IS NOT RECOMMENDED %*s | " %(banner_line_len - 52, " "),
               " %s " % ('=' * banner_line_len)]]
        first = self.out_doc.firstChild
        for comment in banner:
            self.out_doc.insertBefore(comment, first)
        return self.out_doc.toprettyxml()

    def to_file(self,filepath):
        xml = self.to_string()
        # write to file
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write(xml)

def xmacro_main():
    if(len(sys.argv) < 2):
        print("Usage: xmacro <inputfile> (the name of inputfile must be xxx.xmacro)")
        return -1
    inputfile = sys.argv[1]
    # check
    if os.path.splitext(inputfile)[1] != '.xmacro':
        print("Error: the name of inputfile must be xxx.xmacro")
        return -2  
    # process 
    xmacro=XMLMacro()
    xmacro.set_xml_file(inputfile)
    try:
        xmacro.generate()
        print(xmacro.to_string())
    except Exception as e:
        print("Error:",e)
    return 0
    
if __name__ == '__main__':
    xmacro_main()