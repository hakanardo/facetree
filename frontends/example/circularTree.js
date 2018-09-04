var distanceGen = 70;
var width = (2 * 7 + 1) * distanceGen;
var height = width;
var colLookUp = {'blå': 'blue', 'grön': 'green', 'gul': 'yellow', 'röd': 'red'};
var draw;
var endDate = 1950;

function showPopupimage(evt, text, imgid) {
    let popuptext = document.getElementById("popuptext");
    popuptext.innerHTML = text;
    popuptext.style.display = "block";
    popuptext.style.left = evt.pageX + 10 + 'px';
    popuptext.style.top = evt.pageY - 25 + 'px';

    let popupimage = document.getElementById("popupimage");
    popupimage.innerHTML = '';
    var image='';
    if (imgid) {
        axios.get(facetree_backend + "/v1/images/" + imgid + "/thumb.jpg/base64",
                  {"headers": auth_headers})
            .then((response) => {
                //image = 'data:image/jpeg;base64,' + response.data;
                //var info = '<img src="'+image+'"/>';
                popupimage.innerHTML = '<img src="data:image/jpeg;base64,'+response.data+'"/>';
            })
            .catch(function (error) {
                console.log("Image download failed");
                console.log(error);
            });
    }
    popupimage.style.display = "block";
    popupimage.style.left = evt.pageX + 10 + 'px';
    popupimage.style.top = evt.pageY + 10 + 'px';
}

function hidePopupimage() {
    var popupimage = document.getElementById("popupimage");
    popupimage.style.display = "none";
    var popuptext = document.getElementById("popuptext");
    popuptext.style.display = "none";
}

function bestImgId(pers, year) {
    var imgId;
    var yearTaken;
    var minDist = 100;
    try { imgId = pers.imageIds[0][1];}
    catch (err) { imgId='';}
    for(var i = 0; i < pers.imageIds.length; i++) {
        try { yearTaken = parseInt(pers.imageIds[i][0]); }
        catch(err) { yearTaken = 0; }
        if ( Math.abs(year - yearTaken) < minDist) {
            imgId = pers.imageIds[i][1];
            minDist = Math.abs(year - yearTaken);
        }
    }
    return imgId;
}

function individual(id) {
    return database.individuals[id];
};

function animate_tree() {
    var x = document.getElementById('year');
    var year = x.value;
    function frame() {
        year++;  // update parameters
        x.value = year;
        drawTree();
        if (year == 2018)  // check finish condition
            clearInterval(id);
    }
    var id = setInterval(frame, 500); // draw every 0.5s
}

function drawTree() {
    var x = document.getElementById('yearbox');
    var y = document.getElementById('year');
    x.value = y.value;
    endDate = x.value;
    try {var zoomLevel = draw.zoom();}
    catch (err) { var zoomlevel=1;}
    document.getElementById('petriTree').innerHTML = '';
    //draw = SVG('petriTree').size(width, height).viewbox(0, 0, width, height);
    draw = SVG('petriTree').viewbox(0, 0, width, height).panZoom();
    personSVG(database.root);
    //draw.zoom(zoomLevel, {x:width/2, y:height/2}); //recenters graph
    draw.zoom(zoomLevel);
}

function translate(x, y) {
    return {x: x + width/2.0, y: y + height/2.0};
}

function pol2cart(R, alpha) {
    x = R * Math.cos(alpha);
    y = R * Math.sin(alpha);
    return translate(x, y);
}

function popupTxt(rec) {
    var txt = rec.name + "<br>";
    //txt += id+' ';
    txt += rec.birth.from + ' - ';
    try { txt += rec.death.from; }
    catch(err) {;}
    return txt;
}

function personSVG(ind) {
    if (ind.gedId == 'I0631') { return; } // Magda, Wivi
    if (ind.gedId == 'I0639') { return; }
    var gen = ind.generation; //PersonRecs[pid]['generation'];
    var distRing = (gen+1) * distanceGen - distanceGen/2.0;
    var ppos, pos, pos1, pos2, color;
    if (gen == 1) {
        ppos = translate(0, 0);
        draw.text('Petri släktträd').attr({x: ppos.x-distanceGen,
                                             y: ppos.y-distanceGen/2.0, fill: 'black'}).font({family: 'Helvetica', size: 20});
        draw.text(endDate.toString()).attr({x: ppos.x-distanceGen/2.0,
                                            y: ppos.y+distanceGen/4.0, fill: 'black'}).font({family: 'Helvetica', size: 20});
        var pp = draw.group();
        //pp.add(draw.element('title').words(popupTxt(ind)));
        //pp.add(draw.text(pid).attr({x: ppos.x, y: ppos.y, fill: 'grey'}));
        var txt = popupTxt(ind);
        pp.add(draw.circle(10).attr({cx: ppos.x, cy: ppos.y, stroke: 'grey', fill: 'grey',
                                     onmousemove: "showPopupimage(evt, '"+txt+"', '');",
                                     onmouseout: "hidePopupimage();"}));
    } else {
        ppos = pol2cart(gen * distanceGen, ind.alpha); //PersonRecs[pid]['alpha']);
    }
    if (!database.parentin[ind.id]) {
        return;
    }
    var plist = Array.from(database.parentin[ind.id]);
    for (var i in plist) {
        try {
            var chlist = Array.from(database.families[plist[i]].children)
        }
        catch (err) { var chlist = [];}
        for (var j in chlist) {
            var child = individual(chlist[j]);
            if (child.birth.from > endDate) { continue; }
            var color = colLookUp[child.color];
            try {
                if (child.death.from < endDate) { color = 'grey'; }
            }
            catch (err) { ; }
            if (typeof color == 'undefined') { color = 'black'; }
            pos = pol2cart((gen+1) * distanceGen, child.alpha);
            var pers = draw.group();
            //pers.add(draw.element('title').words(popupTxt(child)));
            var txt = popupTxt(child);
            //try {var img = child.imageIds[0][1];}
            try {var img = bestImgId(child, endDate);}
            catch (err) { var img='';}
            pers.add(draw.circle(10).attr({cx: pos.x, cy: pos.y, stroke: color, fill: color,
                                           onmousemove: "showPopupimage(evt, '"+txt+"', '"+img+"');",
                                           onmouseout: "hidePopupimage();"}));
            pos1 = pol2cart(distRing, ind.alpha);
            pos2 = pol2cart(distRing, child.alpha);
            draw.line(ppos.x, ppos.y, pos1.x, pos1.y).attr({stroke: color});
            draw.line(pos2.x, pos2.y, pos.x, pos.y).attr({stroke: color});
            var startAngle = child.alpha;
            var endAngle = ind.alpha;
            if (ind.alpha < child.alpha) {
                startAngle = ind.alpha;
                endAngle = child.alpha;
            }
            var largeArc = 0;
            var sweep = 1;
            if (endAngle - startAngle > Math.PI) {
                largeArc = 1;
                if (endAngle - startAngle > 3 * Math.PI/4) {
                    largeArc = 0
                    sweep = 0
                }
            }
            pos1 = pol2cart(distRing, startAngle);
            pos2 = pol2cart(distRing, endAngle);
            var d = ['M', pos1.x, pos1.y, 'A', distRing, distRing, 0, largeArc, sweep, pos2.x, pos2.y];
            draw.path(d.join(' ')).attr({fill:'none', stroke: color});
            personSVG(child);
        }
    }
    return;
}
