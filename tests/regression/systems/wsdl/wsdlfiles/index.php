<?xml version="1.0" encoding="ISO-8859-1"?>
<definitions xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://www.sinema.com/ws" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns="http://schemas.xmlsoap.org/wsdl/" targetNamespace="http://www.sinema.com/ws">
<types>
<xsd:schema targetNamespace="http://www.sinema.com/ws">
 <xsd:import namespace="http://schemas.xmlsoap.org/soap/encoding/"/>
 <xsd:import namespace="http://schemas.xmlsoap.org/wsdl/"/>
 <xsd:complexType name="Film">
  <xsd:all>
   <xsd:element name="film_id" type="xsd:string"/>
   <xsd:element name="title_tr" type="xsd:string"/>
   <xsd:element name="title_en" type="xsd:string"/>
   <xsd:element name="pic_url" type="xsd:string"/>
   <xsd:element name="small_pic" type="xsd:string"/>
   <xsd:element name="vision" type="xsd:string"/>
   <xsd:element name="puan" type="xsd:string"/>
   <xsd:element name="ozet" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="Filmarray">
  <xsd:complexContent>
   <xsd:restriction base="SOAP-ENC:Array">
    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="tns:Film[]"/>
   </xsd:restriction>
  </xsd:complexContent>
 </xsd:complexType>
 <xsd:complexType name="Seans">
  <xsd:all>
   <xsd:element name="salon_id" type="xsd:string"/>
   <xsd:element name="salon_ad" type="xsd:string"/>
   <xsd:element name="salon_tel" type="xsd:string"/>
   <xsd:element name="salon_ilce" type="xsd:string"/>
   <xsd:element name="seans_saatleri" type="xsd:string"/>
   <xsd:element name="seans_dublajli" type="xsd:string"/>
   <xsd:element name="seans_ekstra" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="Seansarray">
  <xsd:complexContent>
   <xsd:restriction base="SOAP-ENC:Array">
    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="tns:Seans[]"/>
   </xsd:restriction>
  </xsd:complexContent>
 </xsd:complexType>
 <xsd:complexType name="Salon">
  <xsd:all>
   <xsd:element name="salon_id" type="xsd:string"/>
   <xsd:element name="salon_ad" type="xsd:string"/>
   <xsd:element name="salon_tel" type="xsd:string"/>
   <xsd:element name="salon_ilce" type="xsd:string"/>
   <xsd:element name="salon_adres" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="Salonarray">
  <xsd:complexContent>
   <xsd:restriction base="SOAP-ENC:Array">
    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="tns:Salon[]"/>
   </xsd:restriction>
  </xsd:complexContent>
 </xsd:complexType>
 <xsd:complexType name="SalonFilm">
  <xsd:all>
   <xsd:element name="film_id" type="xsd:string"/>
   <xsd:element name="title_tr" type="xsd:string"/>
   <xsd:element name="title_en" type="xsd:string"/>
   <xsd:element name="pic_url" type="xsd:string"/>
   <xsd:element name="seans_saatleri" type="xsd:string"/>
   <xsd:element name="seans_dublajli" type="xsd:string"/>
   <xsd:element name="seans_ekstra" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="SalonFilmarray">
  <xsd:complexContent>
   <xsd:restriction base="SOAP-ENC:Array">
    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="tns:SalonFilm[]"/>
   </xsd:restriction>
  </xsd:complexContent>
 </xsd:complexType>
 <xsd:complexType name="Yazilar">
  <xsd:all>
   <xsd:element name="id" type="xsd:string"/>
   <xsd:element name="title" type="xsd:string"/>
   <xsd:element name="tarih" type="xsd:string"/>
   <xsd:element name="yazi" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="Yazilararray">
  <xsd:complexContent>
   <xsd:restriction base="SOAP-ENC:Array">
    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="tns:Yazilar[]"/>
   </xsd:restriction>
  </xsd:complexContent>
 </xsd:complexType>
 <xsd:complexType name="Iller">
  <xsd:all>
   <xsd:element name="il_id" type="xsd:string"/>
   <xsd:element name="il_adi" type="xsd:string"/>
  </xsd:all>
 </xsd:complexType>
 <xsd:complexType name="Illerarray">
  <xsd:complexContent>
   <xsd:restriction base="SOAP-ENC:Array">
    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="tns:Iller[]"/>
   </xsd:restriction>
  </xsd:complexContent>
 </xsd:complexType>
</xsd:schema>
</types>
<message name="Film_listesiRequest">
  <part name="status" type="xsd:string"/></message>
<message name="Film_listesiResponse">
  <part name="return" type="tns:Filmarray"/></message>
<message name="Film_seanslarRequest">
  <part name="film_id" type="xsd:string"/>
  <part name="il_id" type="xsd:string"/></message>
<message name="Film_seanslarResponse">
  <part name="return" type="tns:Seansarray"/></message>
<message name="Film_ayrintiRequest">
  <part name="film_id" type="xsd:string"/></message>
<message name="Film_ayrintiResponse">
  <part name="title_tr" type="xsd:string"/>
  <part name="title_en" type="xsd:string"/>
  <part name="pic_url" type="xsd:string"/>
  <part name="crew" type="xsd:string"/>
  <part name="cast" type="xsd:string"/>
  <part name="genres" type="xsd:string"/>
  <part name="puan" type="xsd:string"/>
  <part name="ozet" type="xsd:string"/></message>
<message name="Salon_listesiRequest">
  <part name="il_id" type="xsd:string"/></message>
<message name="Salon_listesiResponse">
  <part name="return" type="tns:Salonarray"/></message>
<message name="Salon_ayrintiRequest">
  <part name="salon_id" type="xsd:string"/></message>
<message name="Salon_ayrintiResponse">
  <part name="salon_adi" type="xsd:string"/>
  <part name="salon_tel" type="xsd:string"/>
  <part name="salon_adres" type="xsd:string"/>
  <part name="salon_ilce" type="xsd:string"/></message>
<message name="Salondaki_film_listesiRequest">
  <part name="salon_id" type="xsd:string"/></message>
<message name="Salondaki_film_listesiResponse">
  <part name="return" type="tns:SalonFilmarray"/></message>
<message name="Yazilar_listesiRequest">
  <part name="status" type="xsd:string"/></message>
<message name="Yazilar_listesiResponse">
  <part name="return" type="tns:Yazilararray"/></message>
<message name="IllerRequest">
  <part name="ulke" type="xsd:string"/></message>
<message name="IllerResponse">
  <part name="return" type="tns:Illerarray"/></message>
<portType name="sinemaPortType">
  <operation name="Film_listesi">
    <input message="tns:Film_listesiRequest"/>
    <output message="tns:Film_listesiResponse"/>
  </operation>
  <operation name="Film_seanslar">
    <input message="tns:Film_seanslarRequest"/>
    <output message="tns:Film_seanslarResponse"/>
  </operation>
  <operation name="Film_ayrinti">
    <input message="tns:Film_ayrintiRequest"/>
    <output message="tns:Film_ayrintiResponse"/>
  </operation>
  <operation name="Salon_listesi">
    <input message="tns:Salon_listesiRequest"/>
    <output message="tns:Salon_listesiResponse"/>
  </operation>
  <operation name="Salon_ayrinti">
    <input message="tns:Salon_ayrintiRequest"/>
    <output message="tns:Salon_ayrintiResponse"/>
  </operation>
  <operation name="Salondaki_film_listesi">
    <input message="tns:Salondaki_film_listesiRequest"/>
    <output message="tns:Salondaki_film_listesiResponse"/>
  </operation>
  <operation name="Yazilar_listesi">
    <input message="tns:Yazilar_listesiRequest"/>
    <output message="tns:Yazilar_listesiResponse"/>
  </operation>
  <operation name="Iller">
    <input message="tns:IllerRequest"/>
    <output message="tns:IllerResponse"/>
  </operation>
</portType>
<binding name="sinemaBinding" type="tns:sinemaPortType">
  <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
  <operation name="Film_listesi">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Film_listesi" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Film_seanslar">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Film_seanslar" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Film_ayrinti">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Film_ayrinti" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Salon_listesi">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Salon_listesi" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Salon_ayrinti">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Salon_ayrinti" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Salondaki_film_listesi">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Salondaki_film_listesi" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Yazilar_listesi">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Yazilar_listesi" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
  <operation name="Iller">
    <soap:operation soapAction="http://www.sinema.com/ws/index.php/Iller" style="rpc"/>
    <input><soap:body use="literal" namespace="http://www.sinema.com/ws"/></input>
    <output><soap:body use="literal" namespace="http://www.sinema.com/ws"/></output>
  </operation>
</binding>
<service name="sinema">
  <port name="sinemaPort" binding="tns:sinemaBinding">
    <soap:address location="http://www.sinema.com/ws/index.php"/>
  </port>
</service>
</definitions>