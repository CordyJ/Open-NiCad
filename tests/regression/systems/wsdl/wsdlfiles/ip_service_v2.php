<?xml version="1.0" encoding="UTF-8"?>
<definitions name="ip_service_extern" targetNamespace="https://ipayment.de/service_v2/extern" xmlns:ipayment="https://ipayment.de/service_v2/extern" xmlns:tns="https://ipayment.de/service_v2/extern" xmlns="http://schemas.xmlsoap.org/wsdl/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <types>
    <xsd:schema targetNamespace="https://ipayment.de/service_v2/extern" xmlns:ipayment="https://ipayment.de/service_v2/extern" xmlns="http://schemas.xmlsoap.org/wsdl/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:import namespace="http://schemas.xmlsoap.org/soap/encoding/"/>
      <xsd:complexType name="OptionHashItem">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="key" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="value" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="OptionHash">
        <xsd:complexContent>
          <xsd:restriction base="SOAP-ENC:Array">
            <xsd:sequence>
              <xsd:element maxOccurs="unbounded" minOccurs="0" name="option" type="ipayment:OptionHashItem"/>
            </xsd:sequence>
            <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="ipayment:OptionHashItem[]"/>
          </xsd:restriction>
        </xsd:complexContent>
      </xsd:complexType>
      <xsd:complexType name="AddressData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrName" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreet" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreet2" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrCity" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrZip" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrState" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrCountry" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrEmail" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrTelefon" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrTelefax" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrCheckAddress" type="xsd:boolean"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="TransactionData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="trxAmount" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="trxCurrency" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="invoiceText" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="trxUserComment" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="transactionId" type="xsd:long"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="OptionData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="fromIp" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="orderId" type="xsd:long"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="browserUserAgent" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="browserAcceptHeaders" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="advancedStrictIdCheck" type="xsd:boolean"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="checkFraudattack" type="xsd:boolean"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="checkDoubleTrx" type="xsd:boolean"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="errorLang" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="otherOptions" type="ipayment:OptionHash"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="ThreeDSecureData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="MD" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="PaRes" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="PaymentDataCC">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="ccNumber" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="ccExpdateMonth" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="ccExpdateYear" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="ccCheckcode" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="ccStartdateMonth" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="ccStartdateYear" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="ccIssuenumber" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addressData" type="ipayment:AddressData"/>

        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="PaymentDataELV">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="0" name="bankCode" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="bankAccountnumber" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="bankName" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="bankCountry" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="bankIban" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="bankBic" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addressData" type="ipayment:AddressData"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="PaymentDataMP">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="mpTyp" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="mpMobilenumber" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="mpMobilenumberCountrycode" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addressData" type="ipayment:AddressData"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="AccountData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="accountId" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="trxuserId" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="trxpassword" type="xsd:long"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="adminactionpassword" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:simpleType name="PaymentReturnStatus">
          <xsd:restriction base="xsd:string">
              <xsd:enumeration value="SUCCESS"/>
              <xsd:enumeration value="ERROR"/>
              <xsd:enumeration value="REDIRECT"/>
          </xsd:restriction>
      </xsd:simpleType>
      <xsd:simpleType name="PaymentType">
          <xsd:restriction base="xsd:string">
              <xsd:enumeration value="cc"/>
              <xsd:enumeration value="elv"/>
              <xsd:enumeration value="mp"/>
              <xsd:enumeration value="pp"/>
          </xsd:restriction>
      </xsd:simpleType>
      <xsd:simpleType name="TransactionType">
          <xsd:restriction base="xsd:string">
              <xsd:enumeration value="auth"/>
              <xsd:enumeration value="base_check"/>
              <xsd:enumeration value="check_save"/>
              <xsd:enumeration value="grefund_cap"/>
              <xsd:enumeration value="preauth"/>
          </xsd:restriction>
      </xsd:simpleType>
      <xsd:complexType name="PaymentReturnError">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="retErrorcode" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="retFatalerror" type="xsd:int"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="retErrormsg" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="retAdditionalmsg" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="PaymentReturnRedirect">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="redirectAction" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="redirectData" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="PaymentReturnSuccess">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="retTransdate" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="retTranstime" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="retBooknr" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="retAuthcode" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="PaymentReturn">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="status" type="ipayment:PaymentReturnStatus"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="errorDetails" type="ipayment:PaymentReturnError"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="successDetails" type="ipayment:PaymentReturnSuccess"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="redirectDetails" type="ipayment:PaymentReturnRedirect"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addressData" type="ipayment:AddressData"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addresscheckResult" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="paymentMethod" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="AddresscheckData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="addrStreet" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreetNumber" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreet2" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrCity" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrZip" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrState" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="addrCountry" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="SuggestionArray">
        <xsd:complexContent>
          <xsd:restriction base="SOAP-ENC:Array">
            <xsd:sequence>
              <xsd:element maxOccurs="unbounded" minOccurs="0" name="suggestion" type="xsd:string"/>
            </xsd:sequence>
            <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="xsd:string[]"/>
          </xsd:restriction>
        </xsd:complexContent>
      </xsd:complexType>
      <xsd:simpleType name="AddresscheckFieldstatus">
          <xsd:restriction base="xsd:string">
              <xsd:enumeration value="OK"/>
              <xsd:enumeration value="CORRECTED"/>
              <xsd:enumeration value="SUGGESTIONS"/>
              <xsd:enumeration value="ERROR"/>
              <xsd:enumeration value="UNCHECKED"/>
              <xsd:enumeration value="NORMALIZED"/>
          </xsd:restriction>
      </xsd:simpleType>
      <xsd:complexType name="AddresscheckFieldresult">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="origValue" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="1" name="status" type="ipayment:AddresscheckFieldstatus"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="suggestionList" type="ipayment:SuggestionArray"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="statusDetail" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="AddresscheckReturn">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="status" type="ipayment:AddresscheckFieldstatus"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreet" type="ipayment:AddresscheckFieldresult"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreetNumber" type="ipayment:AddresscheckFieldresult"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrStreet2" type="ipayment:AddresscheckFieldresult"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrCity" type="ipayment:AddresscheckFieldresult"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrZip" type="ipayment:AddresscheckFieldresult"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="addrState" type="ipayment:AddresscheckFieldresult"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:simpleType name="EmailcheckStatus">
          <xsd:restriction base="xsd:string">
              <xsd:enumeration value="OK"/>
              <xsd:enumeration value="ERROR"/>
          </xsd:restriction>
      </xsd:simpleType>
      <xsd:complexType name="EmailcheckReturn">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="status" type="ipayment:EmailcheckStatus"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="statusDetail" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
      <xsd:complexType name="ProcessorUrlData">
        <xsd:sequence>
          <xsd:element maxOccurs="1" minOccurs="1" name="redirectUrl" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="silentErrorUrl" type="xsd:string"/>
          <xsd:element maxOccurs="1" minOccurs="0" name="hiddenTriggerUrl" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>
    </xsd:schema>
  </types>
  <message name="basecheckELVRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataELV"/>
  </message>
  <message name="basecheckCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
  </message>
  <message name="basecheckMPRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataMP"/>
  </message>
  <message name="checksaveELVRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataELV"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="preAuthorizeELVRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataELV"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="captureRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="origTrxNumber" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="refundRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="origTrxNumber" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="checksaveMPRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataMP"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="preAuthorizeMPRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataMP"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="reverseRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="origTrxNumber" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="authorizeELVRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataELV"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="reAuthorizeRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="origTrxNumber" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="preAuthorizeCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="authorizeCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="voiceAuthorizeCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
    <part name="voiceAuthcode" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="paymentAuthenticationReturnRequest">
    <part name="threedsecureData" type="tns:ThreeDSecureData"/>
  </message>
  <message name="authorizeMPRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataMP"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="rePreAuthorizeRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="origTrxNumber" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="checksaveCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="generalRefundCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="voiceGeneralRefundCCRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataCC"/>
    <part name="voiceAuthcode" type="xsd:string"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="generalRefundELVRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataELV"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="generalRefundMPRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="paymentData" type="tns:PaymentDataMP"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="options" type="tns:OptionData"/>
  </message>
  <message name="ipaymentResponse">
    <part name="ipaymentReturn" type="tns:PaymentReturn"/>
  </message>
  <message name="checkAddressRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="addressData" type="tns:AddresscheckData"/>
    <part name="maxSuggestions" type="xsd:int"/>
    <part name="requestId" type="xsd:string"/>
  </message>
  <message name="addresscheckResponse">
    <part name="addresscheckReturn" type="tns:AddresscheckReturn"/>
  </message>
  <message name="checkEmailRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="email" type="xsd:string"/>
    <part name="checkPort" type="xsd:boolean"/>
  </message>
  <message name="emailcheckResponse">
    <part name="emailcheckReturn" type="tns:EmailcheckReturn"/>
  </message>
  <message name="createSessionRequest">
    <part name="accountData" type="tns:AccountData"/>
    <part name="transactionData" type="tns:TransactionData"/>
    <part name="transactionType" type="tns:TransactionType"/>
    <part name="paymentType" type="tns:PaymentType"/>
    <part name="options" type="tns:OptionData"/>
    <part name="processorUrls" type="tns:ProcessorUrlData"/>
  </message>
  <message name="createSessionResponse">
    <part name="sessionId" type="xsd:string"/>
  </message>
  <portType name="ipaymentPortType">
    <operation name="authorizeCC">
      <input message="tns:authorizeCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="authorizeELV">
      <input message="tns:authorizeELVRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="authorizeMP">
      <input message="tns:authorizeMPRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="checksaveCC">
      <input message="tns:checksaveCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="checksaveELV">
      <input message="tns:checksaveELVRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="checksaveMP">
      <input message="tns:checksaveMPRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="generalRefundCC">
      <input message="tns:generalRefundCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="generalRefundELV">
      <input message="tns:generalRefundELVRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="generalRefundMP">
      <input message="tns:generalRefundMPRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="basecheckCC">
      <input message="tns:basecheckCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="basecheckELV">
      <input message="tns:basecheckELVRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="basecheckMP">
      <input message="tns:basecheckMPRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="capture">
      <input message="tns:captureRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="preAuthorizeCC">
      <input message="tns:preAuthorizeCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="preAuthorizeELV">
      <input message="tns:preAuthorizeELVRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="preAuthorizeMP">
      <input message="tns:preAuthorizeMPRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="reAuthorize">
      <input message="tns:reAuthorizeRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="rePreAuthorize">
      <input message="tns:rePreAuthorizeRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="reverse">
      <input message="tns:reverseRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="refund">
      <input message="tns:refundRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="paymentAuthenticationReturn">
      <input message="tns:paymentAuthenticationReturnRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="checkAddress">
      <input message="tns:checkAddressRequest"/>
      <output message="tns:addresscheckResponse"/>
    </operation>
    <operation name="checkEmail">
      <input message="tns:checkEmailRequest"/>
      <output message="tns:emailcheckResponse"/>
    </operation>
    <operation name="voiceAuthorizeCC">
      <input message="tns:voiceAuthorizeCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="voiceGeneralRefundCapCC">
      <input message="tns:voiceGeneralRefundCCRequest"/>
      <output message="tns:ipaymentResponse"/>
    </operation>
    <operation name="createSession">
      <input message="tns:createSessionRequest"/>
      <output message="tns:createSessionResponse"/>
    </operation>
  </portType>
  <binding name="ipaymentBinding" type="tns:ipaymentPortType">
    <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
    <operation name="authorizeCC">
      <soap:operation soapAction="authorizeCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="authorizeELV">
      <soap:operation soapAction="authorizeELV"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="authorizeMP">
      <soap:operation soapAction="authorizeMP"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="checksaveCC">
      <soap:operation soapAction="checksaveCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="checksaveELV">
      <soap:operation soapAction="checksaveELV"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="checksaveMP">
      <soap:operation soapAction="checksaveMP"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="generalRefundCC">
      <soap:operation soapAction="generalRefundCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="generalRefundELV">
      <soap:operation soapAction="generalRefundELV"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="generalRefundMP">
      <soap:operation soapAction="generalRefundMP"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="basecheckCC">
      <soap:operation soapAction="basecheckCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="basecheckELV">
      <soap:operation soapAction="basecheckELV"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="basecheckMP">
      <soap:operation soapAction="basecheckMP"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="capture">
      <soap:operation soapAction="capture"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="preAuthorizeCC">
      <soap:operation soapAction="preAuthorizeCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="preAuthorizeELV">
      <soap:operation soapAction="preAuthorizeELV"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="preAuthorizeMP">
      <soap:operation soapAction="preAuthorizeMP"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="reAuthorize">
      <soap:operation soapAction="reAuthorize"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="rePreAuthorize">
      <soap:operation soapAction="rePreAuthorize"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="reverse">
      <soap:operation soapAction="reverse"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="refund">
      <soap:operation soapAction="refund"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="paymentAuthenticationReturn">
      <soap:operation soapAction="paymentAuthenticationReturn"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="checkAddress">
      <soap:operation soapAction="checkAddress"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="checkEmail">
      <soap:operation soapAction="checkEmail"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="voiceAuthorizeCC">
      <soap:operation soapAction="voiceAuthorizeCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="voiceGeneralRefundCapCC">
      <soap:operation soapAction="voiceGeneralRefundCapCC"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
    <operation name="createSession">
      <soap:operation soapAction="createSession"/>
      <input>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </input>
      <output>
        <soap:body use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" namespace="https://ipayment.de/service_v2/binding"/>
      </output>
    </operation>
  </binding>
  <service name="IpaymentServiceV2">
    <port name="ipayment" binding="tns:ipaymentBinding">
      <soap:address location="https://ipayment.de/v2/ip_service_v2.php"/>
    </port>
  </service>
</definitions>