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

namespace Castle.Core.Logging.Factories
{
	using System;
	using System.IO;

	public abstract class AbstractExtendedLoggerFactory : MarshalByRefObject, IExtendedLoggerFactory
	{
		#region IExtendedLoggerFactory Members

		/// <summary>
		/// Creates a new extended logger, getting the logger name from the specified type.
		/// </summary>
		public virtual IExtendedLogger Create(Type type)
		{
			if (type == null) throw new ArgumentNullException("type");

			return Create(type.FullName);
		}

		/// <summary>
		/// Creates a new extended logger.
		/// </summary>
		public abstract IExtendedLogger Create(string name);

		/// <summary>
		/// Creates a new extended logger, getting the logger name from the specified type.
		/// </summary>
		public virtual IExtendedLogger Create(Type type, LoggerLevel level)
		{
			if (type == null) throw new ArgumentNullException("type");

			return Create(type.FullName, level);
		}

		/// <summary>
		/// Creates a new extended logger.
		/// </summary>
		public abstract IExtendedLogger Create(string name, LoggerLevel level);

		#endregion

		#region ILoggerFactory Members

		/// <summary>
		/// Creates a new logger, getting the logger name from the specified type.
		/// </summary>
		ILogger ILoggerFactory.Create(Type type)
		{
			return Create(type);
		}

		/// <summary>
		/// Creates a new logger.
		/// </summary>
		ILogger ILoggerFactory.Create(string name)
		{
			return Create(name);
		}

		/// <summary>
		/// Creates a new logger, getting the logger name from the specified type.
		/// </summary>
		ILogger ILoggerFactory.Create(Type type, LoggerLevel level)
		{
			return Create(type, level);
		}

		/// <summary>
		/// Creates a new logger.
		/// </summary>
		ILogger ILoggerFactory.Create(string name, LoggerLevel level)
		{
			return Create(name, level);
		}

		#endregion

		/// <summary>
		/// Gets the configuration file.
		/// </summary>
		/// <param name="filename">i.e. log4net.config</param>
		/// <returns></returns>
		protected FileInfo GetConfigFile(string filename)
		{
			FileInfo result;

			if (Path.IsPathRooted(filename))
			{
				result = new FileInfo(filename);
			}
			else
			{
				result = new FileInfo(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, filename));
			}

			return result;
		}
	}
}