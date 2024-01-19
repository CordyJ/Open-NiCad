#region CVS Version Header
/*
 * $Id: WinGUIWidgetHelpers.cs,v 1.38 2004/07/12 11:26:24 t_rendelmann Exp $
 * Last modified by $Author: t_rendelmann $
 * Last modified at $Date: 2004/07/12 11:26:24 $
 * $Revision: 1.38 $
 */
#endregion

using System;
using System.Collections;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Globalization;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

using RssBandit.WinGui.Interfaces;
using RssComponents;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// NodeInfo keeps the infos we need to deal with different TreeNode types.
	/// </summary>
	public class NodeInfo
	{
		public object Tag;
		public ContextMenu ContextMenu;

		private UltraTreeNode _node;
		private bool		_editable, _anyUnread;
		private int		_unreadCount;
		private int		_highlightCount;
		private FeedNodeType _type;
		private ArrayList _allowedChilds;

		private NodeInfo(){
			_editable = false;
			_anyUnread = false;
			_unreadCount = 0;
			_highlightCount = 0;
		}
		public NodeInfo(UltraTreeNode node, FeedNodeType type, ContextMenu menu):this(){
			this._node = node;
			this._node.Tag = this;
			this.Type = type;
			this.ContextMenu = menu;
		}
		public UltraTreeNode Node { get { return _node; } }
		public NodeInfo Parent { get { return NodeHelper.GetInfo(_node.Parent); } }
		public int ImageIndex { get { return (int)this._node.Override.NodeAppearance.Image; } set { this._node.Override.NodeAppearance.Image = value; } }
		public int SelectedImageIndex { get { return (int)this._node.Override.ActiveNodeAppearance.Image; } set { this._node.Override.ActiveNodeAppearance.Image = value; } }
		public int ExpandedImageIndex { get { return (int)this._node.Override.ExpandedNodeAppearance.Image; } set { this._node.Override.ExpandedNodeAppearance.Image = value; } }
		public Color ForeColor { 
			get { return this._node.Override.NodeAppearance.ForeColor; } 
			set { if (this._node.Override.NodeAppearance.ForeColor != value)
					  this._node.Override.NodeAppearance.ForeColor = value; 
			} 
		}

		public FeedNodeType Type { get { return _type; } set { _type = value; } }
		public bool Editable { get { return _editable; } set { _editable = value; } }

		public bool IsRoot { get { return (_type == FeedNodeType.Root); } }
		public bool IsFeed { get {  return (_type == FeedNodeType.Feed); } }
		public bool IsFeedCategory { get {  return (_type == FeedNodeType.Category); } }

		public void AllowDragDropChild(FeedNodeType t) {
			if (_allowedChilds == null)
				_allowedChilds = new ArrayList(1);
			_allowedChilds.Add(t);
		}

		public bool IsChildAllowed(FeedNodeType t) {
			return (_allowedChilds != null && _allowedChilds.Contains(t));
		}

		public bool Equals(NodeInfo info) {
			return (this == info && this.Node == info.Node);
		}

		/// <summary>
		/// AnyUnread and UnreadCount are working interconnected:
		/// if you set AnyUnread to true, this will update the visualized info to
		/// use the Unread Font, but no read counter state info. UnreadCount is NOT
		/// modified anyway. Otherwise, if you set AnyUnread to false, it will 
		/// refresh the caption rendering to default.
		/// </summary>
		public bool AnyUnread {
			get {	return (_anyUnread || _unreadCount > 0);  }
			set {	
				if (_anyUnread != value) { 
					_anyUnread = value; 
					if (_anyUnread) {
						//this.Text = this.Key;		// refresh visual info
					} else if (_unreadCount == 0){ // _anyUnread == false
						//this.Text = this.Key;		// refresh visual info
					}
				}
			}
		}

		/// <summary>
		/// AnyUnread and UnreadCount are working interconnected:
		/// if you set UnreadCount to non zero, AnyUnread will be set to true and
		/// then updates the visualized info to use the Unread Font and 
		/// read counter state info. If UnreadCount is set to zero,
		/// also AnyUnread is reset to false and refresh the caption to default.
		/// </summary>
		public int UnreadCount {
			get {	return _unreadCount;  }
			set {	
				if (value > 0) {
					_anyUnread = true;
					if (value != _unreadCount) {
						_unreadCount = value; 
					}
				}
				else {
					_anyUnread = false;
					_unreadCount = 0; 
				}
			}
		}

		public int HighlightCount {
			get {	return _highlightCount;  }
			set {	
				if (value > 0) {
					if (value != _highlightCount) {
						_highlightCount = value; 
					}
				}
				else {
					_highlightCount = 0; 
				}
			}
		}

		public void UpdateReadStatus(NodeInfo info, int readCounter) {
			if (info == null) return;
			
			if (readCounter <= 0) {			// mark read

				// traverse tree: upwards, one by one. On every step
				// look for unread childs (go down). If there is one, stop walking up.
				// If not, mark it read (normal font state), go on upwards
				if (this.Equals(info)) { 
					// this can happen only once. A Feed can only have category/root as parents
					
					if (info.UnreadCount < Math.Abs(readCounter))
						readCounter = -info.UnreadCount;

					if (readCounter == 0)
						readCounter = -info.UnreadCount;

					info.UnreadCount += readCounter;
					UpdateReadStatus(info.Parent, readCounter);
					
				} 
				else { // Category/Root mark read

					info.UnreadCount += readCounter;
					UpdateReadStatus(info.Parent, readCounter);
				}
			
			} else {	// mark unread (readCounter > 0)

				// traverse tree: upwards, one by one. On each parent
				// mark it unread (bold font state), go on upwards
				if (info.Node.Nodes.Count == 0  /*info.Type != FeedNodeType.Root && info.Type != FeedNodeType.Category */) { 
					
					// this can happen only once. 
					// A Feed can only have category/root as parents
					// we assume here, that the readCounter is a "reset"
					// of the current node.UnreadCounter to the new value.
					// So at first we have to correct all the parents
					UpdateReadStatus(info.Parent, -info.UnreadCount);
					info.UnreadCount = readCounter;

				} else {
					info.UnreadCount += readCounter;
				}
				
				// now we had set the new value, refresh the parent(s)
				UpdateReadStatus(info.Parent, readCounter);

			}

		}
		
		public void UpdateReadStatus(NodeInfo info, bool anyUnread) {
			if (info == null) return;
			
			if (!anyUnread) {			// mark read
				// traverse tree: upwards, one by one. On every step
				// look for unread childs (go down). If there is one, stop walking up.
				// If not, mark it read (normal font state), go on upwards
				if (this.Equals(info)) { 
					
					// this can happen only once. 
					// A Feed can only have category/root folder as parents
					info.AnyUnread = false;
					UpdateReadStatus(info, 0);	// correct the counters
					
				} 
				else { // Category/Root mark read

					info.AnyUnread = false;
					UpdateReadStatus(info.Parent, false);
				}
			}
			else {	// mark unread 
				// traverse tree: upwards, one by one. On each parent
				// mark it unread (bold font state), go on upwards
				info.AnyUnread = true;
				UpdateReadStatus(info.Parent, true);

			}

		}

	}
}
