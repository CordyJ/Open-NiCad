using System;
using System.Drawing;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// Summary description for UnreadCountDrawFilter.
	/// </summary>
	public class UnreadCountDrawFilter: IUIElementDrawFilter
	{
		public UnreadCountDrawFilter()
		{
			//
			// TODO: Add constructor logic here
			//
		}
		#region IUIElementDrawFilter Members

		public Infragistics.Win.DrawPhase GetPhasesToFilter(ref UIElementDrawParams drawParams) {
			if (drawParams.Element is Infragistics.Win.UltraWinTree.NodeSelectableAreaUIElement)
				return Infragistics.Win.DrawPhase.AfterDrawElement ;
			else
				return Infragistics.Win.DrawPhase.None;
		}

		public bool DrawElement(Infragistics.Win.DrawPhase drawPhase, ref UIElementDrawParams drawParams) {
			Infragistics.Win.UIElement uiElement;
			System.Drawing.Graphics g;
			UltraTreeNode node;

			uiElement = drawParams.Element; 
			Rectangle r = uiElement.Rect;

			node = (UltraTreeNode)uiElement.GetContext(typeof(UltraTreeNode));
			//Determine which drawing phase we are in. 
			if (drawPhase == DrawPhase.AfterDrawElement && node != null) {
				int unread = NodeHelper.GetInfo(node).UnreadCount;
				if (unread > 0) {
					g = drawParams.Graphics;
					g.DrawString("(" + unread.ToString() + ")", node.Control.Font, Brushes.Blue, r.X + r.Width, r.Y+1, StringFormat.GenericDefault);
				}
			}
			return false;
		}

		#endregion
	}
}
