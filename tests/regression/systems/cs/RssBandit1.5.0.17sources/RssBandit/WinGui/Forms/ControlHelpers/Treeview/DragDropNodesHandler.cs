using System;
using System.Collections;
using System.Drawing;
using System.Windows.Forms;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

namespace RssBandit.WinGui.Forms.ControlHelpers 
{
	/// <summary>
	/// Summary description for DragDropNodesHandler.
	/// </summary>
	public class DragDropNodesHandler
	{
		#region pivars
		private DropHighlightDrawFilter drawFilter;
		private UltraTree tree;
		private ArrayList dragNodes;
		#endregion

		#region ctor's
		private DragDropNodesHandler() {
		}
		public DragDropNodesHandler(UltraTree treeControl, DropHighlightDrawFilter drawFilter):this()
		{
			if (treeControl == null)
				throw new ArgumentNullException("treeControl");
			if (drawFilter == null)
				throw new ArgumentNullException("drawFilter");

			this.drawFilter = drawFilter;
			this.drawFilter.Invalidate += new EventHandler(this.OnDrawFilterInvalidate);
			this.drawFilter.QueryStateAllowedForNode += new RssBandit.WinGui.Forms.ControlHelpers.DropHighlightDrawFilter.QueryStateAllowedForNodeEventHandler(this.OnDrawFilterQueryStateAllowedForNode);

			this.tree = treeControl;
			this.tree.AllowDrop = true;
			this.tree.AllowAutoDragScrolling = true;

			if (this.tree.DrawFilter == null) {
				this.tree.DrawFilter = this.drawFilter;
			}
			this.tree.Override.SelectionType = SelectType.ExtendedAutoDrag;
			this.tree.DragOver += new System.Windows.Forms.DragEventHandler(this.OnDragOver);
			this.tree.SelectionDragStart += new EventHandler(this.OnSelectionDragStart);
			this.tree.DragDrop += new System.Windows.Forms.DragEventHandler(this.OnDragDrop);
			this.tree.QueryContinueDrag += new System.Windows.Forms.QueryContinueDragEventHandler(this.OnQueryContinueDrag);
			this.tree.DragLeave += new EventHandler(this.OnDragLeave);
		}
		#endregion

		#region Events impl.
		
		private void OnSelectionDragStart(object sender, EventArgs e) {
			this.dragNodes = new ArrayList(tree.SelectedNodes);
			tree.DoDragDrop(tree.SelectedNodes, DragDropEffects.Move);
		}

		private void OnDragOver(object sender, System.Windows.Forms.DragEventArgs e) {
			
			//A dummy node variable used to hold nodes for various 
			//things
			UltraTreeNode aNode;
			//The Point that the mouse cursor is on, in Tree coords. 
			//This event passes X and Y in form coords. 
			System.Drawing.Point pointInTree;

			//Get the position of the mouse in the tree, as opposed
			//to form coords
			pointInTree = this.tree.PointToClient(new Point(e.X, e.Y));

			//Get the node the mouse is over.
			aNode = (UltraTreeNode)this.tree.GetNodeFromPoint(pointInTree);

			// dammn! this does not work (no scrolling on drag to topmost/bottmomost node, sorry) :( 
//			int tcsh = this.tree.ClientSize.Height;
//			int scrollThreshold = 25;
//			if (pointInTree.Y + scrollThreshold > tcsh) {
//				Win32.SendMessage(this.tree.Handle, (int)Win32.Message.WM_VSCROLL, 1, 0);
//			} else if (pointInTree.Y < scrollThreshold) {
//				Win32.SendMessage(this.tree.Handle, (int)Win32.Message.WM_VSCROLL, 0, 0);
//			}

			//Make sure the mouse is over a node
			if (aNode == null) {
				//The Mouse is not over a node
				//Do not allow dropping here
				e.Effect = DragDropEffects.None;
				//Erase any DropHighlight
				this.drawFilter.ClearDropHighlight();
				//Exit stage left
				return;
			}

			//Check to see if we are dropping onto a node who//s
			//parent (grandparent, etc) is selected.
			//This is to prevent the user from dropping a node onto
			//one of it//s own descendents. 
			if (this.IsAnyParentSelected(aNode)) {
				//Mouse is over a node whose parent is selected
				//Do not allow the drop
				e.Effect = DragDropEffects.None;
				//Clear the DropHighlight
				this.drawFilter.ClearDropHighlight();
				//Exit stage left
				return;
			}
			
			//If we//ve reached this point, it//s okay to drop on this node
			//Tell the DrawFilter where we are by calling SetDropHighlightNode
			this.drawFilter.SetDropHighlightNode(aNode, pointInTree);
			//Allow Dropping here. 
			e.Effect = DragDropEffects.Move;
		}

		private void OnDragDrop(object sender, System.Windows.Forms.DragEventArgs e) {
			//A dummy node variable used for various things
			UltraTreeNode aNode;
			//The SelectedNodes which will be dropped
			SelectedNodesCollection selectedNodes;
			//The Node to Drop On
			UltraTreeNode dropNode;
			int i;

			//Set the DropNode
			dropNode = this.drawFilter.DropHightLightNode;

			//Get the Data and put it into a SelectedNodes collection
			//These are the nodes that are being dragged and dropped
			selectedNodes = (SelectedNodesCollection)e.Data.GetData(typeof(SelectedNodesCollection));

			//Sort the selected nodes into their visible position. 
			//This is done so that they stay in the same order when
			//they are repositioned. 
			selectedNodes.SortByPosition();

			//Determine where we are dropping based on the current
			//DropLinePosition of the DrawFilter
			switch (this.drawFilter.DropLinePosition) {
				case DropLinePosition.OnNode: { //Drop ON the node
					//Loop through the SelectedNodes and reposition
					//them to the node that was dropped on.
					//Note that the DrawFilter keeps track of what
					//node the mouse is over, so we can just use
					//DropHighLightNode as the drop target. 
					for (i = 0;i<= (selectedNodes.Count - 1);i++) {
						aNode = (UltraTreeNode)selectedNodes[i];						
						aNode.Reposition(dropNode.Nodes);
					}
					break;
				}
				case DropLinePosition.BelowNode: { //Drop Below the node
					for (i = 0;i<= (selectedNodes.Count - 1);i++) {
						aNode = (UltraTreeNode)selectedNodes[i];						
						aNode.Reposition(dropNode, NodePosition.Next);
						//Change the DropNode to the node that was
						//just repositioned so that the next 
						//added node goes below it. 
						dropNode = aNode;
					}	
					break;
				}
				case DropLinePosition.AboveNode: { //New Index should be the same as the Drop
					for (i = 0;i<= (selectedNodes.Count - 1);i++) {
						aNode = (UltraTreeNode)selectedNodes[i];						
						aNode.Reposition(dropNode, NodePosition.Previous);
					}
					break;
				}
			}

			this.CleanupDragStates();
		}

		private void OnQueryContinueDrag(object sender, System.Windows.Forms.QueryContinueDragEventArgs e) {
			//Did the user press escape? 
			if (e.EscapePressed) {
				//User pressed escape; Cancel the Drag
				e.Action = DragAction.Cancel;
				this.CleanupDragStates();
			}
		}

		private void OnDragLeave(object sender, EventArgs e) {
			//When the mouse goes outside the control, clear the 
			//drophighlight. 
			//Since the DropHighlight is cleared when the 
			//mouse is not over a node, anyway, 
			//this is probably not needed
			//But, just in case the user goes from a node directly
			//off the control...
			this.drawFilter.ClearDropHighlight();
		}

		private void OnDrawFilterInvalidate(object sender, EventArgs e) {
			//Any time the drophighlight changes, the control needs 
			//to know that it has to repaint. 
			//It would be more efficient to only invalidate the area
			//that needs it, but this works and is very clean.
			if (this.tree != null && !this.tree.Disposing)
				this.tree.Invalidate();
		}

		private void OnDrawFilterQueryStateAllowedForNode(object sender, DropHighlightDrawFilter.QueryStateAllowedForNodeEventArgs e) {
			//Check to see if this is a allowed child node. 
			if (!this.ChildsAllowedOnNode(e.Node, this.dragNodes)) { 
				//Childs not allowed
				//Allow users to drop above or below this node - but not on
				e.StatesAllowed = DropLinePosition.AboveNode | DropLinePosition.BelowNode;
				
				//Since we can only drop above or below this node, 
				//we don//t want a middle section. So we set the 
				//sensitivity to half the height of the node
				//This means the DrawFilter will respond to the top half
				//bottom half of the node, but not the middle. 
				this.drawFilter.EdgeSensitivity = e.Node.Bounds.Height / 2;
			}
			else {
				if (e.Node.Selected) {
					//Childs allowed
					//Since it is selected, we don't want to allow
					//dropping ON this node. But we can allow the
					//the user to drop above or below it. 
					e.StatesAllowed = DropLinePosition.AboveNode | DropLinePosition.BelowNode;
					this.drawFilter.EdgeSensitivity = e.Node.Bounds.Height / 2;
				}
				else {
					//Childs allowed and is not selected
					//We can allow dropping here above, below, or on this
					//node. Since the StatesAllow defaults to All, we don't 
					//need to change it. 
					//We set the EdgeSensitivity to 1/3 so that the 
					//Drawfilter will respond at the top, bottom, or 
					//middle of the node. 
					this.drawFilter.EdgeSensitivity = e.Node.Bounds.Height / 3;
				}
			}
		}

		#endregion

		#region private methods
		
		/// <summary>
		/// Walks up the parent chain for a node to determine if any
		/// of it's parent nodes are selected
		/// </summary>
		/// <param name="node"></param>
		/// <returns></returns>
		private bool IsAnyParentSelected(UltraTreeNode node) {
			UltraTreeNode parentNode;
			bool returnValue = false;

			parentNode = node.Parent;
			while (parentNode != null) {
				if (parentNode.Selected) {
					returnValue = true;
					break;
				}
				else {
					parentNode = parentNode.Parent;
				}
			} 

			return returnValue;
		}

		private bool ChildsAllowedOnNode(UltraTreeNode parent, ICollection childs) {
			foreach (UltraTreeNode child in childs) {
				if (!NodeHelper.GetInfo(parent).IsChildAllowed(NodeHelper.GetInfo(child).Type))
					return false;
			}
			return true;
		}

		private void CleanupDragStates() {
			this.drawFilter.ClearDropHighlight();
			this.dragNodes.Clear();
			this.dragNodes = null;
		}

		#endregion

	}
}
