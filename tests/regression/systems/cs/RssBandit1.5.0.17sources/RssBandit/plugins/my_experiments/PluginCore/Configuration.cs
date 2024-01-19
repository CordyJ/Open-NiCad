using System;
using Microsoft.Win32;
using System.IO;

namespace PluginCore
{
	/// <summary>
	/// Configuration. Supports plugin base configuration facilities
	/// </summary>
	public class Configuration
	{
		protected Configuration() {}
		
		/// <summary>
		/// Get/Set the overall plugin base path to store/retrive plugin sattelite files.
		/// </summary>
		public static string PluginBasePath {
			get { return Registry.ConfigBasePath; }
			set { Registry.ConfigBasePath = value; }
		}
		
		/// <summary>
		/// Returns true, if the PluginCore.Configuration is valid: 
		/// PluginBasePath contains a non-empty value.
		/// </summary>
		public static bool IsValid {
			get { return (PluginBasePath.Length > 0); }
		}

		/// <summary>
		/// Returns a plugin/user specific configuration value.
		/// </summary>
		/// <param name="pluginType">The plugin class type</param>
		/// <param name="key">Key (string) for the value to retrive</param>
		/// <returns>Value as String</returns>
		/// <remarks>
		/// Values are currently retrived from the Windows Registry Hive:
		/// <c>HKEY_CURRENT_USER\Software\IBlogExtension.Plugins\&lt;pluginType.FullName&gt;</c>
		/// </remarks>
		public static string GetPluginSetting(Type pluginType, string key) {
			return Registry.GetPluginSetting(pluginType.FullName, key);
		}

		/// <summary>
		/// Set a plugin/user specific configuration value.
		/// </summary>
		/// <param name="pluginType">The plugin class type</param>
		/// <param name="key">Key (string) for the value to store</param>
		/// <param name="settingsValue">value to store</param>
		/// <remarks>If <c>settingsValue</c> is null or empty, 
		/// the key is removed from the storage system.
		/// Values are currently saved to the Windows Registry Hive:
		/// <c>HKEY_CURRENT_USER\Software\IBlogExtension.Plugins\&lt;pluginType.FullName&gt;</c>
		/// </remarks>
		public static void SetPluginSetting(Type pluginType, string key, string settingsValue) {
			Registry.SetPluginSetting(pluginType.FullName, key, settingsValue);
		}

	}

	/// <summary>
	/// Wrap the windows registry access needed for Plugin Configuration Settings
	/// </summary>
	internal class Registry {
			
		private static string ConfigSettings = @"Software\IBlogExtension.Plugins";

		/// <summary>
		/// Set/Get the path to plugin base configuration file directory.
		/// </summary>
		public static string ConfigBasePath {
			get {
				try {
					string retval = String.Empty;
					RegistryKey key = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(ConfigSettings, false);
					string val = ((key == null) ? null : (key.GetValue("ConfigBasePath") as string));
					if (val != null && val.Trim().Length > 0) {
						retval = Environment.ExpandEnvironmentVariables(val.Trim());
					}
					return retval;
				} catch (Exception ex) {
					System.Diagnostics.Trace.WriteLine("Registry:ConfigBasePath (get) cause exception: "+ex.Message);
					return String.Empty;
				}
			}
			set {
				try {
					string newval = value;
					RegistryKey keySettings = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(ConfigSettings, true);
					if (keySettings == null) {
						keySettings = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(ConfigSettings);
					}
					if (newval != null && newval.Length > 0) {
						keySettings.SetValue("ConfigBasePath", newval);
					} else {
						keySettings.DeleteValue("ConfigBasePath");
					}
				} catch (Exception ex) {
					System.Diagnostics.Trace.WriteLine("Registry:ConfigBasePath (set) cause exception: "+ex.Message);
				}
			}
		}
		/// <summary>
		/// Get a Plugin specific value. 
		/// </summary>
		/// <param name="key"></param>
		/// <param name="plugin"></param>
		public static string GetPluginSetting(string plugin, string key) {
			try {
				string retval = String.Empty;
				if (plugin == null || key == null || plugin.Length == 0 || key.Length == 0)
					return retval;
				
				RegistryKey rKey = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(String.Format(@"{0}\{1}", ConfigSettings, plugin), false);
				string val = ((key == null) ? null : (rKey.GetValue(key) as string));
				if (val != null && val.Trim().Length > 0) {
					retval = Environment.ExpandEnvironmentVariables(val.Trim());
				}
				return retval;
			} catch (Exception ex) {
				System.Diagnostics.Trace.WriteLine("Registry:GetPluginSetting('"+plugin+"','"+key+"') cause exception: "+ex.Message);
				return String.Empty;
			}
		}

		/// <summary>
		/// Set a Plugin specific value. 
		/// </summary>
		/// <param name="key"></param>
		/// <param name="plugin"></param>
		/// <param name="settingsValue"></param>
		public static void SetPluginSetting(string plugin, string key, string settingsValue) {
			try {
				if (plugin == null || key == null || plugin.Length == 0 || key.Length == 0)
					return;
				string newval = settingsValue;
				RegistryKey keySettings = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(String.Format(@"{0}\{1}", ConfigSettings, plugin), true);
				if (keySettings == null) {
					keySettings = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(String.Format(@"{0}\{1}", ConfigSettings, plugin));
				}
				if (newval != null && newval.Length > 0) {
					keySettings.SetValue(key, newval);
				} else {
					keySettings.DeleteValue(key);
				}
			} catch (Exception ex) {
				System.Diagnostics.Trace.WriteLine("Registry:SetPluginSetting('"+plugin+"','"+key+"') cause exception: "+ex.Message);
			}
		}
			

		private Registry(){}
	}

}
