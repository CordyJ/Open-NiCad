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
using RssComponents;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// Summary description for FeedNode.
	/// </summary>
	public class SubscriptionNode: TreeNodeBase
	{
		private static ContextMenu _popup = null;	// share one context menu

		public SubscriptionNode(feedsFeed feed, ContextMenu menu):base(feed.title, FeedNodeType.Feed, true, 4) {
			base.Tag = feed;
			feed.Tag = this;
			base.Key = feed.link;
			_popup = menu; 
		}

		#region Implementation of FeedTreeNodeBase
		public override bool AllowedChild(FeedNodeType nsType) {
		 	// no childs allowed
			return false;
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
