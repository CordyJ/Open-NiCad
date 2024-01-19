using System;
using System.Collections;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Windows.Forms;

namespace PluginCore {

	/// <summary>
	/// Summary description for LineControl.
	/// </summary>
	public class LineControl : System.Windows.Forms.Control {
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.Container components = null;

		#region private var's

		private Color			_highlight		= Color.FromKnownColor( KnownColor.ControlLightLight );
		private Color			_shadow			= Color.FromKnownColor( KnownColor.ControlDark );
		private Orientation		_orientation	= Orientation.Horizontal;
		private	bool			_beveled		= true;

		#endregion

		#region ctor's

		/// <summary>
		///  Initializes a new instance of the Line class.
		/// </summary>
		public LineControl() {
			ResizeRedraw	= true;
			Width			= 100;
			Height			= 2;
		}

		#endregion

		#region Properties

		/// <summary>
		/// Gets or sets a value that indicates if the line should be drawn with a 
		/// beveled look. If false, only the <see cref="Highlight"/> color is used.
		/// </summary>
		[
		Category( "Appearance" ),
		Description( "Indicates if the line should be drawn with a  beveled look. If false, only the Highlight color is used." )
		]
		public bool Beveled {
			get {
				return _beveled;
			}
			set {
				_beveled = value;
			}
		}

		/// <summary>
		/// Gets or sets the highlight color.
		/// </summary>
		[
		Category( "Appearance" ),
		Description( "The highlight color" )
		]
		public Color Highlight {
			get {
				return _highlight;
			}
			set {
				_highlight = value;
			}
		}

		/// <summary>
		/// Gets or sets the shadow color.
		/// </summary>
		[
		Category( "Appearance" ),
		Description( "The shadow color" )
		]
		public Color Shadow {
			get {
				return _shadow;
			}
			set {
				_shadow = value;
			}
		}

		/// <summary>
		/// Gets or sets the orientation of the line.
		/// </summary>
		[
		Category( "Appearance" ),
		Description( "The orientation of the line." )
		]
		public Orientation Orientation {
			get {
				return _orientation;
			}
			set {
				_orientation = value;
			}
		}

		/// <summary>
		/// Gets the width of the line.
		/// </summary>
		[
		Browsable( false ),
		Category( "Appearance" ),
		Description( "The width of the line." )
		]
		public int LineWidth {
			get {
				return Orientation == Orientation.Horizontal ? Height : Width;
			}
		}

		#endregion

		#region Methods

		/// <summary>
		/// Overrides <see cref="Control.OnPaint"/>.
		/// </summary>
		/// <param name="pe"></param>
		protected override void OnPaint( PaintEventArgs pe ) {
			Graphics	g	= pe.Graphics;
			Brush		h	= null;
			Brush		s	= null;

			if( Beveled ) {
				h = new SolidBrush( Highlight );
				s = new SolidBrush( Shadow );

				if( Orientation == Orientation.Horizontal ) {
					g.FillRectangle( s, 0, 0, Width, LineWidth / 2 );
					g.FillRectangle( h, 0, LineWidth / 2, Width, LineWidth / 2 );
				}
				else {
					g.FillRectangle( s, 0, 0, LineWidth / 2, Height );
					g.FillRectangle( h, LineWidth / 2, 0, LineWidth / 2, Height );
				}
			}
			else {
				h = new SolidBrush( Highlight );

				if( Orientation == Orientation.Horizontal )
					g.FillRectangle( h, 0, 0, Width, LineWidth );
				else
					g.FillRectangle( h, 0, 0, LineWidth, Height );
			}

			if( h != null )
				h.Dispose();

			if( s != null )
				s.Dispose();
		}

		#endregion
	}

}
