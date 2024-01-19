#region CVS Version Header
/*
 * $Id: TreeFeedsDrawFilter.cs,v 1.3 2006/09/22 16:34:19 t_rendelmann Exp $
 * Last modified by $Author: t_rendelmann $
 * Last modified at $Date: 2006/09/22 16:34:19 $
 * $Revision: 1.3 $
 */
#endregion

#region CVS Version Log
/*
 * $Log: TreeFeedsDrawFilter.cs,v $
 * Revision 1.3  2006/09/22 16:34:19  t_rendelmann
 * added CVS header and change history
 *
 */
#endregion

using System;
using System.Drawing;
using Infragistics.Win;
using Infragistics.Win.UltraWinTree;
using RssBandit.WinGui.Controls;
using RssBandit.WinGui.Utility;

namespace RssBandit.WinGui
{
	/// <summary>
	/// Used to call multiple drawing filters
	/// </summary>
	internal class TreeFeedsDrawFilter : IUIElementDrawFilter
	{
		private IUIElementDrawFilter[] _drawFilter;
		private DrawPhase[] _drawPhase;
		private int _drawFilterCount = 0;

		public TreeFeedsDrawFilter() {
			_drawFilter = new IUIElementDrawFilter[1];
			_drawFilter[0] = new TreeFeedsRootNodeDrawFilter();
			//_drawFilter[1] = new DropHightLightDrawFilter();
			_drawFilterCount = _drawFilter.Length;
			_drawPhase = new DrawPhase[_drawFilterCount];
		}

		/// <summary>
		/// Gets the dragdrop draw filter. Used to access events and
		/// properties used there.
		/// </summary>
		/// <value>The dragdrop draw filter.</value>
		public DropHightLightDrawFilter DragdropDrawFilter {
			get { return (DropHightLightDrawFilter) _drawFilter[1]; }
		}
		
		#region IUIElementDrawFilter

		/// <summary>
		/// Called before each element is about to be drawn.
		/// </summary>
		/// <param name="drawParams">Exposes properties required for drawing an element (e.g. Element, Graphics, InvalidRect etc.)</param>
		/// <returns>
		/// Bit flags indicating which phases of the drawing operation to filter. The DrawElement method will be called only for those phases.
		/// </returns>
		DrawPhase IUIElementDrawFilter.GetPhasesToFilter( ref UIElementDrawParams drawParams )
		{
			DrawPhase phases = DrawPhase.None;
			for (int i=0; i < _drawFilterCount; i++) {
				_drawPhase[i] = _drawFilter[i].GetPhasesToFilter(ref drawParams);
				if (_drawPhase[i] != DrawPhase.None)
					phases |= _drawPhase[i];
			}
			return phases;
		}

		/// <summary>
		/// Called during the drawing operation of a UIElement for a specific phase
		/// of the operation. This will only be called for the phases returned
		/// from the GetPhasesToFilter method.
		/// </summary>
		/// <param name="drawPhase">Contains a single bit which identifies the current draw phase.</param>
		/// <param name="drawParams">Exposes properties required for drawing an element (e.g. Element, Graphics, InvalidRect etc.)</param>
		/// <returns>
		/// Returning true from this method indicates that this phase has been handled and the default processing should be skipped.
		/// </returns>
		bool IUIElementDrawFilter.DrawElement( DrawPhase drawPhase, ref UIElementDrawParams drawParams )
		{
			bool ret = false;
			for (int i=0; i < _drawFilterCount; i++) {
				if (_drawPhase[i] != DrawPhase.None && 
				    _drawFilter[i].DrawElement(drawPhase, ref drawParams))
					ret = true;
			}
			return ret;
		}

		#endregion
	}

	#region TreeFeedsRootNodeDrawFilter

	/// <summary>
	/// Used to impl. custom root UltraTreeNode drawing additions
	/// </summary>
	internal class TreeFeedsRootNodeDrawFilter : IUIElementDrawFilter {
		
		#region IUIElementDrawFilter

		/// <summary>
		/// Called before each element is about to be drawn.
		/// </summary>
		/// <param name="drawParams">Exposes properties required for drawing an element (e.g. Element, Graphics, InvalidRect etc.)</param>
		/// <returns>
		/// Bit flags indicating which phases of the drawing operation to filter. The DrawElement method will be called only for those phases.
		/// </returns>
		DrawPhase IUIElementDrawFilter.GetPhasesToFilter( ref UIElementDrawParams drawParams ) {
			UltraTreeNode treeNode = drawParams.Element.GetContext( typeof(UltraTreeNode), true ) as UltraTreeNode;
			if (treeNode != null) {
				
				//TODO: FIX, DOES NOT YET WORK AS EXPECTED:
				//				if(drawParams.Element is ExpansionIndicatorUIElement )
				//					return DrawPhase.AfterDrawElement; //to extend the clickable area
				
				if (treeNode.Level == 0) {
					// draw complete area (Group Header):
					if(drawParams.Element is EditorWithTextDisplayTextUIElement )
						return DrawPhase.BeforeDrawForeground; //Middle side
					//
					if(drawParams.Element is PreNodeAreaUIElement )
						return DrawPhase.BeforeDrawForeground; //Left text
					if(drawParams.Element is EditorWithTextUIElement )
						return DrawPhase.BeforeDrawForeground; //Middle side
					if(drawParams.Element is NodeSelectableAreaUIElement )
						return DrawPhase.BeforeDrawForeground; //Right side
					//
				} else if (treeNode.Level > 0) {
					// draw the part after the selectable UI area
					// (here: unread counter)
					if(drawParams.Element is NodeSelectableAreaUIElement )
						return DrawPhase.AfterDrawElement;
				}
			}
			return DrawPhase.None;
		}

		/// <summary>
		/// Called during the drawing operation of a UIElement for a specific phase
		/// of the operation. This will only be called for the phases returned
		/// from the GetPhasesToFilter method.
		/// </summary>
		/// <param name="drawPhase">Contains a single bit which identifies the current draw phase.</param>
		/// <param name="drawParams">Exposes properties required for drawing an element (e.g. Element, Graphics, InvalidRect etc.)</param>
		/// <returns>
		/// Returning true from this method indicates that this phase has been handled and the default processing should be skipped.
		/// </returns>
		bool IUIElementDrawFilter.DrawElement( DrawPhase drawPhase, ref UIElementDrawParams drawParams ) {
			UltraTreeNode treeNode = drawParams.Element.GetContext( typeof(UltraTreeNode), true ) as UltraTreeNode;
			if ( treeNode != null ) {
				//TODO: FIX, DOES NOT YET WORK AS EXPECTED:
				//				if(drawParams.Element is ExpansionIndicatorUIElement) {
				//					ExpansionIndicatorUIElement elem = drawParams.Element as ExpansionIndicatorUIElement;
				//					if (elem != null && treeNode.HasExpansionIndicator) {
				//						int ext = 4; //to extend the clickable area
				//						elem.Rect = new Rectangle(elem.Rect.Left - ext, elem.Rect.Top - ext, elem.Rect.Bottom + ext, elem.Rect.Right + ext);
				//						return false; 
				//					}
				//				}

				if(treeNode.Level > 0) {
					TreeFeedsNodeBase feedsNode = treeNode as TreeFeedsNodeBase;
					if (drawPhase == DrawPhase.AfterDrawElement && 
					    feedsNode != null && feedsNode.Control != null) {
						int unread = feedsNode.UnreadCount;
						if (unread > 0) {
							// this image width is a workaround to extend the nods's clickable
							// area to include the unread count visual representation...
							int clickableAreaExtenderImageWidth = feedsNode.Control.RightImagesSize.Width;
							
							string st = String.Format("({0})", unread);
							UIElement uiElement = drawParams.Element; 
							Rectangle ur = uiElement.Rect;
							using (Brush unreadColorBrush = new SolidBrush(FontColorHelper.UnreadColor)) {
								drawParams.Graphics.DrawString(st, FontColorHelper.UnreadFont, 
								                               unreadColorBrush, ur.X + ur.Width - clickableAreaExtenderImageWidth, 
								                               ur.Y, StringFormat.GenericDefault);
							}
							return true;
						}
						
					} 
					return false;
				}
				//
				if(treeNode.Level==0) {
					RectangleF initialRect = drawParams.Element.RectInsideBorders;
					Rectangle r = new Rectangle((int)initialRect.Left,(int)initialRect.Top,(int)initialRect.Width,(int)initialRect.Height);
					r.Width = treeNode.Control.DisplayRectangle.Width+300;
					r.Height = treeNode.ItemHeightResolved;

					if(drawParams.Element is EditorWithTextDisplayTextUIElement ) {
						return false;
					}
					if(drawParams.Element is PreNodeAreaUIElement) {
						//Left Side
						//r.Height+=2;
						r.Width++;
					}
					if(drawParams.Element is EditorWithTextUIElement) {
						//Middle 
						r.Y--;
						r.X--;
						//r.Height++;
						r.Width++;
					}
					if(drawParams.Element is NodeSelectableAreaUIElement) {
						//Rigth side
						//r.Height+=2;
						r.Width++;
					}
					TreeFeedsNodeGroupHeaderPainter.PaintOutlook2003Header( drawParams.Graphics, r);
					return true;
				}
			}

			// To return FALSE from this method indicates that the element should draw itself as normal.
			// To return TRUE  from this method indicates that the element should not draw itself. 
			// Return true to prevent further drawing by the element
			return false;
		}

		#endregion
	}

	#endregion


	#region DragDropHighlight draw filter
	
	//Enumerates the possiblt Drop States
	[System.Flags] internal enum DropLinePositionEnum {
		None = 0,
		OnNode = 1,
		AboveNode = 2,
		BelowNode = 4,
		All = OnNode | AboveNode | BelowNode
	}
	
	internal class DropHightLightDrawFilter: IUIElementDrawFilter 
	{
		//This class has to implement the DrawFilter Interface
		//so it can be used as a DrawFilter by the tree

		public event System.EventHandler Invalidate;
		//public delegate void InvalidateEventHandler( object sender, EventArgs e );

		public event QueryStateAllowedForNodeEventHandler QueryStateAllowedForNode;
		public delegate void QueryStateAllowedForNodeEventHandler( object sender, QueryStateAllowedForNodeEventArgs e );

		//Used by the QueryStateAllowedForNode event
		public class QueryStateAllowedForNodeEventArgs:System.EventArgs {
			public UltraTreeNode Node ;
			public DropLinePositionEnum DropLinePosition;
			public DropLinePositionEnum StatesAllowed ;
		}

		public DropHightLightDrawFilter() {
			//Initialize the properties to the defaults
			InitProperties();
		} 

		//Initialize the properties to the defaults
		private void InitProperties() {
			mvarDropHighLightNode = null;
			mvarDropLinePosition = DropLinePositionEnum.None;
			mvarDropHighLightBackColor = System.Drawing.SystemColors.Highlight;
			mvarDropHighLightForeColor = System.Drawing.SystemColors.HighlightText;
			mvarDropLineColor = System.Drawing.SystemColors.ControlText;
			mvarEdgeSensitivity = 0;
			mvarDropLineWidth = 2;
		}


		//Clean up
		public void Dispose() {
			mvarDropHighLightNode = null;
		}

		//The DropHighLightNode is a reference to the node the
		//Mouse is currently over
		private UltraTreeNode mvarDropHighLightNode;
		public UltraTreeNode DropHightLightNode {
			get {
				return mvarDropHighLightNode;
			}
			set {
				//If the Node is being set to the same value,
				// just exit
				if (mvarDropHighLightNode.Equals(value)) {	
					return;
				}
				mvarDropHighLightNode = value;
				//The DropNode has changed.
				PositionChanged();
			}
		}

		private DropLinePositionEnum mvarDropLinePosition;
		public DropLinePositionEnum DropLinePosition {
			get {
				return mvarDropLinePosition;
			}
			set {
				//If the position is the same as it was, 
				//just exit
				if (mvarDropLinePosition == value) {
					return;
				}
				mvarDropLinePosition = value;
				//The Drop Position has changed
				PositionChanged();
			}
		}

		//The width of the DropLine
		private int mvarDropLineWidth;
		public int DropLineWidth {
			get {
				return mvarDropLineWidth;
			}
			set {
				mvarDropLineWidth = value;
			}
		}

		//The BackColor of the DropHighLight node
		//This only affect the node when it is being dropped On. 
		//Not Above or Below. 
		private System.Drawing.Color mvarDropHighLightBackColor; 
		public System.Drawing.Color DropHighLightBackColor {
			get {
				return mvarDropHighLightBackColor;
			}
			set {
				mvarDropHighLightBackColor = value;
			}
		}

		//The ForeColor of the DropHighLight node
		//This only affect the node when it is being dropped On. 
		//Not Above or Below. 
		private System.Drawing.Color  mvarDropHighLightForeColor;
		public System.Drawing.Color  DropHighLightForeColor {
			get {
				return mvarDropHighLightForeColor;
			}
			set {
				mvarDropHighLightForeColor = value;
			}
		}

		//The color of the DropLine
		private System.Drawing.Color  mvarDropLineColor ;
		public System.Drawing.Color DropLineColor {
			get {
				return mvarDropLineColor;
			}
			set {
				mvarDropLineColor = value;
			}
		}

		//Determines how close to the top or bottom edge of a node
		//the mouse must be to be consider dropping Above or Below
		//respectively. 
		//By default the top 1/3 of the node is Above, the bottom 1/3
		//is Below, and the middle is On. 
		private int mvarEdgeSensitivity ;
		public int EdgeSensitivity {
			get {
				return mvarEdgeSensitivity;
			}
			set {
				mvarEdgeSensitivity = value;
			}
		}

		//When the DropNode or DropPosition change, we fire the
		//Invalidate event to let the program know to invalidate
		//the Tree control. 
		//This is neccessary since the DrawFilter does not have a 
		//reference to the Tree Control (although it probably could)
		private void PositionChanged() {
			// if nobody is listening then just return
			//
			if ( null == this.Invalidate)
				return;

			System.EventArgs e = System.EventArgs.Empty;
		
			this.Invalidate(this, e);
		}

		//Set the DropNode to Nothing and the position to None. This
		//Will clear whatever Drophighlight is in the tree
		public void ClearDropHighlight() {
			SetDropHighlightNode(null, DropLinePositionEnum.None);
		}

		//Call this proc every time the DragOver event of the 
		//Tree fires. 
		//Note that the point pass in MUST be in Tree coords, not
		//form coords
		public void SetDropHighlightNode(UltraTreeNode Node, System.Drawing.Point PointInTreeCoords ) {
			//The distance from the edge of the node used to 
			//determine whether to drop Above, Below, or On a node
			int DistanceFromEdge; 
        
			//The new DropLinePosition
			DropLinePositionEnum NewDropLinePosition;
		
			DistanceFromEdge = mvarEdgeSensitivity;
			//Check to see if DistanceFromEdge is 0
			if (DistanceFromEdge == 0) {
				//It is, so we use the default value - one third. 
				DistanceFromEdge = Node.Bounds.Height / 3;
			}

			//Determine which part of the node the point is in
			if (PointInTreeCoords.Y < (Node.Bounds.Top + DistanceFromEdge)) {
				//Point is in the top of the node
				NewDropLinePosition = DropLinePositionEnum.AboveNode;
			}
			else {
				if (PointInTreeCoords.Y > ((Node.Bounds.Bottom - DistanceFromEdge) - 1)) {
					//Point is in the bottom of the node
					NewDropLinePosition = DropLinePositionEnum.BelowNode;
				}
				else {
					//Point is in the middle of the node
					NewDropLinePosition = DropLinePositionEnum.OnNode;
				}
			}

			//Now that we have the new DropLinePosition, call the
			//real proc to get things rolling
			SetDropHighlightNode(Node, NewDropLinePosition);
		}

		private void SetDropHighlightNode(UltraTreeNode Node , DropLinePositionEnum DropLinePosition ) {
			//Use to store whether there have been any changes in 
			//DropNode or DropLinePosition
			bool IsPositionChanged = false;

			try {
				//Check to see if the nodes are equal and if 
				//the dropline position are equal
				if (mvarDropHighLightNode != null && mvarDropHighLightNode.Equals(Node) && (mvarDropLinePosition == DropLinePosition)) {
					//They are both equal. Nothing has changed. 
					IsPositionChanged = false;
				}
				else {
					//One or both have changed
					IsPositionChanged = true;
				}
			}
			catch {
				//If we reach this code, it means mvarDropHighLightNode 
				//is null, so it could not be compared
				if (mvarDropHighLightNode == null) {
					//Check to see if Node is nothing, so we//ll know
					//if Node = mvarDropHighLightNode
					IsPositionChanged = !(Node == null);
				}
			}

			//Set both properties without calling PositionChanged
			mvarDropHighLightNode = Node;
			mvarDropLinePosition = DropLinePosition;

			//Check to see if the PositionChanged
			if (IsPositionChanged) {
				//Position did change.
				PositionChanged();
			}
		}

		//Only need to trap for 2 phases:
		//AfterDrawElement: for drawing the DropLine
		//BeforeDrawElement: for drawing the DropHighlight
		Infragistics.Win.DrawPhase Infragistics.Win.IUIElementDrawFilter.GetPhasesToFilter(ref Infragistics.Win.UIElementDrawParams drawParams) {
			return Infragistics.Win.DrawPhase.AfterDrawElement | Infragistics.Win.DrawPhase.BeforeDrawElement;
		}

		//The actual drawing code
		bool Infragistics.Win.IUIElementDrawFilter.DrawElement(Infragistics.Win.DrawPhase drawPhase, ref Infragistics.Win.UIElementDrawParams drawParams) {
			Infragistics.Win.UIElement aUIElement;
			System.Drawing.Graphics g;
			UltraTreeNode aNode;

			//If there//s no DropHighlight node or no position
			//specified, then we don//t need to draw anything special. 
			//Just exit Function
			if ((mvarDropHighLightNode == null) || (mvarDropLinePosition == DropLinePositionEnum.None)) {
				return false;
			}

			//Create a new QueryStateAllowedForNodeEventArgs object
			//to pass to the event
			QueryStateAllowedForNodeEventArgs eArgs = new QueryStateAllowedForNodeEventArgs();

			//Initialize the object with the correct info
			eArgs.Node = mvarDropHighLightNode;
			eArgs.DropLinePosition = this.mvarDropLinePosition;

			//Default to all states allowed. 
			eArgs.StatesAllowed = DropLinePositionEnum.All;

			//Raise the event
			this.QueryStateAllowedForNode(this, eArgs);

			//Check to see if the user allowed the current state
			//for this node. If not, exit function
			if ((eArgs.StatesAllowed & mvarDropLinePosition) != mvarDropLinePosition) {
				return false;
			}

			//Get the element being drawn
			aUIElement = drawParams.Element;

			//Determine which drawing phase we are in. 
			switch (drawPhase) {
				case Infragistics.Win.DrawPhase.BeforeDrawElement: {
					//We are in BeforeDrawElement, so we are only concerned with 
					//drawing the OnNode state. 
					if ((mvarDropLinePosition & DropLinePositionEnum.OnNode) == DropLinePositionEnum.OnNode) {
						//Check to see if we are drawing a NodeTextUIElement
						if (aUIElement.GetType() == typeof(Infragistics.Win.UltraWinTree.NodeTextUIElement)) {
							//Get a reference to the node that this
							//NodeTextUIElement is associated with
							aNode = (UltraTreeNode)aUIElement.GetContext(typeof(UltraTreeNode));

							//See if this is the DropHighlightNode
							if (aNode.Equals(mvarDropHighLightNode)) {
								//Set the ForeColor and Backcolor of the node 
								//to the DropHighlight colors 
								//Note that AppearanceData only affects the
								//node for this one paint. It will not
								//change any properties of the node
								drawParams.AppearanceData.BackColor = mvarDropHighLightBackColor;
								drawParams.AppearanceData.ForeColor = mvarDropHighLightForeColor;
							}
						}
					}
					break;
				}
				case Infragistics.Win.DrawPhase.AfterDrawElement: {
					//We're in AfterDrawElement
					//So the only states we are conderned with are
					//Below and Above
					//Check to see if we are drawing the Tree Element
					if (aUIElement.GetType() == typeof(Infragistics.Win.UltraWinTree.UltraTreeUIElement)) {
						//Declare a pen to us for drawing Droplines
						System.Drawing.Pen p = new System.Drawing.Pen(mvarDropLineColor, mvarDropLineWidth);

						//Get a reference to the Graphics object
						//we are drawing to. 
						g = drawParams.Graphics;

						//Get the NodeSelectableAreaUIElement for the 
						//current DropNode. We will use this for
						//positioning and sizing the DropLine
						Infragistics.Win.UltraWinTree.NodeSelectableAreaUIElement tElement ;
						tElement = (Infragistics.Win.UltraWinTree.NodeSelectableAreaUIElement)drawParams.Element.GetDescendant(typeof(Infragistics.Win.UltraWinTree.NodeSelectableAreaUIElement), mvarDropHighLightNode);

						//The left edge of the DropLine
						int LeftEdge = tElement.Rect.Left - 4;

						//We need a reference to the control to 
						//determine the right edge of the line
						UltraTree aTree; 
						aTree = (UltraTree)tElement.GetContext(typeof(UltraTree));
						int RightEdge = aTree.DisplayRectangle.Right -4;

						//Used to store the Vertical position of the 
						//DropLine
						int LineVPosition;

						if ((mvarDropLinePosition & DropLinePositionEnum.AboveNode) == DropLinePositionEnum.AboveNode) {
							//Draw line above node
							LineVPosition = mvarDropHighLightNode.Bounds.Top;
							g.DrawLine(p, LeftEdge, LineVPosition, RightEdge, LineVPosition);
							p.Width = 1;
							g.DrawLine(p, LeftEdge, LineVPosition - 3, LeftEdge, LineVPosition + 2);
							g.DrawLine(p, LeftEdge + 1, LineVPosition - 2, LeftEdge + 1, LineVPosition + 1);
							g.DrawLine(p, RightEdge, LineVPosition - 3, RightEdge, LineVPosition + 2);
							g.DrawLine(p, RightEdge - 1, LineVPosition - 2, RightEdge - 1, LineVPosition + 1);
						}
						if ((mvarDropLinePosition & DropLinePositionEnum.BelowNode) == DropLinePositionEnum.BelowNode) {
							//Draw Line below node
							LineVPosition = mvarDropHighLightNode.Bounds.Bottom;
							g.DrawLine(p, LeftEdge, LineVPosition, RightEdge, LineVPosition);
							p.Width = 1;
							g.DrawLine(p, LeftEdge, LineVPosition - 3, LeftEdge, LineVPosition + 2);
							g.DrawLine(p, LeftEdge + 1, LineVPosition - 2, LeftEdge + 1, LineVPosition + 1);
							g.DrawLine(p, RightEdge, LineVPosition - 3, RightEdge, LineVPosition + 2);
							g.DrawLine(p, RightEdge - 1, LineVPosition - 2, RightEdge - 1, LineVPosition + 1);
						}
					}
					break;
				}				
			}
			return false;
		}
	}
	#endregion
	
}
