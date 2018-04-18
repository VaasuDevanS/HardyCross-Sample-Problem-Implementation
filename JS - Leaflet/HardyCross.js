
// Defining a Map
var AU_Map = L.map('map').setView([13.0095436, 80.2368869], 18);
// OSM Layer
var OSM = new L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                       maxZoom: 100,
                    });

function popUp(feature, layer) {
    layer.bindPopup(feature.properties.name);
  }

function Style(feature, latlng) {
    label = String(feature.properties.value) // Must convert to string, .bindTooltip can't use straight 'feature.properties.attribute'
    return new L.CircleMarker(latlng, {
        radius: 5,
        fillColor: "#ff7800",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }).bindTooltip(label, {permanent: true, opacity: 1}).openTooltip();
}

function Building_Styles(feature) {
    return {
        fillColor: 'pink',
        weight: 2,
        opacity: 1,
        color: 'red',  //Outline color
        fillOpacity: 0.7
    };
}

function Roads_Styles(feature) {
    return {
        weight: 5,
        opacity: 1,
        color: 'green',  //Outline color
        fillOpacity: 0.7
    };
}


AU_Map.addLayer(OSM);    
L.geoJSON(Buildings, {onEachFeature:popUp,style: Building_Styles}).addTo(AU_Map);     // Buildings layer
L.geoJSON(Roads, {onEachFeature:popUp,style: Roads_Styles}).addTo(AU_Map);         // Roads layer
L.geoJSON(Network, {onEachFeature:popUp}).addTo(AU_Map);       // MyNetwork layer
L.geoJSON(TankPoints,
         {pointToLayer:Style,
          onEachFeature:popUp}).addTo(AU_Map);  // TankPoints layer with Styles


function sum(arg){

    var total = 0;
    for (var i in arg){
        total += arg[i];
    }
    return total;
}

function R(num){
    return Math.round(num * 100) / 100;
}
         
function Iterate(obj, Dir, Qa, K){

    var Dels = []
    
    var Hl = {}
    var Hl_Qa = {}
    for (var arc of ['AB', 'BD', 'DA']){
        
        Hl[arc] = (Qa[arc]**2) * K[arc] * Dir[arc];
        Hl_Qa[arc] = Math.abs(Hl[arc]/Qa[arc]);
     }
    var Del1 = -sum(Hl)/(obj.n*sum(Hl_Qa));
    Dels.push(Del1);
    
    var Hl = {}
    var Hl_Qa = {}
    for (var arc of ['BC', 'CD', 'DB']){
        
        Hl[arc] = (Qa[arc]**2) * K[arc] * Dir[arc];
        Hl_Qa[arc] = Math.abs(Hl[arc]/Qa[arc]);
     }
    var Del2 = -sum(Hl)/(obj.n*sum(Hl_Qa));
    Dels.push(Del2)
    
    var text = $('#del');
    text.val(text.val()+' Del1= '+R(Dels[0])+', Del2= '+R(Dels[1])+'\n\n');
    
    var Qa_values = $('#Qa');
    var ans = ' AB= '+R(Qa.AB)+', BD= '+R(Qa.BD)+',DA= '+R(Qa.DA)+', BC= '+R(Qa.BC)+', CD= '+R(Qa.CD);
    Qa_values.val(Qa_values.val()+ans+'\n\n')
    
    if ((R(Dels[0])>=obj.con) && (R(Dels[1])>=obj.con)){
        
        return true;
            
    }else{
        var New_Qa = {};
        for (var arc of ['AB', 'BD', 'DA']){
            if(arc == 'BD'){
                New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[0]-Dels[1];
            }else{
                New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[0];
            }
         }
        for (var arc of ['BC', 'CD', 'DB']){
            if(arc == 'DB'){
                New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[1]-Dels[0];
            }else{
                New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[1];
            }
        }  
        Iterate(obj, Dir, New_Qa, K);
    }
    
}         

function click(){

    var obj = {};
    var Dir = {};
    var Qa = {};
    var K = {};

    obj.a = parseFloat(document.getElementById("a_value").value);
    obj.b = parseFloat(document.getElementById("b_value").value);
    obj.c = parseFloat(document.getElementById("c_value").value);
    obj.d = parseFloat(document.getElementById("d_value").value);
    obj.n = parseFloat(document.getElementById("n_value").value);

    K.AB = parseFloat(document.getElementById("ab_value").value);
    K.BC = parseFloat(document.getElementById("bc_value").value);
    K.CD = parseFloat(document.getElementById("cd_value").value);
    K.DA = parseFloat(document.getElementById("ad_value").value);
    K.BD = parseFloat(document.getElementById("bd_value").value);
    K.DB = parseFloat(document.getElementById("bd_value").value);

    obj.con = parseFloat(document.getElementById("iter_value").value);

    Dir.AB = 1;
    Dir.BC = 1;
    Dir.BD = 1;
    Dir.DA = -1;
    Dir.CD = -1;
    Dir.DB = -1;

    Qa.AB = obj.a / 2;
    Qa.DA = obj.a / 2;
    obj.b += Qa.AB;
    Qa.BC = obj.b / 2;
    Qa.DB = obj.b / 2;
    Qa.BD = obj.b / 2;
    
    if ((Qa.DA+Qa.BD) > obj.d)
        {
            Qa.CD = obj.d - Qa.DA - Qa.BD;
        }
    else
        {
            Qa.CD = Qa.BC - obj.c;
        }
        
    Iterate(obj, Dir, Qa, K);
}

function clear(){
    var text = $('#del');
    var Qa_values = $('#Qa');
    text.val('');
    Qa_values.val('');
}

$('body').on('click', '#submit', click); // Calling the function when Generate is clicked
$('body').on('click', '#clear', clear); // Calling the clear function

// EOF
