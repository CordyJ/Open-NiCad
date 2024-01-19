using System;
using System.ComponentModel;
using System.Windows.Forms;
using System.Windows.Forms.Design;
using System.Drawing;


namespace PluginCore
{
	/// <summary>
	/// Prompts the user to select a folder.
	/// </summary>
	[
	DesignTimeVisible(true),
	ToolboxItem(true),
	/* ToolboxBitmap( typeof( BrowseForFolderPrompt ), "Design.BrowseForFolderPrompt.bmp" ) */
	]
	public class BrowseForFolderPrompt : FolderNameEditor, IComponent {
		
		#region private var's

		private FolderNameEditor.FolderBrowser			_browser		= new FolderNameEditor.FolderBrowser();
		private ISite									_site			= null;

		#endregion
		
		#region Public Events

		/// <summary>
		/// Fired when the form is disposed.
		/// </summary>
		public event EventHandler Disposed;

		/// <summary>
		/// Raises the <see cref="Disposed"/> event.
		/// </summary>
		protected virtual void OnDisposed( EventArgs e ) {
			if( Disposed != null )
				Disposed( this, e );
		}

		#endregion
		
		#region ctor's

		/// <summary>
		/// Initializes a new instance of the BrowseForFolderPrompt class.
		/// </summary>
		public BrowseForFolderPrompt() {
		}

		/// <summary>
		/// Initializes a new instance of the BrowseForFolderPrompt class.
		/// </summary>
		/// <param name="description">
		///		A description of the folder the user is browsing for.
		/// </param>
		/// <param name="startLocation">
		///		One of the <see cref="FolderBrowserFolder"/> values 
		///		that indicates the starting location.
		/// </param>
		public BrowseForFolderPrompt( PluginCore.FolderBrowserFolder startLocation, string description ) {
			StartLocation	= startLocation;
			Description		= description;
		}

		/// <summary>
		/// Implements the Dispose method of the IComponent interface.
		/// </summary>
		public void Dispose() {
			OnDisposed( EventArgs.Empty );
		}

		#endregion

		#region Properties

		/// <summary>
		/// Implements <see cref="IComponent.Site"/>.
		/// </summary>
		[ Browsable( false ) ]
		public ISite Site {
			get {
				return _site;
			}
			set {
				_site = value;
			}
		}

		/// <summary>
		/// Gets or sets the Startup folder.
		/// </summary>
		[
		Description( "The Startup folder." ),
		DefaultValue( FolderBrowserFolder.Desktop )
		]
		public PluginCore.FolderBrowserFolder StartLocation {
			get {
				return ((PluginCore.FolderBrowserFolder) ((int)_browser.StartLocation) );
			}
			set {
				_browser.StartLocation = (FolderBrowserFolder)((int)value);
			}
		}

		/// <summary>
		/// Gets the path to the selected folder.
		/// </summary>
		[ Browsable( false ) ]
		public string Folder {
			get {
				return _browser.DirectoryPath;
			}
		}

		/// <summary>
		/// Gets or sets the description of the folder browsing for.
		/// </summary>
		[
		Description( "The description of the folder browsing for." )
		]
		public string Description {
			get {
				return _browser.Description;
			}
			set {
				_browser.Description = value;
			}
		}

		/// <summary>
		/// Gets or sets a value that indicates if the folder browser can only return computers. If the user selects anything other than a computer, the OK button is grayed. 
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser can only return computers. If the user selects anything other than a computer, the OK button is grayed. " ),
		DefaultValue( false )
		]
		public bool BrowseForComputer {
			get {
				return ( ((int)_browser.Style) & 4069 ) == 4096;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 4096 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~4096 );
			}
		}

		/// <summary>
		/// Gets or sets a value that indicates if the folder browser can return any object that it can return. 
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser can return any object that it can return." ),
		DefaultValue( false )
		]
		public bool BrowseForEverything {
			get {
				return ( ((int)_browser.Style) & 16384 ) == 16384;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 16384 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~16384 );
			}
		}

		/// <summary>
		/// Gets or sets a value that indicates if the folder browser can only return printers. If the user selects anything other than a printer, the OK button is grayed.
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser can only return printers. If the user selects anything other than a printer, the OK button is grayed." ),
		DefaultValue( false )
		]
		public bool BrowseForPrinter {
			get {
				return ( ((int)_browser.Style) & 8192 ) == 8192;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 8192 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~8192 );
			}
		}

		/// <summary>
		/// Gets or sets a value that indicates if the folder browser will not include network folders below the domain level in the dialog box's tree view control, or allow navigation to network locations outside of the domain.
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser will not include network folders below the domain level in the dialog box's tree view control, or allow navigation to network locations outside of the domain." ),
		DefaultValue( false )
		]
		public bool RestrictToDomain {
			get {
				return ( ((int)_browser.Style) & 2 ) == 2;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 2 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~2 );
			}
		}

		/// <summary>
		/// Gets or sets a value that indicates if the folder browser will only return local file system directories. If the user selects folders that are not part of the local file system, the OK button is grayed.
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser will only return local file system directories. If the user selects folders that are not part of the local file system, the OK button is grayed." ),
		DefaultValue( true )
		]
		public bool RestrictToFileSystem {
			get {
				return ( ((int)_browser.Style) & 1 ) == 1;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 1 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~1 );
			}
		}

		/// <summary>
		/// Gets or sets a value that indicates if the folder browser will only return obejcts of the local file system that are within the root folder or a subfolder of the root folder. If the user selects a subfolder of the root folder that is not part of the local file system, the OK button is grayed.
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser will only return obejcts of the local file system that are within the root folder or a subfolder of the root folder. If the user selects a subfolder of the root folder that is not part of the local file system, the OK button is grayed." ),
		DefaultValue( false )
		]
		public bool RestrictToSubfolders {
			get {
				return ( ((int)_browser.Style) & 8 ) == 8;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 8 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~8 );
			}
		}
	
		/// <summary>
		/// Gets or sets a value that indicates if the folder browser includes a TextBox control in the browse dialog box that allows the user to type the name of an item. 
		/// </summary>
		[
		Category( "Options" ),
		Description( "Indicates if the folder browser includes a TextBox control in the browse dialog box that allows the user to type the name of an item." ),
		DefaultValue( false )
		]
		public bool ShowTextBox {
			get {
				return ( ((int)_browser.Style) & 16 ) == 16;
			}
			set {
				if( value )
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) | 16 );
				else
					_browser.Style = (FolderBrowserStyles)( ((int)_browser.Style) & ~16 );

			}
		}

		#endregion

		#region Methods
		/// <summary>
		/// Displasy the form as a modal dialog.
		/// </summary>
		/// <returns>
		///		Returns one of the <see cref="DialogResult"/> values.
		/// </returns>
		public DialogResult ShowDialog() {
			return _browser.ShowDialog();
		}
		
		/// <summary>
		/// Displasy the form as a modal dialog.
		/// </summary>
		/// <param name="owner">
		///		The parent window that owns the dialog.
		/// </param>
		/// <returns>
		///		Returns one of the <see cref="DialogResult"/> values.
		/// </returns>
		public DialogResult ShowDialog( IWin32Window owner ) {
			return _browser.ShowDialog( owner );
		}

		/// <summary>
		/// Prompts the user for a folder.
		/// </summary>
		/// <returns>
		///		Returns the selected folder, or null.
		/// </returns>
		public static string Prompt() {
			return Prompt( PluginCore.FolderBrowserFolder.Desktop, "" );
		}

		/// <summary>
		/// Prompts the user for a folder.
		/// </summary>
		/// <param name="description">
		///		A description of the folder the user is browsing for.
		/// </param>
		/// <param name="startLocation">
		///		One of the <see cref="FolderBrowserFolder"/> values 
		///		that indicates the starting location.
		/// </param>
		/// <param name="owner">
		///		The parent window.
		/// </param>
		/// <returns>
		///		Returns the selected folder, or null.
		/// </returns>
		public static string Prompt( IWin32Window owner, PluginCore.FolderBrowserFolder startLocation, string description ) {
			BrowseForFolderPrompt prompt = new BrowseForFolderPrompt( startLocation, description );
			if( prompt.ShowDialog( owner ) == DialogResult.OK )
				return prompt.Folder;

			return null;
		}

		/// <summary>
		/// Prompts the user for a folder.
		/// </summary>
		/// <param name="description">
		///		A description of the folder the user is browsing for.
		/// </param>
		/// <param name="startLocation">
		///		One of the <see cref="FolderBrowserFolder"/> values 
		///		that indicates the starting location.
		/// </param>
		/// <returns>
		///		Returns the selected folder, or null.
		/// </returns>
		public static string Prompt( PluginCore.FolderBrowserFolder startLocation, string description ) {
			BrowseForFolderPrompt prompt = new BrowseForFolderPrompt( startLocation, description );
			if( prompt.ShowDialog() == DialogResult.OK )
				return prompt.Folder;

			return null;
		}

		/// <summary>
		/// Prompts the user for a folder.
		/// </summary>
		/// <param name="description">
		///		A description of the folder the user is browsing for.
		/// </param>
		/// <param name="startLocation">
		///		One of the <see cref="FolderBrowserFolder"/> values 
		///		that indicates the starting location.
		/// </param>
		/// <param name="owner">
		///		The Parent window.
		/// </param>
		/// <returns>
		///		Returns the selected folder, or null.
		/// </returns>
		public static string Show( IWin32Window owner, PluginCore.FolderBrowserFolder startLocation, string description ) {
			return Prompt( owner, startLocation, description );
		}

		/// <summary>
		/// Prompts the user for a folder.
		/// </summary>
		/// <param name="description">
		///		A description of the folder the user is browsing for.
		/// </param>
		/// <param name="startLocation">
		///		One of the <see cref="FolderBrowserFolder"/> values 
		///		that indicates the starting location.
		/// </param>
		/// <returns>
		///		Returns the selected folder, or null.
		/// </returns>
		public static string Show( PluginCore.FolderBrowserFolder startLocation, string description ) {
			return Prompt( startLocation, description );
		}

		#endregion
		
	} 

	#region FolderBrowserFolder enum
	///<summary>
	///Summary of FolderBrowserFolder
	///</summary>
	public enum FolderBrowserFolder {
		/// <summary>
		/// The user's desktop.
		/// </summary>
		Desktop		= 0x0000,

		/// <summary>
		/// The user's favorites folder.
		/// </summary>
		Favorites	= 0x0006,

		/// <summary>
		/// The contents of the My Computer icon. 
		/// </summary>
		MyComputer	= 0x0011,

		/// <summary>
		/// The user's My Documents folder. 
		/// </summary>
		MyDocuments	= 0x0005,

		/// <summary>
		/// User's location to store pictures. 
		/// </summary>
		MyPictures	= 0x0027,

		/// <summary>
		/// Network and dial-up connections. 
		/// </summary>
		NetAndDialupConnections	= 0x0032,

		/// <summary>
		/// The network neighborhood. 
		/// </summary>
		NetoworkNeighborhood	= 0x0012,

		/// <summary>
		/// A folder containing installed printers. 
		/// </summary>
		Printers	= 0x0004,

		/// <summary>
		/// A folder containing shortcuts to recently opened files. 
		/// </summary>
		Recent		= 0x0008,

		/// <summary>
		/// A folder containing shortcuts to applications to send documents to. 
		/// </summary>
		SendTo		= 0x0009,

		/// <summary>
		/// The user's Start menu. 
		/// </summary>
		StartMenu	= 0x000B,

		/// <summary>
		/// The user's file templates. 
		/// </summary>
		Templates	= 0x0015
	} // end enum FolderBrowserFolder
	#endregion
}
