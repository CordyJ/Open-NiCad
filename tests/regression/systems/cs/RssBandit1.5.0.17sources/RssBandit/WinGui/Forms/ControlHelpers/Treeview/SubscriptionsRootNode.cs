#region CVS Version Header
/*
 * $Id: SubscriptionsRootNode.cs,v 1.38 2004/07/12 11:26:24 t_rendelmann Exp $
 * Last modified by $Author: t_rendelmann $
 * Last modified at $Date: 2004/07/12 11:26:24 $
 * $Revision: 1.38 $
 */
#endregion

using System;
using System.Drawing;
using System.Collections;
using System.Windows.Forms;

using RssBandit.WinGui.Interfaces;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// Summary description for SubscriptionsRootNode.
	/// </summary>
	internal class SubscriptionsRootNode: TreeNodeBase
	{
		private static ContextMenu _popup = null;	// share one context menu
		public SubscriptionsRootNode(string text, ContextMenu menu):base(text,FeedNodeType.Root, false, 0)
		{
			base.Key = "SubscriptionsRootNode";
			base.ExpandedImageIndex = 1;
			base.Editable = false;
			_popup = menu; 
		}
		#region Implementation of FeedTreeNodeBase
		public override bool AllowedChild(FeedNodeType nsType) {
			return (nsType == FeedNodeType.Feed || nsType == FeedNodeType.Category);
		}
		public override void PopupMenu(System.Drawing.Point screenPos) {
			/*
			  if (_popup != null)
				  _popup.TrackPopup(screenPos);
			  */
		}
		public override void UpdateContextMenu() {
			if (base.Control != null)
				base.Control.ContextMenu = _popup;
		}

		#endregion
	}
}
