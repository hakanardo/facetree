"""
Import familytree from Gramps XML to facetree database
"""
from os import access, R_OK
from os.path import isfile
import re
import xml.etree.ElementTree as ET

#test version of API
from dbAPI_test import dbImport
dbAPI = dbImport()
dbAPI.setUp() #Fix authentication
from flask.json import dumps as json_dumps
from app import app
client = app.app.test_client()
#

fn = 'Petri.xml'
xmlns =  '{http://gramps-project.org/xml/1.7.1/}'
ns = {'mx': 'http://gramps-project.org/xml/1.7.1/'}
tree = ET.parse(fn)
treeRoot = tree.getroot()

def getHandles(xml, field):
    handles = []
    try:
        for ref in xml.findall('mx:'+field, ns):
            handles.append(ref.attrib['hlink'])
    except: pass
    return handles

def namestr(name):
    given = name.find("mx:first", ns).text
    last = name.find("mx:surname", ns).text
    return "%s %s" % (given, last)

def dateToInt(date):
    #Use only the year
    #if not date: return None
    dateInt = 0
    m = re.search(r".*(\d\d\d\d).*", date)
    if m:
        year = m.group(1)
        dateInt = int(year)
    return dateInt

families = treeRoot.find("mx:families", ns)
persons = treeRoot.find("mx:people", ns)
events = treeRoot.find("mx:events", ns)
places = treeRoot.find("mx:places", ns)
tags = treeRoot.find("mx:tags", ns)
objects = treeRoot.find("mx:objects", ns)
"""
Relations/families Gramps XML
    <family handle="_bed6a8644f878b5ff01afc719ed" change="1490781871" id="F0001">
      <rel type="Married"/>
      <father hlink="_bed6a8642ca7eedcafb38bca211"/>
      <mother hlink="_bed6a8645042067c5c7bdcf4317"/>
      <eventref hlink="_c054d25ea0d75db0303" role="Family"/>
      <childref hlink="_bed6a86453e7a1b4bb9ceff12bd"/>
      <childref hlink="_bed6a86455d675653e5a2e2f0b1"/>
    </family>
"""
for family in families.findall("mx:family", ns):
    fid = family.attrib['id']
    #print("%s: Family")
    rec = {'type': 'Family', 'author': 'Gramps', 'gedId': fid, 'children': []}
    for parent in ('father', 'mother'):
        try:
            p = family.find('mx:'+parent, ns)
            handle = p.attrib['hlink']
            person = persons.find("mx:person[@handle='%s']" % handle, ns)
            rec[parent] = person.attrib['id']
        except Exception as ex:
            #print(ex)
            pass
    #for childref in family.findall("mx:childref", ns):
    #    handle = childref.attrib['hlink']
    for handle in getHandles(family, 'childref')
        person = persons.find("mx:person[@handle='%s']" % handle, ns)
        rec['children'].append(person.attrib['id'])
    if not rec['children']: del rec['children']
    #print(rec)
    id = dbAPI.create_record(rec)
    if rec['gedId'] == 'F0015': famTestId = id #TEST

"""
Individuals Gramps XML
    <person handle="_bed6a8642ca7eedcafb38bca211" change="1493358091" id="I0001">
      <gender>M</gender>
      <name type="Birth Name">
        <first>Anders</first>
        <surname>Ardö</surname>
      </name>
      <eventref hlink="_c054d2688ca3a9a04df" role="Primary"/>
      <objref hlink="_d8df844c5972741f3e96068459d">
       <region corner1_x="85" corner1_y="49" corner2_x="88" corner2_y="58"/>
      </objref>
      <childof hlink="_bed6a8644fa64e670e89c9cf42"/>
      <parentin hlink="_bed6a8644f878b5ff01afc719ed"/>
      <tagref hlink="_d8df844b55162915ac2345a1e04"/>

    <event handle="_bed6a8645111d7cb049d3f6ccd0" change="1501790855" id="E0001">
      <type>Birth</type>
      <dateval val="1950-01-17"/>
      <place hlink="_bed6a8642d271be2adfd008a00f"/>
    </event>
      <daterange start="1873" stop="1876"/>
      <datespan start="1878" stop="1882"/>

    <placeobj handle="_d1b26259ca0157ad1b1fc1121ff" change="1490468597" id="P0010" type="Country">
      <ptitle>Sverige</ptitle>
      <pname value="Sverige"/>
      <pname value="Sweden"/>
      <coord long="13.1935176849" lat="55.7041130066"/>
    </placeobj>

  <tags>
    <tag handle="_d8df844b55162915ac2345a1e04" change="1453216673" name="röd" color="#000000" priority="0"/>

    <object handle="_c06b56c58f646456aec9a935a7d" change="1475497866" id="O0002">
      <file src="/data/Pictures/Arkiv ARDO/2011/2011 08 Vka DK/IMG_7529.JPG" mime="image/jpeg" description="IMG_7529"/>
"""
for person in persons.findall("mx:person", ns):
    pid = person.attrib['id']
    name = namestr(person.find("mx:name", ns)) #Bara type Birth name?
    #print('%s: %s' % (pid, name))
    rec = {'type': 'Individual', 'author': 'Gramps', 'gedId': pid, 'name': name}
    imgFn = None
    locs = []
    #events
    for event in person.findall("mx:eventref", ns):
        handle = event.attrib['hlink']
        ev = events.find("mx:event[@handle='%s']" % handle, ns)
        type = ev.find("mx:type", ns).text
        if type in ('Birth', 'Residence', 'Death', 'Burial'):
            loc = {'from': 0}
            try:
                d = dateToInt(ev.find("mx:dateval", ns).attrib['val'])
                loc['from'] = d
            except: pass
            for field in ("mx:daterange", "mx:datespan"):
                try:
                    dates = ev.find(field, ns)
                    loc['from'] = dateToInt(dates.attrib['start'])
                    loc['to'] = dateToInt(dates.attrib['stop'])
                    #break  ??
                except: pass
            place = ev.find("mx:place", ns)
            try:
                handle = place.attrib['hlink']
                placeobj = places.find("mx:placeobj[@handle='%s']" % handle, ns)
                coord = placeobj.find("mx:coord", ns)
                loc['long'] = coord.attrib['long']
                loc['lat'] = coord.attrib['lat']
            except: pass
            #Evt iterate over placeref in placeobj until coord found?
            locs.append(loc)
    #tags
    #for tag in person.findall("mx:tagref", ns):
    #    handle = tag.attrib['hlink']
    for handle in getHandles(person, 'tagref')
        tagobj = tags.find("mx:tag[@handle='%s']" % handle, ns)
        if tagobj.attrib['name'] != 'Petri':
            rec['color'] = tagobj.attrib['name']
    #Relations
    #for childref in person.findall("mx:childof", ns):
    #    handle = childref.attrib['hlink']
    for handle in getHandles(person, 'childof')
        family = families.find("mx:family[@handle='%s']" % handle, ns)
        rec['childfam'] = family.attrib['id']
    pfam = []
    #for parentref in person.findall("mx:parentin", ns):
    #    handle = parentref.attrib['hlink']
    for handle in getHandles(person, 'parentin')
        family = families.find("mx:family[@handle='%s']" % handle, ns)
        pfam.append(family.attrib['id'])
    if pfam: rec['parentin'] = pfam
    #Images
    imageFile = None
    #for objref in person.findall("mx:objref", ns):
    #    handle = objref.attrib['hlink']
    for handle in getHandles(person, 'objref')
        image = objects.find("mx:object[@handle='%s']" % handle, ns)
        try:
            file = image.find("mx:file", ns)
            imageFile = file.attrib['src']
            if isfile(imageFile) and access(imageFile, R_OK):
                #FIX extract region
                break #Only take one?
        except: pass
    #print(imageFile)
    if imageFile and isfile(imageFile) and access(imageFile, R_OK):
        #FIX Handle region
        fil = open(imageFile, 'rb')
        image = fil.read()
        fil.close()
        rec['imageId'] = dbAPI.save_image(image)
    if locs:
        rec['location'] = sorted(locs, key=lambda x: x['from'])
    #print(rec)
    id = dbAPI.create_record(rec)
    if rec['gedId']=='I0028': testId = id #TEST

#Test
r = dbAPI.get('/v1/records')
for rec in r.json:
    if rec['type'] == 'Individual': print(rec['name'], rec['gedId'], rec['id'])
    else: print('Family', rec['gedId'], rec['id'])
print(testId)
r = dbAPI.get('/v1/records/%s' % (testId))
print(r.json)
r = dbAPI.get('/v1/records/%s' % (famTestId))
print(r.json)
#Documentation
"""
Record structure:
{
'type': 'Family',
'id': 'c8f0c0f1-3c90-4407-aeba-e98d720bcf67',
'version': '1525542247418',
'author': 'xxx',
'gedId': 'F0015',
'father': 'I0028',
'mother': 'I0029',
'children': ['I0054', 'I1033', 'I0056', 'I0053', 'I1122', 'I0842']
}
{
'type': 'Individual',
'id': 'c2996fd9-830f-43ce-ba82-27ff637230b0',
'version': '1525542247741',
'author': 'xxx',
'gedId': 'I0028',
'name': 'David Ekedahl',
'imageId': '9a66d841-62cc-45fe-8b7a-e9ea1959065a',
'color': 'röd',
'location': [{'from': 1878, 'long': '13.3259861111111', 'lat': '56.8922166666667'},
{'from': 1946, 'to': 1965, 'long': '12.8464212', 'lat': '56.6768526'}]
        <location> from, long, lat mandatory; to optional
'parentin': ['F0015'],
'childfam': 'F0016'
}
Birth, Death year also in separate fields?
image coordinates ??
"""
