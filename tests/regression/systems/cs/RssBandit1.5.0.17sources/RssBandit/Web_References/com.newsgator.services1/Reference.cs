//------------------------------------------------------------------------------
// <autogenerated>
//     This code was generated by a tool.
//     Runtime Version: 1.1.4322.2032
//
//     Changes to this file may cause incorrect behavior and will be lost if 
//     the code is regenerated.
// </autogenerated>
//------------------------------------------------------------------------------

// 
// This source code was auto-generated by Microsoft.VSDesigner, Version 1.1.4322.2032.
// 
namespace RssBandit.com.newsgator.services1 {
    using System.Diagnostics;
    using System.Xml.Serialization;
    using System;
    using System.Web.Services.Protocols;
    using System.ComponentModel;
    using System.Web.Services;
    
    
    /// <remarks/>
    [System.Diagnostics.DebuggerStepThroughAttribute()]
    [System.ComponentModel.DesignerCategoryAttribute("code")]
    [System.Web.Services.WebServiceBindingAttribute(Name="FolderWebServiceSoap", Namespace="http://services.newsgator.com/svc/Folder.asmx")]
    public class FolderWebService : System.Web.Services.Protocols.SoapHttpClientProtocol {
        
        public NGAPIToken NGAPITokenValue;
        
        /// <remarks/>
        public FolderWebService() {
            this.Url = "http://services.newsgator.com/ngws/svc/Folder.asmx";
        }
        
        /// <remarks/>
        [System.Web.Services.Protocols.SoapHeaderAttribute("NGAPITokenValue")]
        [System.Web.Services.Protocols.SoapDocumentMethodAttribute("http://services.newsgator.com/svc/Folder.asmx/GetOrCreateFolder", RequestNamespace="http://services.newsgator.com/svc/Folder.asmx", ResponseNamespace="http://services.newsgator.com/svc/Folder.asmx", Use=System.Web.Services.Description.SoapBindingUse.Literal, ParameterStyle=System.Web.Services.Protocols.SoapParameterStyle.Wrapped)]
        public int GetOrCreateFolder(string name, int parentId, string root) {
            object[] results = this.Invoke("GetOrCreateFolder", new object[] {
                        name,
                        parentId,
                        root});
            return ((int)(results[0]));
        }
        
        /// <remarks/>
        public System.IAsyncResult BeginGetOrCreateFolder(string name, int parentId, string root, System.AsyncCallback callback, object asyncState) {
            return this.BeginInvoke("GetOrCreateFolder", new object[] {
                        name,
                        parentId,
                        root}, callback, asyncState);
        }
        
        /// <remarks/>
        public int EndGetOrCreateFolder(System.IAsyncResult asyncResult) {
            object[] results = this.EndInvoke(asyncResult);
            return ((int)(results[0]));
        }
        
        /// <remarks/>
        [System.Web.Services.Protocols.SoapHeaderAttribute("NGAPITokenValue")]
        [System.Web.Services.Protocols.SoapDocumentMethodAttribute("http://services.newsgator.com/svc/Folder.asmx/CreateFolder", RequestNamespace="http://services.newsgator.com/svc/Folder.asmx", ResponseNamespace="http://services.newsgator.com/svc/Folder.asmx", Use=System.Web.Services.Description.SoapBindingUse.Literal, ParameterStyle=System.Web.Services.Protocols.SoapParameterStyle.Wrapped)]
        public int CreateFolder(string name, int parentId, string root) {
            object[] results = this.Invoke("CreateFolder", new object[] {
                        name,
                        parentId,
                        root});
            return ((int)(results[0]));
        }
        
        /// <remarks/>
        public System.IAsyncResult BeginCreateFolder(string name, int parentId, string root, System.AsyncCallback callback, object asyncState) {
            return this.BeginInvoke("CreateFolder", new object[] {
                        name,
                        parentId,
                        root}, callback, asyncState);
        }
        
        /// <remarks/>
        public int EndCreateFolder(System.IAsyncResult asyncResult) {
            object[] results = this.EndInvoke(asyncResult);
            return ((int)(results[0]));
        }
        
        /// <remarks/>
        [System.Web.Services.Protocols.SoapHeaderAttribute("NGAPITokenValue")]
        [System.Web.Services.Protocols.SoapDocumentMethodAttribute("http://services.newsgator.com/svc/Folder.asmx/DeleteFolder", RequestNamespace="http://services.newsgator.com/svc/Folder.asmx", ResponseNamespace="http://services.newsgator.com/svc/Folder.asmx", Use=System.Web.Services.Description.SoapBindingUse.Literal, ParameterStyle=System.Web.Services.Protocols.SoapParameterStyle.Wrapped)]
        public void DeleteFolder(int id) {
            this.Invoke("DeleteFolder", new object[] {
                        id});
        }
        
        /// <remarks/>
        public System.IAsyncResult BeginDeleteFolder(int id, System.AsyncCallback callback, object asyncState) {
            return this.BeginInvoke("DeleteFolder", new object[] {
                        id}, callback, asyncState);
        }
        
        /// <remarks/>
        public void EndDeleteFolder(System.IAsyncResult asyncResult) {
            this.EndInvoke(asyncResult);
        }
        
        /// <remarks/>
        [System.Web.Services.Protocols.SoapHeaderAttribute("NGAPITokenValue")]
        [System.Web.Services.Protocols.SoapDocumentMethodAttribute("http://services.newsgator.com/svc/Folder.asmx/MoveFolder", RequestNamespace="http://services.newsgator.com/svc/Folder.asmx", ResponseNamespace="http://services.newsgator.com/svc/Folder.asmx", Use=System.Web.Services.Description.SoapBindingUse.Literal, ParameterStyle=System.Web.Services.Protocols.SoapParameterStyle.Wrapped)]
        public void MoveFolder(int id, int newParentId) {
            this.Invoke("MoveFolder", new object[] {
                        id,
                        newParentId});
        }
        
        /// <remarks/>
        public System.IAsyncResult BeginMoveFolder(int id, int newParentId, System.AsyncCallback callback, object asyncState) {
            return this.BeginInvoke("MoveFolder", new object[] {
                        id,
                        newParentId}, callback, asyncState);
        }
        
        /// <remarks/>
        public void EndMoveFolder(System.IAsyncResult asyncResult) {
            this.EndInvoke(asyncResult);
        }
        
        /// <remarks/>
        [System.Web.Services.Protocols.SoapHeaderAttribute("NGAPITokenValue")]
        [System.Web.Services.Protocols.SoapDocumentMethodAttribute("http://services.newsgator.com/svc/Folder.asmx/RenameFolder", RequestNamespace="http://services.newsgator.com/svc/Folder.asmx", ResponseNamespace="http://services.newsgator.com/svc/Folder.asmx", Use=System.Web.Services.Description.SoapBindingUse.Literal, ParameterStyle=System.Web.Services.Protocols.SoapParameterStyle.Wrapped)]
        public void RenameFolder(int id, string newName) {
            this.Invoke("RenameFolder", new object[] {
                        id,
                        newName});
        }
        
        /// <remarks/>
        public System.IAsyncResult BeginRenameFolder(int id, string newName, System.AsyncCallback callback, object asyncState) {
            return this.BeginInvoke("RenameFolder", new object[] {
                        id,
                        newName}, callback, asyncState);
        }
        
        /// <remarks/>
        public void EndRenameFolder(System.IAsyncResult asyncResult) {
            this.EndInvoke(asyncResult);
        }
        
        /// <remarks/>
        [System.Web.Services.Protocols.SoapHeaderAttribute("NGAPITokenValue")]
        [System.Web.Services.Protocols.SoapDocumentMethodAttribute("http://services.newsgator.com/svc/Folder.asmx/GetFolders", RequestNamespace="http://services.newsgator.com/svc/Folder.asmx", ResponseNamespace="http://services.newsgator.com/svc/Folder.asmx", Use=System.Web.Services.Description.SoapBindingUse.Literal, ParameterStyle=System.Web.Services.Protocols.SoapParameterStyle.Wrapped)]
        public System.Xml.XmlElement GetFolders() {
            object[] results = this.Invoke("GetFolders", new object[0]);
            return ((System.Xml.XmlElement)(results[0]));
        }
        
        /// <remarks/>
        public System.IAsyncResult BeginGetFolders(System.AsyncCallback callback, object asyncState) {
            return this.BeginInvoke("GetFolders", new object[0], callback, asyncState);
        }
        
        /// <remarks/>
        public System.Xml.XmlElement EndGetFolders(System.IAsyncResult asyncResult) {
            object[] results = this.EndInvoke(asyncResult);
            return ((System.Xml.XmlElement)(results[0]));
        }
    }
    
    /// <remarks/>
    [System.Xml.Serialization.XmlTypeAttribute(Namespace="http://services.newsgator.com/svc/Folder.asmx")]
    [System.Xml.Serialization.XmlRootAttribute(Namespace="http://services.newsgator.com/svc/Folder.asmx", IsNullable=false)]
    public class NGAPIToken : System.Web.Services.Protocols.SoapHeader {
        
        /// <remarks/>
        public string Token;
    }
}
