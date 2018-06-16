var distanceGen = 70;
var width = (2 * 7 + 1) * distanceGen;
var height = width;
var colLookUp = {'blå': 'blue', 'grön': 'green', 'gul': 'yellow', 'röd': 'red'};
var draw;
var endDate = 1950;

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
    var txt = rec.name; //PersonRecs[id]['name'] + "\n";
    //txt += id+' ';
    txt += rec.birth.from + ' - '; //PersonRecs[id]['birth']['from'] + ' - ';
    try { txt += rec.death.from; } //PersonRecs[id]['death']['from']; }
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
        //draw.text('Petri ' + endDate.toString()).attr({x: 0, y: 20, fill: 'black'}).font({family: 'Helvetica', size: 20});
        ppos = translate(0, 0);
        draw.text('Petri släktträd').attr({x: ppos.x-distanceGen,
                                             y: ppos.y-distanceGen/2.0, fill: 'black'}).font({family: 'Helvetica', size: 20});
        draw.text(endDate.toString()).attr({x: ppos.x-distanceGen/2.0,
                                            y: ppos.y+distanceGen/2.0, fill: 'black'}).font({family: 'Helvetica', size: 20});
        var pp = draw.group();
        pp.add(draw.element('title').words(popupTxt(ind)));
        //pp.add(draw.text(pid).attr({x: ppos.x, y: ppos.y, fill: 'grey'}));
        pp.add(draw.circle(10).attr({cx: ppos.x, cy: ppos.y, stroke: 'grey', fill: 'grey'}));
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
            pers.add(draw.element('title').words(popupTxt(child)));
            pers.add(draw.circle(10).attr({cx: pos.x, cy: pos.y, stroke: color, fill: color}));
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
