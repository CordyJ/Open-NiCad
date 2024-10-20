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

namespace Castle.MonoRail.Framework.Internal
{
	using System;
	using Castle.MonoRail.Framework.Helpers;

	/// <summary>
	/// Abstract class that contains the shared logic of JS Generation, separated from
	/// the various view engines implementations
	/// </summary>
	public abstract class JSGeneratorBase
	{
		/// <summary>
		/// The generator instance
		/// </summary>
		protected readonly IJSGenerator generator;

		/// <summary>
		/// Initializes a new instance of the <see cref="JSGeneratorBase"/> class.
		/// </summary>
		/// <param name="generator">The generator.</param>
		protected JSGeneratorBase(IJSGenerator generator)
		{
			this.generator = generator;
		}

		/// <summary>
		/// Executes an operation (totally late bound)
		/// </summary>
		/// <param name="method">The method.</param>
		/// <param name="args">The args.</param>
		/// <returns></returns>
		protected object InternalInvoke(string method, params object[] args)
		{
			if (method == "el")
			{
				if (args == null || args.Length != 1)
				{
					throw new ArgumentException("el() method must be invoked with the element name as an argument");
				}
				if (args[0] == null)
				{
					throw new ArgumentNullException("el() method invoked with a null argument");
				}

				return CreateJSElementGenerator(
					generator.CreateElementGenerator(args[0].ToString()));
			}
			else if (method == "select")
			{
				if (args == null || args.Length != 1)
				{
					throw new ArgumentException(
						"select() method must be invoked with the element/css selection rule name as an argument");
				}
				if (args[0] == null)
				{
					throw new ArgumentNullException("select() method invoked with a null argument");
				}

				return CreateJSCollectionGenerator(
					generator.CreateCollectionGenerator(args[0].ToString()));
			}

			DynamicDispatchSupport dispInterface = generator as DynamicDispatchSupport;
			if (dispInterface == null)
			{
				throw new MonoRail.Framework.RailsException("JS Generators must inherit DynamicDispatchSupport");
			}

			if (dispInterface.IsGeneratorMethod(method))
			{
				return dispInterface.Dispatch(method, args);
			}

			return CreateNullGenerator();
		}

		/// <summary>
		/// Creates a null generator.
		/// </summary>
		/// <returns></returns>
		protected abstract object CreateNullGenerator();

		/// <summary>
		/// Creates a JS collection generator.
		/// </summary>
		/// <param name="collectionGenerator">The collection generator.</param>
		/// <returns></returns>
		protected abstract object CreateJSCollectionGenerator(IJSCollectionGenerator collectionGenerator);

		/// <summary>
		/// Creates a JS element generator.
		/// </summary>
		/// <param name="elementGenerator">The element generator.</param>
		/// <returns></returns>
		protected abstract object CreateJSElementGenerator(IJSElementGenerator elementGenerator);

		/// <summary>
		/// Delegates to the generator
		/// </summary>
		/// <returns>
		/// A <see cref="T:System.String"></see> that represents the current <see cref="T:System.Object"></see>.
		/// </returns>
		public override string ToString()
		{
			return generator.ToString();
		}
	}
}