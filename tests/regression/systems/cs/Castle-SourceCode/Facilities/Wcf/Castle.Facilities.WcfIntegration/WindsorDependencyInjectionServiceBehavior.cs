// Copyright 2004-2007 Castle Project - http://www.castleproject.org/
// 
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
//     http://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using Castle.MicroKernel;

namespace Castle.Facilities.WcfIntegration
{
	using System;
	using System.Collections.Generic;
	using System.Collections.ObjectModel;
	using System.ServiceModel;
	using System.ServiceModel.Channels;
	using System.ServiceModel.Description;
	using System.ServiceModel.Dispatcher;

	public class WindsorDependencyInjectionServiceBehavior : IServiceBehavior
	{
		private readonly IKernel kernel;

		public WindsorDependencyInjectionServiceBehavior(IKernel kernel)
		{
			this.kernel = kernel;
		}

		#region IServiceBehavior Members

		///<summary>
		///Provides the ability to inspect the service host and the service description to confirm that the service can run successfully.
		///</summary>
		///<param name="serviceHostBase">The service host that is currently being constructed.</param>
		///<param name="serviceDescription">The service description.</param>
		public void Validate(ServiceDescription serviceDescription, ServiceHostBase serviceHostBase)
		{
		}

		///<summary>
		///Provides the ability to pass custom data to binding elements to support the contract implementation.
		///</summary>
		///<param name="serviceHostBase">The host of the service.</param>
		///<param name="bindingParameters">Custom objects to which binding elements have access.</param>
		///<param name="serviceDescription">The service description of the service.</param>
		///<param name="endpoints">The service endpoints.</param>
		public void AddBindingParameters(
			ServiceDescription serviceDescription, ServiceHostBase serviceHostBase,
			Collection<ServiceEndpoint> endpoints, BindingParameterCollection bindingParameters)
		{
		}

		public void ApplyDispatchBehavior(ServiceDescription serviceDescription, ServiceHostBase serviceHostBase)
		{
			Dictionary<string, Type> contractNameToContractType = new Dictionary<string, Type>();
			foreach (ServiceEndpoint endpoint in serviceDescription.Endpoints)
			{
				contractNameToContractType[endpoint.Contract.Name] = endpoint.Contract.ContractType;
			}
			foreach (ChannelDispatcherBase cdb in serviceHostBase.ChannelDispatchers)
			{
				ChannelDispatcher cd = cdb as ChannelDispatcher;
				if (cd != null)
				{
					foreach (EndpointDispatcher ed in cd.Endpoints)
					{
						if (contractNameToContractType.ContainsKey(ed.ContractName))
						{
							ed.DispatchRuntime.InstanceProvider =
								new WindsorInstanceProvider(kernel,
								                            contractNameToContractType[ed.ContractName]
									);
						}
					}
				}
			}
		}

		#endregion
	}
}
