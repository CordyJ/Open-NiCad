#region CVS Version Header
/*
 * $Id: AsyncWebRequest.cs,v 1.22 2005/06/30 18:59:00 t_rendelmann Exp $
 * Last modified by $Author: t_rendelmann $
 * Last modified at $Date: 2005/06/30 18:59:00 $
 * $Revision: 1.22 $
 */
#endregion

using System;
using System.Collections;
using System.IO;
using System.Xml;
using NewsComponents;
using NewsComponents.Feed;
using NewsComponents.Net;
using NewsComponents.Utils;
using NUnit.Framework;

namespace RssBandit.UnitTests
{
#if TESTBGDOWNLOADER
	/// <summary>
	/// Background Downloader Tests.
	/// </summary>
	[TestFixture]
	public class BGDownloaderTests: CassiniHelperTestFixture
	{

		private bool eventsConnected = false;
		private BackgroundDownloadManager bgm;
		
		/// <summary>
		/// Tests download of enclosures
		/// </summary>
		[Test]
		public void DownloadEnclosures()
		{
			NewsHandler handler = new NewsHandler(APP_NAME);
			
			feedsFeed f = new feedsFeed();
			//f.link = "http://www.byte.org/blog/NotRandomBytes/index.xml"; // multiple enclosures at an item
			f.link = "http://feeds.feedburner.com/ericriceshow";	// one enclosure
			//IFeedDetails fd = handler.GetFeedInfo(f.link);
			f.downloadenclosures = true;
			f.downloadenclosuresSpecified = true;
			f.enclosurefolder = Path.Combine(Path.GetTempPath(), APP_NAME) ;
			handler.FeedsTable.Add(f.link, f);

			ArrayList items = handler.GetItemsForFeed(f);
			Assert.IsNotNull(items, "GetItemsForFeed() failed");

			bgm = new BackgroundDownloadManager(APP_NAME, new TestInfoProvider(f, items) /* handler */);

			AttachEvents();
			bgm.Download( CreateFrom(f, items), TimeSpan.MaxValue);
			DetachEvents();
		}

		private DownloadItem[] CreateFrom(feedsFeed f, IList items) {
			ArrayList dlItems = new ArrayList();
			foreach (NewsItem item in items) {
				XmlElement[] xArray = RssHelper.GetOptionalElements(item.OptionalElements, "enclosure", "");
				if (xArray != null) {
					DownloadItem d = new DownloadItem(f.link, item.Link);
					foreach (XmlElement x in xArray) {
						string url = x.Attributes.GetNamedItem("url").Value;
						MimeType mime = new MimeType(x.Attributes.GetNamedItem("type").Value);
						long size = Int64.Parse(x.Attributes.GetNamedItem("length").Value	);
						d.Files.Add(new DownloadFile(url, mime, size));
					}
					if (d.Files.Count > 0)
						dlItems.Add(d);
				}
			}
			return (DownloadItem[])dlItems.ToArray( typeof(DownloadItem) );
		}

		private void AttachEvents() {
			if (!eventsConnected) {
				bgm.DownloadCompleted += new DownloadCompletedEventHandler(this.OnDownloadCompleted);
				bgm.DownloadError += new DownloadErrorEventHandler(this.OnDownloadError);
				bgm.DownloadProgress += new DownloadProgressEventHandler(this.OnDownloadProgress);
				bgm.DownloadStarted += new DownloadStartedEventHandler(this.OnDownloadStarted);
				eventsConnected = true;
			}
		}

		private void DetachEvents() {
			if (eventsConnected) {
				bgm.DownloadCompleted -= new DownloadCompletedEventHandler(this.OnDownloadCompleted);
				bgm.DownloadError -= new DownloadErrorEventHandler(this.OnDownloadError);
				bgm.DownloadProgress -= new DownloadProgressEventHandler(this.OnDownloadProgress);
				bgm.DownloadStarted -= new DownloadStartedEventHandler(this.OnDownloadStarted);
				eventsConnected = false;
			}

		}

		private void OnDownloadCompleted(object sender, DownloadItemEventArgs e) {
			Console.WriteLine("OnDownloadCompleted(): {0}" , e.DownloadItem.OwnerId);
		}

		private void OnDownloadError(object sender, DownloadItemErrorEventArgs e) {
			Console.WriteLine("OnDownloadError(): at {0} - {1}" , e.DownloadItem.OwnerId, e.Exception.Message);
		}

		private void OnDownloadProgress(object sender, DownloadProgressEventArgs e) {
			Console.WriteLine("OnDownloadProgress(): {0} {1}/{2} bytes transferred" , e.DownloadItem.OwnerId, e.BytesTransferred, e.BytesTotal);
		}

		private void OnDownloadStarted(object sender, DownloadStartedEventArgs e) {
			Console.WriteLine("OnDownloadStarted(): {0}" , e.DownloadItem.OwnerId);
		}

		/// <summary>
		/// Just mimics the feedHandler, and provide infos about the feedsFeed
		/// to test here only (not about all feeds). So we need the feedsFeed and it's
		/// items to simulate it completely.
		/// </summary>
		class TestInfoProvider: IDownloadInfoProvider {
			private feedsFeed feed;
			private IList items;

			public TestInfoProvider(feedsFeed f, IList items) {
				this.feed = f;
				this.items = items;
			}

			#region IDownloadInfoProvider Members

			public IDownloadInfo GetDownloadInfo(string downloadOwnerId) {
				// usually we retrieve the feed from feedsTable here
				if (feed.link == downloadOwnerId) {
					return new SimpleDownloadInfo();
				}
				return null;
			}

			#endregion

		}

		class SimpleDownloadInfo: IDownloadInfo {

			#region IDownloadInfo Members

			public DownloadFile[] Files {
				get {
					// TODO:  Add TestDownloadInfo.Files getter implementation
					// if no files are specified at creation time
					// a.g. like the CreateFrom() method from test class above
					return new DownloadFile[]{};
				}
			}

			public System.Net.IWebProxy Proxy {
				get {
					// no webproxy
					return null;
				}
			}

			public string Description {
				get {
					return "Download MP3 from url";
				}
			}

			/// <summary>
			/// Description of one DownloadItem, should describe the 
			/// download owner item.
			/// </summary>
			public string ItemDescription(string itemOwnerId) {
				throw new NotImplementedException(); 
			}

			public System.Net.ICredentials Credentials {
				get {
					// no credentials
					return null;
				}
			}

			public string TargetFolder {
				get {
					return "";
				}
			}

			#endregion
		}


	}
#endif
}
