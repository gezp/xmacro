# xmacro

`xmacro` is a simple tool to define and parse XML macro. it's inspired by [ros/xacro](https://github.com/ros/xacro) which is an XML macro language desiged for `urdf`. `xmacro` looks like a simplified version of `ros/xacro`, it's simpler, but it works well both for `urdf` and `sdf`. in addition it's flexible, and also easy to use.

* `xmacro` is independent of ROS, you could install it by `pip` .
* XML namespace isn't used in `xmacro`, there are some reserved tags: `xmacro_include`, `xmacro_define_value`, `xmacro_define_block`, `xmacro_block`.
* it provides python api so that we could parse xml file in ROS2 launch file.
* `xmacro4sdf` : `xmacro` with some specific functions for `sdf`(pre-defined common macro, `xmacro_include` path parser for `model://`).
* `xmacro4urdf` : `xmacro` with some specific functions for `urdf`(pre-defined common macro, `xmacro_include` path parser for `package://`).

## Usage

Installation

```bash
# install by pip
pip install xmacro
# install from source code
git clone https://github.com/gezp/xmacro.git
cd xmacro && sudo python3 setup.py install
```
examples

```bash
# some examples in folder test/xmacro
xmacro test_xmacro_block.xml.xmacro > test_xmacro_block.xml
```

##  XMLMacro Features

* Value macro
* Block macro
* Math expressions
* Include
* Python API

### Value macro

Value macro are named values that can be inserted anywhere into the XML document **except `<xmacro_define_block>` block**.

xmacro definition

```xml
<!--definition of properties -->
<xmacro_define_value name="radius" value="4.3" />
<!--use of properties-->
<circle diameter="${2 * radius}" />
```

generated xml

```xml
<circle diameter="8.6" />
```

### Block macro

Define block macros with the macro tag `<xmacro_define_block>`, then specify the macro name and a list of parameters. The list of parameters should be whitespace separated. 

The usage of block macros is to define `<xmacro_block>` which will be replaced with corresponding `<xmacro_define_block>` block.

xmacro definition

```xml
<!--definition of macro-->
<xmacro_define_value name="mass" value="0.2" />
<xmacro_define_block name="box_inertia" params="m x y z">
    <mass>${m}</mass>
    <inertia>
         <ixx>${m*(y*y+z*z)/12}</ixx>
         <ixy>0</ixy>
         <ixz>0</ixz>
         <iyy>${m*(x*x+z*z)/12}</iyy>
         <iyz>0</iyz>
        <izz>${m*(x*x+z*z)/12}</izz>
    </inertia>
</xmacro_define_block>
<!--use of macro-->
<inertial>
     <pose>0 0 0.02 0 0 0</pose>
     <xmacro_block name="box_inertia" m="${mass}" x="0.3" y="0.1" z="0.2"/>
</inertial>
```

generated xml

```xml
<inertial>
    <pose>0 0 0.02 0 0 0</pose>
    <mass>0.2</mass>
    <inertia>
        <ixx>0.0008333333333333335</ixx>
        <ixy>0</ixy>
        <ixz>0</ixz>
        <iyy>0.002166666666666667</iyy>
        <iyz>0</iyz>
        <izz>0.002166666666666667</izz>
    </inertia>
</inertial>
```

* only support simple parameters (string and number), and block parameters isn't supported.
* it's supported to use other  `xmacro_block`  in `xmacro_define_block` which is recursive definition (the max nesting level is 5).

condition block

a example here (you could find more examples in `test/xmacro/test_xmacro_condition.xml.xmacro`)
```xml
<!--use of macro-->
<inertial>
    <pose>0 0 0.02 0 0 0</pose>
    <xmacro_block name="box_inertia" m="${mass}" x="0.3" y="0.1" z="0.2" condition="${mass==0.2}"/>
</inertial>
```
* the `condition` can be `True`, `False`, `1`, `0`, we can also use math expression to define condition, but operator `<` and `>` isn't supported in math expression.
* if `condition` is `False` or `0`, the `xmacro_block` wou't be loaded.
* `condition` is reserved attribute of `<xmacro_block>`, so `condition` can't be used as `params` of `<xmacro_define_block>`.


### Math expressions

* within dollared-braces `${xxxx}`, you can also write simple math expressions.
* refer to examples of  **Value macro** and **Block macro** 
* it's implemented by calling `eval()` in python, so it's unsafe for some cases.

### Including other xmacro files

You can include other xmacro files by using the `<xmacro_include>` tag.

*  it will include the xmcaro definition with tag `<xmacro_define_value>` and macros with tag `<xmacro_define_block>`.

```xml
<xmacro_include uri="file://simple_car/model.sdf.xmacro"/>
```

* The uri for `file` means to open the file directly.
  *  it try to open the file with relative path `simple_car/model.sdf.xmacro` . 
  * you can also try to open file with absolute path `/simple_car/model.sdf.xmacro` with uri `file:///simple_car/model.sdf.xmacro`.
* `<xmacro_include>` supports to include  recursively.  

### Python API

you can use `xmacro` in python easily

```python
from xmacro.xmacro import XMLMacro

xmacro=XMLMacro()
#case1 parse from file
xmacro.set_xml_file(inputfile)
xmacro.generate()
xmacro.to_file(outputfile)

#case2 parse from xml string
xmacro.set_xml_string(xml_str)
xmacro.generate()
xmacro.to_file(outputfile)

#case3 generate to string
xmacro.set_xml_file(inputfile)
xmacro.generate()
xmacro.to_string()

#case4 custom macro value
xmacro.set_xml_file(inputfile)
# use custom dictionary to overwrite global macro value defined by <xmacro_define_value>
kv={"rplidar_a2_h":0.8}
xmacro.generate(kv)
xmacro.to_file(outputfile)
```

## XMLMacro4sdf Features

pre-defined common.sdf.xmacro

```xml
<!--macro defination:inertia-->
<xmacro_define_block name="inertia_cylinder" params="m r l">
<xmacro_define_block name="inertia_box" params="m x y z">
<xmacro_define_block name="inertia_sphere" params="m r">
<!--macro defination:geometry-->
<xmacro_define_block name="geometry_cylinder" params="r l">
<xmacro_define_block name="geometry_box" params="x y z">
<xmacro_define_block name="geometry_sphere" params="r">
<xmacro_define_block name="geometry_mesh" params="uri">
<!--macro defination:visual_collision_with_mesh-->
<xmacro_define_block name="visual_collision_with_mesh" params="prefix uri">
```

examples

```bash
# some examples in folder test/sdf
xmacro4sdf model.sdf.xmacro > model.sdf
```


## XMLMacro4urdf Features

pre-defined common.urdf.xmacro

```xml
<!--macro defination:inertia-->
<xmacro_define_block name="inertia_cylinder" params="m r l">
<xmacro_define_block name="inertia_box" params="m x y z">
<xmacro_define_block name="inertia_sphere" params="m r">
<!--macro defination:geometry-->
<xmacro_define_block name="geometry_cylinder" params="r l">
<xmacro_define_block name="geometry_box" params="x y z">
<xmacro_define_block name="geometry_sphere" params="r">
<xmacro_define_block name="geometry_mesh" params="uri">
```

examples

```bash
# some examples in folder test/urdf
xmacro4urdf robot.urdf.xmacro > robot.urdf
```

## Maintainer and License 

maintainer : Zhenpeng Ge, zhenpeng.ge@qq.com

`xmacro` is provided under MIT License.
