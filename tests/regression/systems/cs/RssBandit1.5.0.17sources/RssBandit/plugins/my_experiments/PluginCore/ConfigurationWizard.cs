using System;
using System.Drawing;
using System.Collections;
using System.ComponentModel;
using System.Windows.Forms;

namespace PluginCore
{
	/// <summary>
	/// Summary description for ConfigurationWizard.
	/// </summary>
	public class ConfigurationWizard : System.Windows.Forms.Form
	{
		private System.Windows.Forms.Panel panelTop;
		private System.Windows.Forms.Label labelTopRight;
		private System.Windows.Forms.Label labelTopInfo;
		private PluginCore.BrowseForFolderPrompt browseForFolderPrompt;
		private PluginCore.LineControl lineControl1;
		private PluginCore.LineControl lineControl2;
		private System.Windows.Forms.Panel dialogStepsContainer;
		private System.Windows.Forms.Button _cancel;
		private System.Windows.Forms.Button _back;
		private System.Windows.Forms.Button _next;
		private System.Windows.Forms.Button _help;
		private System.Windows.Forms.Button _finish;
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.Container components = null;

		public ConfigurationWizard()
		{
			//
			// Required for Windows Form Designer support
			//
			InitializeComponent();

			//
			// TODO: Add any constructor code after InitializeComponent call
			//
		}

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		protected override void Dispose( bool disposing )
		{
			if( disposing )
			{
				if(components != null)
				{
					components.Dispose();
				}
			}
			base.Dispose( disposing );
		}

		#region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{
			System.Resources.ResourceManager resources = new System.Resources.ResourceManager(typeof(ConfigurationWizard));
			this.panelTop = new System.Windows.Forms.Panel();
			this.labelTopInfo = new System.Windows.Forms.Label();
			this.labelTopRight = new System.Windows.Forms.Label();
			this.browseForFolderPrompt = new PluginCore.BrowseForFolderPrompt();
			this.lineControl1 = new PluginCore.LineControl();
			this.lineControl2 = new PluginCore.LineControl();
			this.dialogStepsContainer = new System.Windows.Forms.Panel();
			this._cancel = new System.Windows.Forms.Button();
			this._back = new System.Windows.Forms.Button();
			this._next = new System.Windows.Forms.Button();
			this._help = new System.Windows.Forms.Button();
			this._finish = new System.Windows.Forms.Button();
			this.panelTop.SuspendLayout();
			this.SuspendLayout();
			// 
			// panelTop
			// 
			this.panelTop.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
				| System.Windows.Forms.AnchorStyles.Right)));
			this.panelTop.BackColor = System.Drawing.Color.White;
			this.panelTop.Controls.Add(this.labelTopInfo);
			this.panelTop.Controls.Add(this.labelTopRight);
			this.panelTop.Location = new System.Drawing.Point(0, 0);
			this.panelTop.Name = "panelTop";
			this.panelTop.Size = new System.Drawing.Size(510, 60);
			this.panelTop.TabIndex = 0;
			// 
			// labelTopInfo
			// 
			this.labelTopInfo.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
				| System.Windows.Forms.AnchorStyles.Right)));
			this.labelTopInfo.FlatStyle = System.Windows.Forms.FlatStyle.System;
			this.labelTopInfo.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((System.Byte)(0)));
			this.labelTopInfo.Location = new System.Drawing.Point(20, 10);
			this.labelTopInfo.Name = "labelTopInfo";
			this.labelTopInfo.Size = new System.Drawing.Size(410, 40);
			this.labelTopInfo.TabIndex = 1;
			this.labelTopInfo.Text = "Welcome!";
			// 
			// labelTopRight
			// 
			this.labelTopRight.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
			this.labelTopRight.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
			this.labelTopRight.Image = ((System.Drawing.Image)(resources.GetObject("labelTopRight.Image")));
			this.labelTopRight.Location = new System.Drawing.Point(446, 7);
			this.labelTopRight.Name = "labelTopRight";
			this.labelTopRight.Size = new System.Drawing.Size(45, 45);
			this.labelTopRight.TabIndex = 0;
			// 
			// browseForFolderPrompt
			// 
			this.browseForFolderPrompt.Description = "";
			this.browseForFolderPrompt.StartLocation = PluginCore.FolderBrowserFolder.Desktop;
			// 
			// lineControl1
			// 
			this.lineControl1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
				| System.Windows.Forms.AnchorStyles.Right)));
			this.lineControl1.Beveled = true;
			this.lineControl1.Highlight = System.Drawing.SystemColors.ControlLightLight;
			this.lineControl1.Location = new System.Drawing.Point(0, 57);
			this.lineControl1.Name = "lineControl1";
			this.lineControl1.Orientation = System.Windows.Forms.Orientation.Horizontal;
			this.lineControl1.Shadow = System.Drawing.SystemColors.ControlDark;
			this.lineControl1.Size = new System.Drawing.Size(510, 5);
			this.lineControl1.TabIndex = 1;
			this.lineControl1.TabStop = false;
			this.lineControl1.Text = "lineControl1";
			// 
			// lineControl2
			// 
			this.lineControl2.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
				| System.Windows.Forms.AnchorStyles.Right)));
			this.lineControl2.Beveled = true;
			this.lineControl2.Highlight = System.Drawing.SystemColors.ControlLightLight;
			this.lineControl2.Location = new System.Drawing.Point(-7, 310);
			this.lineControl2.Name = "lineControl2";
			this.lineControl2.Orientation = System.Windows.Forms.Orientation.Horizontal;
			this.lineControl2.Shadow = System.Drawing.SystemColors.ControlDark;
			this.lineControl2.Size = new System.Drawing.Size(510, 5);
			this.lineControl2.TabIndex = 2;
			this.lineControl2.TabStop = false;
			this.lineControl2.Text = "lineControl2";
			// 
			// dialogStepsContainer
			// 
			this.dialogStepsContainer.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
				| System.Windows.Forms.AnchorStyles.Left) 
				| System.Windows.Forms.AnchorStyles.Right)));
			this.dialogStepsContainer.Location = new System.Drawing.Point(0, 65);
			this.dialogStepsContainer.Name = "dialogStepsContainer";
			this.dialogStepsContainer.Size = new System.Drawing.Size(500, 240);
			this.dialogStepsContainer.TabIndex = 3;
			// 
			// _cancel
			// 
			this._cancel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
			this._cancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
			this._cancel.FlatStyle = System.Windows.Forms.FlatStyle.System;
			this._cancel.Location = new System.Drawing.Point(135, 325);
			this._cancel.Name = "_cancel";
			this._cancel.Size = new System.Drawing.Size(80, 24);
			this._cancel.TabIndex = 4;
			this._cancel.Text = "&Cancel";
			// 
			// _back
			// 
			this._back.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
			this._back.FlatStyle = System.Windows.Forms.FlatStyle.System;
			this._back.Location = new System.Drawing.Point(230, 325);
			this._back.Name = "_back";
			this._back.Size = new System.Drawing.Size(80, 24);
			this._back.TabIndex = 5;
			this._back.Text = "<< &Back";
			// 
			// _next
			// 
			this._next.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
			this._next.FlatStyle = System.Windows.Forms.FlatStyle.System;
			this._next.Location = new System.Drawing.Point(315, 325);
			this._next.Name = "_next";
			this._next.Size = new System.Drawing.Size(80, 24);
			this._next.TabIndex = 6;
			this._next.Text = "&Next >>";
			// 
			// _help
			// 
			this._help.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
			this._help.FlatStyle = System.Windows.Forms.FlatStyle.System;
			this._help.Location = new System.Drawing.Point(10, 325);
			this._help.Name = "_help";
			this._help.Size = new System.Drawing.Size(80, 24);
			this._help.TabIndex = 7;
			this._help.Text = "&Help";
			// 
			// _finish
			// 
			this._finish.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
			this._finish.DialogResult = System.Windows.Forms.DialogResult.Cancel;
			this._finish.FlatStyle = System.Windows.Forms.FlatStyle.System;
			this._finish.Location = new System.Drawing.Point(410, 325);
			this._finish.Name = "_finish";
			this._finish.Size = new System.Drawing.Size(80, 24);
			this._finish.TabIndex = 8;
			this._finish.Text = "Finish";
			// 
			// ConfigurationWizard
			// 
			this.AcceptButton = this._next;
			this.AutoScaleBaseSize = new System.Drawing.Size(5, 14);
			this.CancelButton = this._cancel;
			this.ClientSize = new System.Drawing.Size(497, 361);
			this.Controls.Add(this._finish);
			this.Controls.Add(this._cancel);
			this.Controls.Add(this._back);
			this.Controls.Add(this._next);
			this.Controls.Add(this._help);
			this.Controls.Add(this.dialogStepsContainer);
			this.Controls.Add(this.lineControl2);
			this.Controls.Add(this.lineControl1);
			this.Controls.Add(this.panelTop);
			this.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((System.Byte)(0)));
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.MinimumSize = new System.Drawing.Size(505, 395);
			this.Name = "ConfigurationWizard";
			this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Hide;
			this.Text = "Plugin Configuration Wizard";
			this.panelTop.ResumeLayout(false);
			this.ResumeLayout(false);

		}
		#endregion
	}
}
