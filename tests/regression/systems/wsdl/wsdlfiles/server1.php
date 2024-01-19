<?xml version="1.0" encoding="ISO-8859-1"?>
<definitions xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://localhost/nusoap" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns="http://schemas.xmlsoap.org/wsdl/" targetNamespace="http://localhost/nusoap">
<types>
<xsd:schema targetNamespace="http://localhost/nusoap"
>
 <xsd:import namespace="http://schemas.xmlsoap.org/soap/encoding/" />
 <xsd:import namespace="http://schemas.xmlsoap.org/wsdl/" />
</xsd:schema>
</types>
<message name="CalculateOntarioTaxRequest">
  <part name="amount" type="xsd:string" /></message>
<message name="CalculateOntarioTaxResponse">
  <part name="return" type="xsd:string" /></message>
<portType name="CanadaTaxCalculatorPortType">
  <operation name="CalculateOntarioTax">
    <input message="tns:CalculateOntarioTaxRequest"/>
    <output message="tns:CalculateOntarioTaxResponse"/>
  </operation>
</portType>
<binding name="CanadaTaxCalculatorBinding" type="tns:CanadaTaxCalculatorPortType">
  <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
  <operation name="CalculateOntarioTax">
    <soap:operation soapAction="http://film-shop-home.de/temp/nusoap/try2/server1.php/CalculateOntarioTax" style="rpc"/>
    <input><soap:body use="encoded" namespace="http://localhost/nusoap" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/></input>
    <output><soap:body use="encoded" namespace="http://localhost/nusoap" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/></output>
  </operation>
</binding>
<service name="CanadaTaxCalculator">
  <port name="CanadaTaxCalculatorPort" binding="tns:CanadaTaxCalculatorBinding">
    <soap:address location="http://film-shop-home.de/temp/nusoap/try2/server1.php"/>
  </port>
</service>
</definitions>