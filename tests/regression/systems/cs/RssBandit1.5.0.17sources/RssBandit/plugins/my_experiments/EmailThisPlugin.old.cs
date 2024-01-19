using System; 
using System.Xml.XPath; 
using Syndication.Extensibility;
using System.Windows.Forms;
using System.Diagnostics;

namespace Microsoft.Douglasp.Blog {


       public class EmailThisPlugin:IBlogExtension {
	
         public bool HasConfiguration { get {return false; } }
	 public bool HasEditingGUI{ get {return false; } }


	 public void Configure(IWin32Window parent){
	   /* yeah, right */
	 }


	      public string DisplayName { get { return "Email This..."; } }

 
              public void BlogItem(System.Xml.XPath.IXPathNavigable rssFragment, bool edited) {
                     
                     LaunchEmail(GetMailUrl(rssFragment.CreateNavigator()));
              }


              private String GetMailUrl(XPathNavigator nav) {

                     const String TEMPLATE_STRING = @"mailto:nobody@example.com?subject={0}&body={1}";
                     
                     return String.Format(TEMPLATE_STRING,
			    nav.Evaluate("string(//item/title/text())"),
                            nav.Evaluate("string(//item/link/text())"));
              }

 

              private void LaunchEmail(String mailUrl) {

		 Process.Start(mailUrl); 
              }

       

       }

 

}
