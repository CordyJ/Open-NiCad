using System;
using System.Collections;
using System.Drawing;

using Infragistics.Win;
using Infragistics.Win.UltraWinTree;

namespace RssBandit.WinGui.Forms.ControlHelpers
{
	/// <summary>
	/// DrawFilters forward drawing commands to a chain of object(s) implementing IUIElementDrawFilter.
	/// </summary>
	public class DrawFilters: IUIElementDrawFilter
	{
		private IUIElementDrawFilter[] _drawFilters;

		private DrawFilters() {}
		public DrawFilters(params IUIElementDrawFilter[] drawFilters)
		{
			_drawFilters = drawFilters;
		}

		#region IUIElementDrawFilter Members

		public Infragistics.Win.DrawPhase GetPhasesToFilter(ref UIElementDrawParams drawParams) {
			DrawPhase dp = DrawPhase.None;
			for (int i=0; i < _drawFilters.Length; i++) {
				DrawPhase fdp =_drawFilters[i].GetPhasesToFilter(ref drawParams);
				if (fdp != DrawPhase.None)
					dp |= fdp;
			}
			return dp;
		}

		public bool DrawElement(Infragistics.Win.DrawPhase drawPhase, ref UIElementDrawParams drawParams) {
			
			for (int i=0; i < _drawFilters.Length; i++) {
				DrawPhase fdp = _drawFilters[i].GetPhasesToFilter(ref drawParams);
				if (fdp == DrawPhase.None)
					continue;
				if ((drawPhase & fdp) == drawPhase) {
					bool ret = _drawFilters[i].DrawElement(drawPhase, ref drawParams);
					if (ret)
						return true;	// exclusive drawing phase
				}
			}

			return false;
		}

		#endregion
	}
}
