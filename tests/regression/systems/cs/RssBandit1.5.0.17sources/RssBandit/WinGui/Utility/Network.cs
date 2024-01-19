using System;
using System.Collections.Specialized;
using System.Runtime.InteropServices;
using System.Threading;
using RssBandit.Common.Logging;

namespace RssBandit.Network
{
	#region new untested stuff

	#region NetworkAvailabilityEventArgs
	
	internal delegate void NetworkAvailabilityChangedEventHandler(object sender, NetworkAvailabilityEventArgs e);
	internal delegate void NetworkAddressChangedEventHandler(object sender, EventArgs e);

	internal class NetworkAvailabilityEventArgs : EventArgs {
		/// <summary>
		/// Initializes a new instance of the <see cref="NetworkAvailabilityEventArgs"/> class.
		/// </summary>
		/// <param name="isAvailable">if set to <c>true</c> [is available].</param>
		internal NetworkAvailabilityEventArgs(bool isAvailable) {
			IsAvailable = isAvailable;
		}

		/// <summary>
		/// Gets true if the network is available
		/// </summary>
		public readonly bool IsAvailable; 
	}

	#endregion

	internal class NetworkChange {

		[DllImport("wininet.dll", SetLastError=true)]
		private extern static bool InternetGetConnectedState(out int flags, int reserved);

		internal class AvailabilityChangeListener {
			// Methods
			static AvailabilityChangeListener() {
				NetworkChange.AvailabilityChangeListener.syncObject = new object();
				NetworkChange.AvailabilityChangeListener.s_availabilityCallerArray = null;
				//NetworkChange.AvailabilityChangeListener.addressChange = null;
				NetworkChange.AvailabilityChangeListener.isAvailable = false;
				//NetworkChange.AvailabilityChangeListener.s_RunHandlerCallback = new ContextCallback(NetworkChange.AvailabilityChangeListener.RunHandlerCallback);
			}

			private static void ChangedAddress(object sender, EventArgs eventArgs) {}
			private static void RunHandlerCallback(object state) {}
				
			internal static void Start(NetworkAvailabilityChangedEventHandler caller) {
				lock (NetworkChange.AvailabilityChangeListener.syncObject) {
					if (NetworkChange.AvailabilityChangeListener.s_availabilityCallerArray == null) {
						NetworkChange.AvailabilityChangeListener.s_availabilityCallerArray = new ListDictionary();
						NetworkChange.AvailabilityChangeListener.addressChange = new NetworkAddressChangedEventHandler(NetworkChange.AvailabilityChangeListener.ChangedAddress);
					}
					if (NetworkChange.AvailabilityChangeListener.s_availabilityCallerArray.Count == 0) {
						NetworkChange.AvailabilityChangeListener.isAvailable = NetworkInterface.GetIsNetworkAvailable();
						NetworkChange.AddressChangeListener.UnsafeStart(NetworkChange.AvailabilityChangeListener.addressChange);
					}
					if ((caller != null) && !NetworkChange.AvailabilityChangeListener.s_availabilityCallerArray.Contains(caller)) {
						NetworkChange.AvailabilityChangeListener.s_availabilityCallerArray.Add(caller, null);
					}
				}
	
			}

			internal static void Stop(NetworkAvailabilityChangedEventHandler caller) {}

			// Fields
			private static NetworkAddressChangedEventHandler addressChange;
			private static bool isAvailable;
			private static ListDictionary s_availabilityCallerArray;
			//private static System.Threading.ContextCallback s_RunHandlerCallback;
			private static object syncObject;
		}

			
		internal class AddressChangeListener {
			// Methods
			static AddressChangeListener() {}
			private static void AddressChangedCallback(object stateObject, bool signaled) {}
			private static void RunHandlerCallback(object state){}
			internal static void Start(NetworkAddressChangedEventHandler caller){}
			private static void StartHelper(NetworkAddressChangedEventHandler caller, bool captureContext, StartIPOptions startIPOptions) {}
			internal static void Stop(object caller){}
			internal static void UnsafeStart(NetworkAddressChangedEventHandler caller){}

			// Fields
			private static ListDictionary s_callerArray;
			//private static SafeCloseSocketAndEvent s_ipv4Socket;
			private static WaitHandle s_ipv4WaitHandle;
			//private static SafeCloseSocketAndEvent s_ipv6Socket;
			private static WaitHandle s_ipv6WaitHandle;
			private static bool s_isListening;
			private static bool s_isPending;
			private static RegisteredWaitHandle s_registeredWait;
			//private static ContextCallback s_runHandlerCallback;
		}


		/// <summary>
		/// Internal get is network available (CLR2 similar implementation).
		/// </summary>
		/// <returns></returns>
		private bool CLR2InternalGetIsNetworkAvailable() {
			if (Environment.OSVersion.Platform == PlatformID.Win32NT) {
				//				NetworkInterface[] interfaceArray1 = SystemNetworkInterface.GetNetworkInterfaces();
				//				foreach (NetworkInterface interface1 in interfaceArray1) {
				//					if (((interface1.OperationalStatus == OperationalStatus.Up) && (interface1.NetworkInterfaceType != NetworkInterfaceType.Tunnel)) && (interface1.NetworkInterfaceType != NetworkInterfaceType.Loopback)) {
				//						return true;
				//					}
				//				}
				//				return false;
			}
			
			int flags = 0;
			try {
				return InternetGetConnectedState(out flags, 0);
			} catch (Exception ex) {
				Log.Error("InternetGetConnectedState() API call failed with error: " + Marshal.GetLastWin32Error(), ex);
			}
			return false;
		}
		
		private void QueryNetworkAdapterConfiguration () {
			// get information about network adapters without also retrieving 
			// information about things like RAS and VPN connections:
			/*
				 * strComputer = "."
					Set objWMIService = GetObject( _
						"winmgmts:\\" & strComputer & "\root\cimv2")
					Set IPConfigSet = objWMIService.ExecQuery _
						("Select IPAddress from Win32_NetworkAdapterConfiguration" _
							& " where IPEnabled=TRUE")
 
					For Each IPConfig in IPConfigSet
						If Not IsNull(IPConfig.IPAddress) Then 
							For i=LBound(IPConfig.IPAddress) _
								to UBound(IPConfig.IPAddress)
								WScript.Echo IPConfig.IPAddress(i)
							Next
						End If
					Next

				 */
		}
		/// <summary>
		/// Enumerates network adapters installed on the computer.
		/// </summary>
		private void EnumerateNetworkAdapters() {
			//			// Information about network adapters can be found
			//			// by querying the WMI class Win32_NetworkAdapter,
			//			// NetConnectionStatus = 2 filters the ones that are not connected.
			//			// WMI related classes are located in assembly System.Management.dll
			//			ManagementObjectSearcher searcher = new 
			//				ManagementObjectSearcher("SELECT * FROM Win32_NetworkAdapter" + 
			//				" WHERE NetConnectionStatus=2");
			//
			//			ManagementObjectCollection adapterObjects = searcher.Get();
			//
			//			foreach (ManagementObject adapterObject in adapterObjects) {
			//				string name    =    adapterObject["Name"];
			//
			//				this.adapters.Add(adapter); // Add it to ArrayList adapter
			//			}
		}
	}
	public abstract class NetworkInterface {
		// Methods
		protected NetworkInterface() {}
		public static NetworkInterface[] GetAllNetworkInterfaces() {
			return new NetworkInterface[]{};
		}
		//public abstract IPInterfaceProperties GetIPProperties();
		//public abstract IPv4InterfaceStatistics GetIPv4Statistics();
		public static bool GetIsNetworkAvailable() {
			return true;
		}

		//public abstract PhysicalAddress GetPhysicalAddress();
		//public abstract bool Supports(NetworkInterfaceComponent networkInterfaceComponent);

		// Properties
		public abstract string Description { get; }
		public abstract string Id { get; }
		public abstract bool IsReceiveOnly { get; }
		public static int LoopbackInterfaceIndex { get { return 0; } }
		public abstract string Name { get; }
		public abstract NetworkInterfaceType NetworkInterfaceType { get; }
		public abstract OperationalStatus OperationalStatus { get; }
		public abstract long Speed { get; }
		public abstract bool SupportsMulticast { get; }
	}

	public enum NetworkInterfaceType {
		// Fields
		AsymmetricDsl = 0x5e,
		Atm = 0x25,
		BasicIsdn = 20,
		Ethernet = 6,
		Ethernet3Megabit = 0x1a,
		FastEthernetFx = 0x45,
		FastEthernetT = 0x3e,
		Fddi = 15,
		GenericModem = 0x30,
		GigabitEthernet = 0x75,
		HighPerformanceSerialBus = 0x90,
		IPOverAtm = 0x72,
		Isdn = 0x3f,
		Loopback = 0x18,
		MultiRateSymmetricDsl = 0x8f,
		Ppp = 0x17,
		PrimaryIsdn = 0x15,
		RateAdaptDsl = 0x5f,
		Slip = 0x1c,
		SymmetricDsl = 0x60,
		TokenRing = 9,
		Tunnel = 0x83,
		Unknown = 1,
		VeryHighSpeedDsl = 0x61,
		Wireless80211 = 0x47
	}
		
	public enum OperationalStatus {
		// Fields
		Dormant = 5,
		Down = 2,
		LowerLayerDown = 7,
		NotPresent = 6,
		Testing = 3,
		Unknown = 4,
		Up = 1
	}

	[Flags]
	internal enum StartIPOptions {
		None,
		StartIPv4,
		StartIPv6,
		Both
	}


	#endregion

}
