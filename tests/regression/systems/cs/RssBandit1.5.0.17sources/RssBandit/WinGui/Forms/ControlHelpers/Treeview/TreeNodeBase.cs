using System;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

using RssBandit.WinGui.Interfaces;

namespace RssBandit.WinGui.Forms.ControlHelpers {
	/// <summary>
	/// State of the tree view nodes
	/// </summary>
	public abstract class TreeNodeBase: UltraTreeNode {
		private FeedNodeType	_type;
		private bool					_editable, _anyUnread;
		private int					_unreadCount;
		private int					_highlightCount;
		protected static Font	_normalFont;
		protected static Font	_highlightFont;
		protected int				_levelFix = -1;

		protected TreeNodeBase() {}	// not anymore allowed
		protected TreeNodeBase(string text, FeedNodeType nodeType):this(text, nodeType, false){}
		protected TreeNodeBase(string text, FeedNodeType nodeType, bool editable):base() {
			this.Text = text;
			_unreadCount = 0;
			_highlightCount = 0;
			_type = nodeType;
			_editable = editable;
			_anyUnread = false;
		}
		protected TreeNodeBase(string text, FeedNodeType nodeType, bool editable, int imageIndex):base() {
			this.Text = text;
			_unreadCount = 0;
			_highlightCount = 0;
			this.ImageIndex = imageIndex;
			_type = nodeType;
			_editable = editable;
			_anyUnread = false;
		}
		
		//TODO: implement/override the ISerializable GetObjectData constructor (FxCop warning)

		public virtual int ImageIndex { get { return (int)this.Override.NodeAppearance.Image; } set { this.Override.NodeAppearance.Image = value; } }
		public virtual int SelectedImageIndex { get { return (int)this.Override.ActiveNodeAppearance.Image; } set { this.Override.ActiveNodeAppearance.Image = value; } }
		public virtual int ExpandedImageIndex { get { return (int)this.Override.ExpandedNodeAppearance.Image; } set { this.Override.ExpandedNodeAppearance.Image = value; } }
		public virtual FeedNodeType Type { get { return _type; } set { _type = value; } }
		public virtual bool Editable { get { return _editable; } set { _editable = value; } }
		public virtual Font NormalFont { get { return _normalFont; } set { _normalFont = value; this.NodeFont = value; } }
		public virtual Font HighlightFont { get { return _highlightFont; } set { _highlightFont = value; this.NodeFont = value; } }
		public virtual Font NodeFont {	
			get { return null;	}
			set {
				//TODO
			}
		}

		public virtual Color ForeColor { 
			get { return this.Override.NodeAppearance.ForeColor; } 
			set { if (this.Override.NodeAppearance.ForeColor != value)
					  this.Override.NodeAppearance.ForeColor = value; 
			} 
		}

//		// override some methods so we do not always have to cast explicitly
//		public virtual new FeedTreeNodeBase FirstNode {
//			get {	return (FeedTreeNodeBase)base.FirstNode; }
//		}
//		public virtual new FeedTreeNodeBase NextNode {
//			get {	return (FeedTreeNodeBase)base.NextNode; }
//		}
//		public virtual new FeedTreeNodeBase LastNode {
//			get {	return (FeedTreeNodeBase)base.LastNode; }
//		}
		public virtual new TreeNodeBase Parent {
			get {	return (TreeNodeBase)base.Parent; }
//			set {	base.Parent = value; }
		}
		
//		/// <summary>
//		/// HACK: workaround the "Level not set" bug
//		/// </summary>
//		public virtual new int Level { 
//			get { if (_levelFix < 0) return base.Level; return _levelFix; } 
//			set { _levelFix = value; } 
//		}

		/// <summary>
		/// Now handles the whole visual node text formatting
		/// </summary>
		/// <value>Returns the <see cref="Key"/> of the node. 
		/// Sets the new displayed text and font of a node according to the
		/// unread items counter info.</value>
		public virtual new string Text {
			get { return base.Text; }
			set { 
				string sInfo = String.Empty;
				bool fontChanged = false;
				if (_unreadCount > 0 || _anyUnread) {
					if (this.NodeFont != null) {
						this.NodeFont = null;	// use defaultFont of the tree
						fontChanged = true;
					}
					if (_unreadCount > 0) {
						sInfo =  String.Concat(" (", _unreadCount.ToString() , ")");
					}
				} 
				else if (_highlightCount > 0) {
					if (this.NodeFont != _highlightFont) {
						this.NodeFont = _highlightFont;
						fontChanged = true;
					}
				} else {
					if (this.NodeFont != _normalFont) {
						this.NodeFont = _normalFont;
						fontChanged = true;
					}
				}

				string s;
				if (value == null || value.Trim().Length == 0)
					s = Resource.Manager["RES_GeneralNewItemText"] + sInfo;
				else
					s = value + sInfo;

				if (fontChanged || base.Text != s)
					base.Text = s;
			}
		}

		/// <summary>
		/// Enables to set the editable node text before labelEdit.
		/// </summary>
		public virtual string EditableText {
			get { return this.Text;   }
			set { base.Text = value; }
		}
		
//		public virtual string Key {
//			get { return _key; base.Key }
//			set { 
//				if (value == null || value.Trim().Length == 0)
//					_key = Resource.Manager["RES_GeneralNewItemText"];
//				else
//					_key = value.Trim();
//
//				this.Text = _key;		// refresh visual info
//			}
//		}

		/// <summary>
		/// AnyUnread and UnreadCount are working interconnected:
		/// if you set AnyUnread to true, this will update the visualized info to
		/// use the Unread Font, but no read counter state info. UnreadCount is NOT
		/// modified anyway. Otherwise, if you set AnyUnread to false, it will 
		/// refresh the caption rendering to default.
		/// </summary>
		public virtual bool AnyUnread {
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
		public virtual int UnreadCount {
			get {	return _unreadCount;  }
			set {	
				if (value > 0) {
					_anyUnread = true;
					if (value != _unreadCount) {
						_unreadCount = value; 
						//this.Text = this.Key;		// refresh visual info
					}
				}
				else {
					_anyUnread = false;
					_unreadCount = 0; 
					//this.Text = this.Key;
				}
			}
		}

		public virtual int HighlightCount {
			get {	return _highlightCount;  }
			set {	
				if (value > 0) {
					if (value != _highlightCount) {
						_highlightCount = value; 
						//this.Text = this.Key;		// refresh visual info
					}
				}
				else {
					_highlightCount = 0; 
					//this.Text = this.Key;
				}
			}
		}

//		public virtual new string FullPath {
//			get {
//				TreeNodeBase tn = this.Parent;
//				string sep = this.Control.PathSeparator;
//				StringBuilder sb = new StringBuilder(this.Key);
//				while (tn != null) {
//					sb.Insert(0, tn.Key + sep);
//					tn = tn.Parent;
//				}
//				return sb.ToString(); 
//			}
//		}

		public void UpdateReadStatus(TreeNodeBase thisNode, int readCounter) {
			if (thisNode == null) return;
			
			if (readCounter <= 0) {			// mark read

				// traverse tree: upwards, one by one. On every step
				// look for unread childs (go down). If there is one, stop walking up.
				// If not, mark it read (normal font state), go on upwards
				if (this.Equals(thisNode)) { 
					// this can happen only once. A Feed can only have category/root as parents
					
					if (thisNode.UnreadCount < Math.Abs(readCounter))
						readCounter = -thisNode.UnreadCount;

					if (readCounter == 0)
						readCounter = -thisNode.UnreadCount;

					thisNode.UnreadCount += readCounter;
					UpdateReadStatus(thisNode.Parent, readCounter);
					
				} 
				else { // Category/Root mark read

					thisNode.UnreadCount += readCounter;
					UpdateReadStatus(thisNode.Parent, readCounter);
				}
			
			} else {	// mark unread (readCounter > 0)

				// traverse tree: upwards, one by one. On each parent
				// mark it unread (bold font state), go on upwards
				if (thisNode.Nodes.Count == 0  /*thisNode.Type != FeedNodeType.Root && thisNode.Type != FeedNodeType.Category */) { 
					
					// this can happen only once. 
					// A Feed can only have category/root as parents
					// we assume here, that the readCounter is a "reset"
					// of the current node.UnreadCounter to the new value.
					// So at first we have to correct all the parents
					UpdateReadStatus(thisNode.Parent, -thisNode.UnreadCount);
					thisNode.UnreadCount = readCounter;

				} else {
					thisNode.UnreadCount += readCounter;
				}
				
				// now we had set the new value, refresh the parent(s)
				UpdateReadStatus(thisNode.Parent, readCounter);

			}

		}
		
		public void UpdateReadStatus(TreeNodeBase thisNode, bool anyUnread) {
			if (thisNode == null) return;
			
			if (!anyUnread) {			// mark read
				// traverse tree: upwards, one by one. On every step
				// look for unread childs (go down). If there is one, stop walking up.
				// If not, mark it read (normal font state), go on upwards
				if (this.Equals(thisNode)) { 
					
					// this can happen only once. 
					// A Feed can only have category/root folder as parents
					thisNode.AnyUnread = false;
					UpdateReadStatus(thisNode, 0);	// correct the counters
					
				} 
				else { // Category/Root mark read

					thisNode.AnyUnread = false;
					UpdateReadStatus(thisNode.Parent, false);
				}
			}
			else {	// mark unread 
				// traverse tree: upwards, one by one. On each parent
				// mark it unread (bold font state), go on upwards
				thisNode.AnyUnread = true;
				UpdateReadStatus(thisNode.Parent, true);

			}

		}

		public abstract bool AllowedChild(FeedNodeType nsType);
		public abstract void PopupMenu(System.Drawing.Point screenPos);
		public abstract void UpdateContextMenu();
	}

}
