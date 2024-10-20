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

namespace Castle.Windsor
{
	/// <summary>
	/// Gets the environment information (name). Implementors should 
	/// use to define their environments and how those affect the configuration.
	/// It is also used by the <see cref="Castle.Windsor.Configuration.Interpreters.XmlInterpreter"/>
	/// to define a flag with the environment name.
	/// </summary>
	public interface IEnvironmentInfo
	{
		/// <summary>
		/// Gets the name of the environment.
		/// </summary>
		/// <returns></returns>
		string GetEnvironmentName();
	}
}
