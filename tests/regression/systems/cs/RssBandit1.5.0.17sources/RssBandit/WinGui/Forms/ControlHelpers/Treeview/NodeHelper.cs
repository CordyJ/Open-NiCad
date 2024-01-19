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
using System.Globalization;

using TD.SandBar;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

using RssBandit.WinGui.Utility;
using RssBandit.WinGui.Interfaces;
using RssComponents;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// Summary description for NodeHelper.
	/// </summary>
	public sealed class NodeHelper
	{
		private NodeHelper()	{}

		#region hlpers to set/get NodeInfo at TreeNodes

		public static NodeInfo GetInfo(UltraTreeNode node) {
			if (node != null)
				return (NodeInfo)node.Tag;
			return null;
		}
		public static NodeInfo SetFeedNodeInfo(UltraTreeNode node, feedsFeed feed, ContextMenu menu) {
			NodeInfo info = new NodeInfo(node, FeedNodeType.Feed, menu);
			info.Tag = feed;
			feed.Tag = info;
			info.ImageIndex = 4;
			info.Editable = true;
			node.Key = feed.link;
			return info;
		}
		public static NodeInfo SetFeedRootNodeInfo(UltraTreeNode node, ContextMenu menu) {
			NodeInfo info = new NodeInfo(node, FeedNodeType.Root, menu);
			info.ImageIndex = 0;
			info.ExpandedImageIndex = 1;
			info.AllowDragDropChild(FeedNodeType.Category);
			info.AllowDragDropChild(FeedNodeType.Feed);
			node.Key = "SubscriptionsRoot";
			// allow delete on sub-nodes, but not the root node itself:
			node.Override.AllowDelete = DefaultableBoolean.False;
			node.Nodes.Override.AllowDelete = DefaultableBoolean.True;

			return info;
		}
		public static NodeInfo SetFeedCategoryNodeInfo(UltraTreeNode node, ContextMenu menu) {
			NodeInfo info = new NodeInfo(node, FeedNodeType.Category, menu);
			info.ImageIndex = 2;
			info.ExpandedImageIndex = 3;
			info.Editable = true;
			info.AllowDragDropChild(FeedNodeType.Feed);
			// allow delete on sub-nodes and node itself:
			node.Override.AllowDelete = DefaultableBoolean.True;
			node.Nodes.Override.AllowDelete = DefaultableBoolean.True;
			return info;
		}
		public static NodeInfo SetFinderCategoryNodeInfo(UltraTreeNode node, ContextMenu menu) {
			NodeInfo info = new NodeInfo(node, FeedNodeType.FinderCategory, menu);
			info.ImageIndex = 2;
			info.ExpandedImageIndex = 3;
			info.Editable = true;
			info.AllowDragDropChild(FeedNodeType.FinderCategory);
			info.AllowDragDropChild(FeedNodeType.Finder);
			return info;
		}
		#endregion

		/// <summary>
		/// Traverse down the tree on the path defined by 'category' 
		/// starting with 'startNode'.
		/// </summary>
		/// <param name="startNode">UltraTreeNode to start with</param>
		/// <param name="category">A category path, e.g. 'Category1\SubCategory1'.</param>
		/// <param name="menu">Context menu</param>
		/// <returns>The leave category node.</returns>
		/// <remarks>If one category in the path is not found, it will be created.</remarks>
		public static UltraTreeNode CreateSubscriptionCategoryHierarchy(UltraTreeNode startNode, string category, ContextMenu menu)	{
			
			if (StringHelper.EmptyOrNull(category) || startNode == null) return startNode;
			return CreateCategoryHierarchy(startNode, category, FeedNodeType.Category, menu);
		}
		
		/// <summary>
		/// Traverse down the tree on the path defined by 'category' 
		/// starting with 'startNode'.
		/// </summary>
		/// <param name="startNode">UltraTreeNode to start with</param>
		/// <param name="category">A category path, e.g. 'Category1\SubCategory1'.</param>
		/// <param name="menu">Context menu</param>
		/// <returns>The leave category node.</returns>
		/// <remarks>If one category in the path is not found, it will be created.</remarks>
		public static UltraTreeNode CreateFinderCategoryHierarchy(UltraTreeNode startNode, string category, ContextMenu menu)	{

			if (StringHelper.EmptyOrNull(category) || startNode == null) return startNode;
			return CreateCategoryHierarchy(startNode, category, FeedNodeType.FinderCategory, menu);
		}

		private static UltraTreeNode CreateCategoryHierarchy(UltraTreeNode startNode, string category, FeedNodeType type, ContextMenu menu) {
			if (StringHelper.EmptyOrNull(category) || startNode == null) return startNode;

			string[] catHives = category.Split(startNode.Control.PathSeparator.ToCharArray());
			UltraTreeNode n = null;
			bool wasNew = false;

			foreach (string catHive in catHives){

				n = null;

				if (!wasNew) 
					n = FindChild(startNode, catHive, type);

				if (n == null) {
					n = AddNode(startNode, catHive);
					switch (type) {
						case FeedNodeType.Category:					
							SetFeedCategoryNodeInfo(n, menu);
							break;
						case FeedNodeType.FinderCategory:					
							SetFinderCategoryNodeInfo(n, menu);
							break;
						default:
							System.Diagnostics.Debug.Assert(false, "cannot set a CategoryNodeInfo on node type: " + type.ToString());
							break;
					}
					wasNew = true;	// do not call FindChild(), if the parent was yet created
				}

				startNode = n;

			}//foreach
			
			return startNode;
		}

		/// <summary>
		/// Add a new node
		/// </summary>
		/// <param name="parent">UltraTreeNode</param>
		/// <param name="text">to display</param>
		public static UltraTreeNode AddNode(UltraTreeNode parent, string text) {
			return AddNode(parent, text, String.Empty);
		}

		/// <summary>
		/// Add a new node
		/// </summary>
		/// <param name="parent">UltraTreeNode</param>
		/// <param name="text">to display</param>
		public static UltraTreeNode AddNode(UltraTreeNode parent, string text, string key) {
			return parent.Nodes.Add(key, text);
		}

		private static UltraTreeNode FindChild(UltraTreeNode n, string text, FeedNodeType nType) {
			if (n == null || text == null) return null;
			text = text.Trim();
			foreach (UltraTreeNode t in n.Nodes)	{	
				if (GetInfo(t).Type == nType && String.Compare(t.Text, text, false, CultureInfo.CurrentCulture) == 0)	// node names are usually english or client locale
					return t;
			}
			return null;
		}

	}

}
