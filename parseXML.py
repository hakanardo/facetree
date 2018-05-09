"""
Import familytree from Gramps XML to facetree database
"""
from os import access, R_OK
from os.path import isfile
import re
import xml.etree.ElementTree as ET
from PIL import Image
TEST = True
from dbAPI import dbImport
dbAPI = dbImport(auth = {"email": "hakan@debian.org", "password": "7tsLKBZo"})

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

def handleEvent(ev, type):
    loc = {'eventType': type, 'from': 0}
    try:
        dat = ev.find("mx:dateval", ns).attrib['val']
        d = dateToInt(dat)
        loc['from'] = d
        if type in ('Birth', 'Death'):
            try:
                rec[type] = dat
            except:
                try:
                    rec[type] = dat
                except: pass
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
    return loc

families = treeRoot.find("mx:families", ns)
persons = treeRoot.find("mx:people", ns)
events = treeRoot.find("mx:events", ns)
places = treeRoot.find("mx:places", ns)
tags = treeRoot.find("mx:tags", ns)
objects = treeRoot.find("mx:objects", ns)
gedId2Id = {}
file2Id = {}
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
      <dateval val="2006"/>
"""
for person in persons.findall("mx:person", ns):
    pid = person.attrib['id']
    name = namestr(person.find("mx:name", ns)) #Bara type Birth name?
    sex = person.find("mx:gender", ns).text
    #print('%s: %s' % (pid, name))
    rec = {'type': 'Individual', 'author': 'Gramps', 'gedId': pid, 'name': name, 'sex': sex}
    imgFn = None
    locs = []
    #events
    for event in person.findall("mx:eventref", ns):
        handle = event.attrib['hlink']
        ev = events.find("mx:event[@handle='%s']" % handle, ns)
        type = ev.find("mx:type", ns).text
        if type in ('Birth', 'Residence', 'Death', 'Burial'): #CHR?
            locs.append(handleEvent(ev, type))
    #tags
    for handle in getHandles(person, 'tagref'):
        tagobj = tags.find("mx:tag[@handle='%s']" % handle, ns)
        if tagobj.attrib['name'] != 'Petri':
            rec['color'] = tagobj.attrib['name']
    """
    #Relations - Replaced with an autogenerated index in the backend
    #for childref in person.findall("mx:childof", ns):
    #    handle = childref.attrib['hlink']
    for handle in getHandles(person, 'childof'):
        family = families.find("mx:family[@handle='%s']" % handle, ns)
        rec['childfam'] = family.attrib['id']
    pfam = []
    #for parentref in person.findall("mx:parentin", ns):
    #    handle = parentref.attrib['hlink']
    for handle in getHandles(person, 'parentin'):
        family = families.find("mx:family[@handle='%s']" % handle, ns)
        pfam.append(family.attrib['id'])
    if pfam: rec['parentin'] = pfam
    """
    #Images
    rec['imageIds'] = []
    #for handle in getHandles(person, 'objref'):
    i=0
    for objref in person.findall("mx:objref", ns):
        handle = objref.attrib['hlink']
        object = objects.find("mx:object[@handle='%s']" % handle, ns)
        cropedId = '?'
        i+=1
        try:
            file = object.find("mx:file", ns)
            imageFile = file.attrib['src']
            if isfile(imageFile) and access(imageFile, R_OK):
                if not file2Id.get(imageFile):
                    fil = open(imageFile, 'rb')
                    image = fil.read()
                    fil.close()
                    #rec['imageIds'].append(dbAPI.save_image(image))
                    id = dbAPI.save_image(image)
                    file2Id[imageFile] = id
                    cropedId = id
                    #print("%s %d %s" % (imageFile, len(image), cropedId))
                #Try to crop image
                try:
                    #print('try region')
                    #ET.dump(objref)
                    region = objref.find("mx:region", ns)
                    x1 = int(region.attrib['corner1_x'])
                    y1 = int(region.attrib['corner1_y'])
                    x2 = int(region.attrib['corner2_x'])
                    y2 = int(region.attrib['corner2_y'])
                    #print("  %d %d - %d %d" % (x1, y1, x2, y2))
                    im = Image.open(imageFile)
                    #print ('  width: %d - height: %d' % im.size) # returns (width, height) tuple
                    (width, height) = im.size
                    left = int(width * min(x1, x2)/100.)
                    right = int(width * max(x1, x2)/100.)
                    upper = int(height * min(y1, y2)/100.)
                    lower = int(height * max(y1, y2)/100.)
                    #TMP
                    #print("Crop to %d %d %d %d" % (left, upper, right, lower))
                    from io import BytesIO
                    cropedIm = BytesIO()
                    im.crop((left, upper, right, lower)).save(cropedIm, 'JPEG')
                    cropedId = dbAPI.save_image(cropedIm.getvalue())
                    #print("Saved cropped im %s", cropedId)
                    #TMP
                    #cropedId = dbAPI.crop_image(file2Id[imageFile], left, upper, right, lower)
                except:
                    #print('except region')
                    pass
                #Date <dateval>
                dat = None
                try:
                    #ET.dump(object)
                    dat = object.find("mx:dateval", ns).attrib['val']
                except:
                    #print('except dat')
                    pass
                #print("  End %s %s" % (dat, cropedId))
                rec['imageIds'].append((dat, cropedId))
        except:
            #print('Error saving %s' % imageFile)
            pass
        #print('------END image------')
        #if i>=2: sys.exit()
    if locs:
        rec['location'] = sorted(locs, key=lambda x: x['from'])
    #print(rec)
    id = dbAPI.create_record(rec)
    gedId2Id[rec['gedId']] = id
    #print('---------------end person')
    if TEST:
        if rec['gedId']=='I0028': testId = id #TEST

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
            rec[parent] = gedId2Id[person.attrib['id']]
        except Exception as ex:
            pass
    marriages = []
    for handle in getHandles(family, 'eventref'):
        event = events.find("mx:event[@handle='%s']" % handle, ns)
        type = event.find("mx:type", ns).text
        if type in ('Marriage', 'Divorce'):  #What about Residence?
            marriages.append(handleEvent(event, type))
    rec['marriages'] = marriages
    for handle in getHandles(family, 'childref'):
        person = persons.find("mx:person[@handle='%s']" % handle, ns)
        rec['children'].append(gedId2Id[person.attrib['id']])
    if not rec['children']: del rec['children']
    #print(rec)
    id = dbAPI.create_record(rec)
    if TEST:
        if rec['gedId'] == 'F0015': famTestId = id #TEST

if TEST:
    """
    r = dbAPI.get_records()
    for rec in r.json():
        if rec['type'] == 'Individual': print(rec['name'], rec['gedId'], rec['id'])
        else: print('Family', rec['gedId'], rec['id'])
    print(testId)
    """
    r = dbAPI.get_record(testId)
    print(r)
    r = dbAPI.get_record(famTestId)
    print(r)
