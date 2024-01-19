#region CVS Version Header
/*
 * $Id: WinGUIWidgetHelpers.cs,v 1.38 2004/07/12 11:26:24 t_rendelmann Exp $
 * Last modified by $Author: t_rendelmann $
 * Last modified at $Date: 2004/07/12 11:26:24 $
 * $Revision: 1.38 $
 */
#endregion

using System;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

using RssBandit.WinGui.Interfaces;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// Summary description for SubscriptionCategory.
	/// </summary>
	public class SubscriptionCategoryNode: TreeNodeBase
	{
		private static ContextMenu _popup = null;	// share one context menu

		public SubscriptionCategoryNode(string text):base(text,FeedNodeType.Category, true, 2) {
			base.ExpandedImageIndex = 3;
		}
		public SubscriptionCategoryNode(string text, ContextMenu menu):this(text) {
			_popup = menu; 
		}


		#region Implementation of FeedTreeNodeBase
		public override bool AllowedChild(FeedNodeType nsType) {
			return (nsType == FeedNodeType.Category || nsType == FeedNodeType.Feed);
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
