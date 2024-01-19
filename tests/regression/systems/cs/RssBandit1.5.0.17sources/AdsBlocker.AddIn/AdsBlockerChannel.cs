#region CVS Version Header
/*
 * $Id: AdsBlockerChannel.cs,v 1.4 2007/02/11 15:56:54 carnage4life Exp $
 * Last modified by $Author: carnage4life $
 * Last modified at $Date: 2007/02/11 15:56:54 $
 * $Revision: 1.4 $
 */
#endregion

using System;
using System.Text.RegularExpressions;

using NewsComponents;

namespace ChannelServices.AdsBlocker.AddIn
{
	/// <summary>
	/// AdsBlockerChannel: implements a news channel processor to block ads.
	/// </summary>
	public class AdsBlockerChannel: NewsItemChannelBase
	{
		//TODO: make if configurable:
		private static string AdsReplacementFormat = "<span style='color:gray;font-size:x-small;'>[blocked Ad]<!-- RssBandit.AdsBlocker blocked url: {0} --></span>";
		
		private static Regex RegExFindAHref = new Regex(
			@"<a\s+([^>]*\s*)?href\s*=\s*(?:""(?<1>[/\a-z0-9_][^""]*)""|'(?<1>[/\a-z0-9_][^']*)'|(?<1>[/\a-z0-9_]\S*))(\s[^>]*)?>(?<2>.*?)</a>" + "|" +
			@"<img\s+([^>]*\s*)?src\s*=\s*(?:""(?<1>[/\a-z0-9_][^""]*)""|'(?<1>[/\a-z0-9_][^']*)'|(?<1>[^\s]*))([^>]*)?>", 
			RegexOptions.Singleline | RegexOptions.IgnoreCase | RegexOptions.Compiled);
		private MatchEvaluator matchEvaluator;
		private Uri _baseUrl;

		public AdsBlockerChannel():
			base("http://www.rssbandit.org/displaying-channels/newsitemcontent/adsblocker", 100) 
		{
			this.matchEvaluator = new MatchEvaluator(this.RegexUrlEvaluate);
		}

		public override INewsItem Process(INewsItem item) {
			if (BlackWhiteListFactory.HasBlacklists) {
				_baseUrl = null;
				
				if (item.HasContent) {
					string content = item.Content; 
					string currentBaseUrl = (item.Link == null || item.Link.Length == 0) ? item.FeedLink : item.Link;
					if (currentBaseUrl != null) {
						try {
							_baseUrl = new Uri(currentBaseUrl);
						} catch (UriFormatException) {}
					}
					try{
						// iterate the <a href="badUrl">...</a> matches
						item.SetContent(RegExFindAHref.Replace(content, this.matchEvaluator), item.ContentType);
					}catch(Exception){}
				}
			}
			return base.Process (item);
		}

		private string RegexUrlEvaluate(Match m) {
			Uri inspectUri =  ConvertToAbsoluteUri(m.Groups[1].ToString(), _baseUrl, true);
			if (inspectUri != null) {
				
				//info: m.Groups[2].ToString() would be the link text	
				
				if (BlackWhiteListFactory.HasWhitelists) {
					foreach (IWhitelist processor in BlackWhiteListFactory.Whitelists) {
						Match bm = processor.IsWhitelisted(inspectUri); 
						if (bm != null && bm.Success)	// keep it:
							return m.ToString();
					}
				}
				//if we get called, we have blacklists configured:
				foreach (IBlacklist processor in BlackWhiteListFactory.Blacklists) {
					Match bm = processor.IsBlacklisted(inspectUri); 
					if (bm != null && bm.Success)		// block it:
						return String.Format(AdsReplacementFormat, inspectUri);
				}
			}
			return m.ToString();
		}

		/// <summary>
		/// Converts a relative url to an absolute one. baseUrl is used as the base to fix the other.
		/// </summary>
		/// <param name="url">Url to fix</param>
		/// <param name="baseUri">base Uri to be used</param>
		/// <param name="onlyValid">Provide true, if the url should only be handled if no UriFormatException happens.</param>
		/// <returns>converted Url, or null</returns>
		public static string ConvertToAbsoluteUrl(string url, Uri baseUri, bool onlyValid) {
			
			Uri uri = ConvertToAbsoluteUri(url, baseUri, onlyValid);
			if (uri != null)
				return uri.AbsoluteUri;

			if (!onlyValid)	// return original:
				return url;
			return null;
		}

		/// <summary>
		/// Converts a relative url to an absolute one. baseUrl is used as the base to fix the other.
		/// </summary>
		/// <param name="url">Url to fix</param>
		/// <param name="baseUri">base Uri to be used</param>
		/// <param name="onlyValid">Provide true, if the url should only be handled if no UriFormatException happens.</param>
		/// <returns>converted Url, or null</returns>
		public static Uri ConvertToAbsoluteUri(string url, Uri baseUri, bool onlyValid) {
			
			if (url == null)
				return null;

			try {
				// we must check baseUri, because the Uri constructor
				// will raise a NullRefEx in case it is used internally:
				if (baseUri != null) {
					return new Uri(baseUri,url); 
				} else {
					return new Uri(url); 
				}
			} catch (UriFormatException) {
				if (onlyValid) return null;
			}
			// return original:
			return null;
		}

		

	}
}
