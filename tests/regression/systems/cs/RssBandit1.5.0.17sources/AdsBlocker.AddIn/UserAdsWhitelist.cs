using System;
using System.Text.RegularExpressions;

namespace ChannelServices.AdsBlocker.AddIn
{
	/// <summary>
	/// Summary description for UserAdsWhitelist.
	/// </summary>
	public class UserAdsWhitelist: IWhitelist
	{
		private static bool loaded = false;
		private static Regex whiteListRegex = null;
		private static string whitelist = null;
		private static object whiteListLock = new object();

		public UserAdsWhitelist(){}

		#region IWhitelist Members

		public void Initialize(string newWhiteList) {
			lock(whiteListLock) {
				if (whitelist == null || whitelist != newWhiteList) {
					if (newWhiteList != null && newWhiteList.Length > 0) {
						whitelist = newWhiteList;
						whitelist = whitelist.Replace(";","|");
						whiteListRegex = new Regex(whitelist,RegexOptions.IgnoreCase|RegexOptions.Singleline);
					} else {
						throw new ArgumentNullException("blacklist");
					}
				}
			}

			loaded = true;
		}

		public ChannelServices.AdsBlocker.AddIn.ListUpdateState UpdateWhitelist() {
			return ListUpdateState.None;
		}

		public System.Text.RegularExpressions.Match IsWhitelisted(Uri uri) {
			if (!loaded || uri == null) 
				return null;
			
			try {
				Match match = null;
				// we want to remove the Query from the url as it 
				// may contain keywords that easily match the white list. 
				// However, we CHECK against the stripped uri but log the COMPLETE referral!
				string strippedUri = uri.Scheme + "://" + uri.Authority + uri.AbsolutePath;

				lock (whiteListLock) {
					match = whiteListRegex.Match(strippedUri);
				}

				return match;
			}
			catch (Exception ex) {
				throw new Exception(String.Format("An error occured trying to determine if {0} is whitelisted", uri), ex.InnerException);
			}
		}

		#endregion
	}
}
