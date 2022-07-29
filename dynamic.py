# dynamic.py

"""
Execute in an AppControl check action :
curl -L -k -s "https://raw.githubusercontent.com/joaomdsc/sample/main/dynamic.py" | python3
"""

xmap = """\
<xcapptree>
  <component name="C1" displayname="Dyn C1" message="Dynamic component with one parent" group="myGroup" >
    <father>Main</father>
  </component>
  <component name="C2" displayname="Dyn C2" message="Dynamic component with no group and no parent">
    <father>Main</father>
  </component>
</xcapptree>
"""

print(xmap)