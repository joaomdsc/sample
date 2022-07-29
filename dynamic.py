# dynamic.py

"""
Execute in an AppControl check action :
curl -L -k -s "https://raw.githubusercontent.com/joaomdsc/sample/main/dynamic.py" | python3
"""

xmap = """\
<xcapptree>
  <component group="myGroup" color="255,0,0" type="service" name="C1"
    displayname="Dyn C1" message="Dynamic component with one parent" >
    <father>Main</father>
  </component>
  <component name="C2" displayname="Dyn C2" color="0,255,0"
    state="started" message="Dynamic component with no group and no parent"
    type="dollar">
  </component>
</xcapptree>
"""

print(xmap)
