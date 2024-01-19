#region Copyright PROCOS AG; All rights reserved
// Code copyright by PROCOS AG; FL-9490 Vaduz; All rights reserved
#endregion

using System.Windows.Forms;
using System.Diagnostics;

using Infragistics.Win.UltraWinToolbars;

using PROCOS.ACB.Shared;

namespace PROCOS.ACB.Utils
{
	/// <summary>
	/// Summary description for ToolsHelper.
	/// </summary>
	internal class ToolsHelper
	{
		private UltraToolbarsManager[] tbm;

		public ToolsHelper(UltraToolbarsManager[] tbm)
		{
			this.tbm = tbm;
			FixStateButtonTools();
		}

		public void LockToolbars(bool value) {
			foreach (UltraToolbarsManager m in tbm)
				m.LockToolbars = value;
		}

		public ToolBase this[string key] {
			get {
				foreach (UltraToolbarsManager m in tbm) {
					if (m.Tools.Exists(key) )
						return m.Tools[key];
				}
				return null;
			}
		}

		public void EventsEnable() {
			foreach (UltraToolbarsManager m in tbm)
				m.EventManager.AllEventsEnabled = true;
		}
		public void EventsDisable() {
			foreach (UltraToolbarsManager m in tbm)
				m.EventManager.AllEventsEnabled = false;
		}

		#region SetEnabled

		public void SetEnabled(string key) {
			this.SetEnabled(key.Substring(1), (key[0] == '+' ? true : false));
		}
		public void SetEnabled(string key, bool value) {
			foreach (UltraToolbarsManager m in tbm) {
				if (m.Tools.Exists(key)) {
					ToolBase tool = m.Tools[key];
					tool.SharedProps.Enabled = value;
				}
			}
		}
		public void SetEnabled(params string[] tools) {
			for (int i = 0; i < tools.Length; i++) {
				char onOff = tools[i][0];
				string key = tools[i].Substring(1);	
				foreach (UltraToolbarsManager m in tbm) {
					if (m.Tools.Exists(key))
						m.Tools[key].SharedProps.Enabled = (onOff == '+' ? true : false);
				}
			}
		}
		public bool IsEnabled(string tool) {
			ToolBase t = this[tool];
			if (t != null)
				return t.SharedProps.Enabled;
			Trace.WriteLine("Unkonwn tool key: " + tool);
			return false;	
		}

		#endregion

		#region SetChecked

		public void SetChecked(string key) {
			this.SetChecked(key.Substring(1), (key[0] == '+' ? true : false));
		}
		public void SetChecked(string key, bool value) {
			StateButtonTool tool = this[key] as StateButtonTool;
			Debug.Assert((tool != null), "Tool '" + tool + "' is not a StateButtonTool!" );
			if (tool != null && tool.Checked != value)
				tool.Checked = value;
		}
		public void SetChecked(params string[] tools) {
			for (int i = 0; i < tools.Length; i++) {
				char onOff = tools[i][0];
				string key = tools[i].Substring(1);	
				foreach (UltraToolbarsManager m in tbm) {
					if (m.Tools.Exists(key))
						this.SetChecked(key, (onOff == '+' ? true : false));
				}
			}
		}
		public bool IsChecked(string tool) {
			StateButtonTool sbTool = this[tool] as StateButtonTool;
			Debug.Assert((sbTool != null), "Tool '" + tool + "' is not a StateButtonTool!" );
			if (sbTool != null)
				return sbTool.Checked;
			return false;
		}

		#endregion

		#region SetVisible
		public void SetVisible(string key) {
			this.SetVisible(key.Substring(1), (key[0] == '+' ? true : false));
		}
		public void SetVisible(string key, bool value) {
			foreach (UltraToolbarsManager m in tbm) {
				if (m.Tools.Exists(key)) {
					ToolBase tool = m.Tools[key];
					tool.SharedProps.Visible = value;
				}
			}
		}
		public void SetVisible(params string[] tools) {
			for (int i = 0; i < tools.Length; i++) {
				char onOff = tools[i][0];
				string key = tools[i].Substring(1);	
				foreach (UltraToolbarsManager m in tbm) {
					if (m.Tools.Exists(key))
						this.SetVisible(key, (onOff == '+' ? true : false));
				}
			}
		}
		public bool IsVisible(string tool) {
			ToolBase t = this[tool];
			if (t != null)
				return t.SharedProps.Visible;
			Trace.WriteLine("Unkonwn tool key: " + tool);
			return false;	
		}
		#endregion

		public bool ReCreateMenuDropDownFromCommands(string dropDownKey, MenuCommand[] commands) {
			if (dropDownKey == null)
				return false;

			bool enableDropDown = false;
			
			foreach (UltraToolbarsManager m in tbm) {
				
				PopupMenuTool pm = null;
				ToolBase dropDown = null;

				if (m.Tools.Exists(dropDownKey))
					dropDown = m.Tools[dropDownKey];
			
				if (dropDown == null)
					continue;

				// cleanup
				dropDown.Tag = null;
				if (dropDown is PopupMenuTool) {
					pm = dropDown as PopupMenuTool;
					foreach (ToolBase t in pm.Tools) {
						t.Tag = null;
					}
					pm.Tools.Clear();
				}

				if (commands != null && commands.Length > 0) {

					if (commands[0].Enabled) 
						enableDropDown = true;

					dropDown.SharedProps.AppearancesSmall.Appearance.Image = commands[0].Image;
					dropDown.SharedProps.Tag = commands[0];		// on behalf of cmd

					foreach (MenuCommand cmd in commands) {
						// create child(s)
						string key = "_mc__" + cmd.Key;
						ToolBase newTool = null;

						if (m.Tools.Exists(key))
							newTool = m.Tools[key];
						if (newTool == null) {
							newTool = new ButtonTool(key);		
							m.Tools.Add(newTool); 
						}
					
						if (pm != null && pm.ToolbarsManager == m)
							newTool = pm.Tools.AddTool(key);

						newTool.SharedProps.Category = dropDown.SharedProps.Category;
						newTool.SharedProps.Tag = cmd;		// on behalf of cmd
						newTool.SharedProps.AppearancesSmall.Appearance.Image = cmd.Image;
						newTool.SharedProps.Caption = cmd.Text;
						newTool.SharedProps.Shortcut = cmd.Shortcut;
						newTool.SharedProps.Enabled = cmd.Enabled;
						
						if (newTool.InstanceProps != null)
							newTool.InstanceProps.IsFirstInGroup = cmd.BeginGroup;
						
						// take over first enabled cmd to the top
						if (! enableDropDown && cmd.Enabled) {
							dropDown.SharedProps.AppearancesSmall.Appearance.Image = cmd.Image;
							dropDown.SharedProps.Tag = cmd;		// on behalf of this cmd
							enableDropDown = true;
						}

					}

				} else {
					dropDown.SharedProps.Enabled = false;
				}
			}

			return enableDropDown; 
		}

		public bool ReCreateMenuDropDownFromTextImageItems(string dropDownKey, ITextImageItem[] textImageItems) {
			if (dropDownKey == null)
				return false;

			foreach (UltraToolbarsManager m in tbm) {
				
				PopupMenuTool pm = null;
				ToolBase dropDown = null;

				if (m.Tools.Exists(dropDownKey))
					dropDown = m.Tools[dropDownKey];
			
				if (dropDown == null)
					continue;

				// cleanup
				dropDown.Tag = null;
				if (dropDown is PopupMenuTool) {
					pm = dropDown as PopupMenuTool;
					foreach (ToolBase t in pm.Tools) {
						t.Tag = null;
					}
					pm.Tools.Clear();
				}

				if (textImageItems != null && textImageItems.Length > 0) {

					dropDown.SharedProps.Tag = 0;		// on behalf of first entry

					for (int i= 0; i < textImageItems.Length; i++) {
						ITextImageItem cmd = textImageItems[i];
						// create child(s)
						string key = dropDownKey +"_history_" + i.ToString();
						ToolBase newTool = null;

						if (m.Tools.Exists(key))
							newTool = m.Tools[key];
						if (newTool == null) {
							newTool = new ButtonTool(key);		
							m.Tools.Add(newTool); 
						}
					
						if (pm != null && pm.ToolbarsManager == m)
							pm.Tools.AddTool(key);

						newTool.SharedProps.Category = dropDown.SharedProps.Category;
						newTool.SharedProps.Tag = cmd;		// on behalf of cmd
						newTool.SharedProps.AppearancesSmall.Appearance.Image = cmd.Image;
						newTool.SharedProps.Caption = cmd.Text;
						
					}

				} else {
					dropDown.SharedProps.Enabled = false;
				}
			}

			return true; 
		}

		public void AttachContextMenu(Control c, string menuKey) {
			if (c != null) {
				foreach (UltraToolbarsManager m in tbm) {
					if (m.Tools.Exists(menuKey)) {
						m.SetContextMenuUltra(c, menuKey);
						return;
					}
				}
			}
		}
		public void DetachContextMenu(Control c, string menuKey) {
			if (c != null)
				foreach (UltraToolbarsManager m in tbm) {
					if (m.Tools.Exists(menuKey)) {
						m.SetContextMenuUltra(c, null);
						return;
					}
				}
		}

		private void FixStateButtonTools() {
			foreach (UltraToolbarsManager m in tbm) {
				for (int i = 0; i < m.Tools.Count; i++) {
					StateButtonTool tool = m.Tools[i] as StateButtonTool;
					if (tool != null && tool.MenuDisplayStyle != StateButtonMenuDisplayStyle.DisplayCheckmark)
						tool.MenuDisplayStyle = StateButtonMenuDisplayStyle.DisplayCheckmark;
				}
			}
		}
	}
}
