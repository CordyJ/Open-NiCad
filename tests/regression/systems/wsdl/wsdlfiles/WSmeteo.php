<?xml version="1.0" encoding="ISO-8859-1"?>
<definitions xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://mdmj.dubois.club.fr/soap/MeteoService" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns="http://schemas.xmlsoap.org/wsdl/" targetNamespace="http://mdmj.dubois.club.fr/soap/MeteoService">
<types><xsd:schema targetNamespace="http://mdmj.dubois.club.fr/soap/MeteoService"
>
 <xsd:import namespace="http://schemas.xmlsoap.org/soap/encoding/" />
 <xsd:import namespace="http://schemas.xmlsoap.org/wsdl/" />
 <xsd:complexType name="retour">
  <xsd:sequence>
   <xsd:element name="station" type="tns:station-distance" maxOccurs="unbounded" minOccurs="0"/>
  </xsd:sequence>
 </xsd:complexType>
 <xsd:complexType name="code">
  <xsd:sequence>
   <xsd:element name="station" type="xsd:string" maxOccurs="1" minOccurs="0"/>
  </xsd:sequence>
 </xsd:complexType>
 <xsd:complexType name="station-distance">
  <xsd:all>
   <xsd:element name="station" type="tns:station"/>
   <xsd:element name="distance" type="xsd:float"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="entree">
  <xsd:all>
   <xsd:element name="ville" type="xsd:string"/>
   <xsd:element name="nombre" type="xsd:int"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="station">
  <xsd:all>
   <xsd:element name="ICAO" type="xsd:string"/>
   <xsd:element name="latitude" type="xsd:float"/>
   <xsd:element name="longitude" type="xsd:float"/>
   <xsd:element name="nom" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="meteo">
  <xsd:all>
   <xsd:element name="ville" type="xsd:string"/>
   <xsd:element name="date" type="xsd:datetime"/>
   <xsd:element name="vit_vent" type="xsd:int"/>
   <xsd:element name="dir_vent" type="xsd:int"/>
   <xsd:element name="pression" type="xsd:int"/>
   <xsd:element name="temp" type="xsd:int"/>
   <xsd:element name="rosee" type="xsd:int"/>
   <xsd:element name="METAR" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
</xsd:schema>
</types>
<message name="GetStationPlusProcheRequest"><part name="input" type="tns:entree" /></message>
<message name="GetStationPlusProcheResponse"><part name="return" type="tns:retour" /></message>
<message name="GetMeteoRequest"><part name="input" type="tns:code" /></message>
<message name="GetMeteoResponse"><part name="return" type="tns:meteo" /></message>
<portType name="MeteoServicePortType"><operation name="GetStationPlusProche"><input message="tns:GetStationPlusProcheRequest"/><output message="tns:GetStationPlusProcheResponse"/></operation><operation name="GetMeteo"><input message="tns:GetMeteoRequest"/><output message="tns:GetMeteoResponse"/></operation></portType>
<binding name="MeteoServiceBinding" type="tns:MeteoServicePortType"><soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/><operation name="GetStationPlusProche"><soap:operation soapAction="http://mdmj.dubois.club.fr/villes/WS/WSmeteo.php/GetStationPlusProche" style="rpc"/><input><soap:body use="encoded" namespace="urn:http://mdmj.dubois.club.fr/villes/" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/></input><output><soap:body use="encoded" namespace="urn:http://mdmj.dubois.club.fr/villes/" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/></output></operation><operation name="GetMeteo"><soap:operation soapAction="http://mdmj.dubois.club.fr/villes/WS/WSmeteo.php/GetMeteo" style="rpc"/><input><soap:body use="encoded" namespace="urn:http://mdmj.dubois.club.fr/villes/" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/></input><output><soap:body use="encoded" namespace="urn:http://mdmj.dubois.club.fr/villes/" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/></output></operation></binding>
<service name="MeteoService"><port name="MeteoServicePort" binding="tns:MeteoServiceBinding"><soap:address location="http://mdmj.dubois.club.fr/villes/WS/WSmeteo.php"/></port></service>
</definitions>