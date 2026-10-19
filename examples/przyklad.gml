<?xml version="1.0" encoding="UTF-8"?>
<gml:FeatureCollection
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:egb="urn:gugik:specyfikacje:gmlas:ewidencjaGruntowIBudynkow:1.0"
    xmlns:ges="urn:gugik:specyfikacje:gmlas:geodezyjnaEwidencjaSieciUzbrojeniaTerenu:1.0"
    xmlns:ot="urn:gugik:specyfikacje:gmlas:bazaDanychObiektowTopograficznych500:1.0"
    xmlns:osg="urn:gugik:specyfikacje:gmlas:osnowyGeodezyjne:1.0">

  <gml:featureMember>
    <egb:EGB_DzialkaEwidencyjna gml:id="dz.1">
      <egb:idDzialki>141201_1.0001.123</egb:idDzialki>
      <egb:numerDzialki>123</egb:numerDzialki>
      <egb:geometria>
        <gml:Polygon srsName="EPSG:2177">
          <gml:exterior>
            <gml:LinearRing>
              <gml:posList>5712340.00 6512100.00 5712380.00 6512160.00 5712330.00 6512200.00 5712300.00 6512140.00 5712340.00 6512100.00</gml:posList>
            </gml:LinearRing>
          </gml:exterior>
        </gml:Polygon>
      </egb:geometria>
    </egb:EGB_DzialkaEwidencyjna>
  </gml:featureMember>

  <gml:featureMember>
    <egb:EGB_Budynek gml:id="bud.1">
      <egb:idBudynku>141201_1.0001.5_BUD</egb:idBudynku>
      <egb:funkcjaBudynku>budynek mieszkalny</egb:funkcjaBudynku>
      <egb:geometria>
        <gml:Polygon srsName="EPSG:2177">
          <gml:exterior>
            <gml:LinearRing>
              <gml:posList>5712345.00 6512120.00 5712360.00 6512140.00 5712350.00 6512150.00 5712335.00 6512130.00 5712345.00 6512120.00</gml:posList>
            </gml:LinearRing>
          </gml:exterior>
        </gml:Polygon>
      </egb:geometria>
    </egb:EGB_Budynek>
  </gml:featureMember>

  <gml:featureMember>
    <egb:EGB_PunktGraniczny gml:id="pg.1">
      <egb:numerPunktu>1-123</egb:numerPunktu>
      <egb:geometria>
        <gml:Point srsName="EPSG:2177">
          <gml:pos>5712340.00 6512100.00</gml:pos>
        </gml:Point>
      </egb:geometria>
    </egb:EGB_PunktGraniczny>
  </gml:featureMember>

  <gml:featureMember>
    <ges:GES_PrzewodWodociagowy gml:id="w.1">
      <ges:rodzajPrzewodu>woda</ges:rodzajPrzewodu>
      <ges:geometria>
        <gml:Curve srsName="EPSG:2177">
          <gml:segments>
            <gml:LineStringSegment>
              <gml:posList>5712300.00 6512100.00 5712330.00 6512140.00 5712360.00 6512170.00</gml:posList>
            </gml:LineStringSegment>
          </gml:segments>
        </gml:Curve>
      </ges:geometria>
    </ges:GES_PrzewodWodociagowy>
  </gml:featureMember>

  <gml:featureMember>
    <ges:GES_PrzewodGazowy gml:id="g.1">
      <ges:geometria>
        <gml:LineString srsName="EPSG:2177">
          <gml:posList>5712310.00 6512090.00 5712350.00 6512130.00</gml:posList>
        </gml:LineString>
      </ges:geometria>
    </ges:GES_PrzewodGazowy>
  </gml:featureMember>

  <gml:featureMember>
    <ges:GES_Wezel gml:id="wz.1">
      <ges:geometria>
        <gml:Point srsName="EPSG:2177">
          <gml:pos>5712330.00 6512140.00</gml:pos>
        </gml:Point>
      </ges:geometria>
    </ges:GES_Wezel>
  </gml:featureMember>

  <gml:featureMember>
    <ot:OT_SKBU_L gml:id="ogr.1">
      <ot:rodzaj>ogrodzenie</ot:rodzaj>
      <ot:geometria>
        <gml:LineString srsName="EPSG:2177">
          <gml:posList>5712340.00 6512100.00 5712380.00 6512160.00 5712330.00 6512200.00</gml:posList>
        </gml:LineString>
      </ot:geometria>
    </ot:OT_SKBU_L>
  </gml:featureMember>

  <gml:featureMember>
    <ot:OT_RTPW_P gml:id="drz.1">
      <ot:rodzaj>drzewo lisciaste</ot:rodzaj>
      <ot:geometria>
        <gml:Point srsName="EPSG:2177">
          <gml:pos>5712355.00 6512155.00</gml:pos>
        </gml:Point>
      </ot:geometria>
    </ot:OT_RTPW_P>
  </gml:featureMember>

  <gml:featureMember>
    <osg:OSG_PunktOsnowy gml:id="os.1">
      <osg:numer>1234</osg:numer>
      <osg:geometria>
        <gml:Point srsName="EPSG:2177">
          <gml:pos>5712300.00 6512100.00</gml:pos>
        </gml:Point>
      </osg:geometria>
    </osg:OSG_PunktOsnowy>
  </gml:featureMember>

</gml:FeatureCollection>
