#region CVS Version Header
/*
 * $Id: NewsItemAdsBlocker.cs,v 1.1 2005/10/21 13:07:42 t_rendelmann Exp $
 * Last modified by $Author: t_rendelmann $
 * Last modified at $Date: 2005/10/21 13:07:42 $
 * $Revision: 1.1 $
 */
#endregion

using NewsComponents;

namespace ChannelServices.AdsBlocker.AddIn
{
	/// <summary>
	/// NewsItemAdsBlocker. 
	/// Sample for an NewsComponents.ChannelService implementation
	/// </summary>
	public class NewsItemAdsBlocker: IChannelProcessor
	{
		public NewsItemAdsBlocker(){}
		
		#region IChannelProcessor Members

		public INewsChannel[] GetChannels() {
			return new INewsChannel[] {new AdsBlockerChannel()};
		}

		#endregion
	}
}
