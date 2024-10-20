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

namespace Castle.DynamicProxy.Tests
{
	using System;
	using NUnit.Framework;
	using System.Reflection.Emit;
	using System.IO;
	using System.Reflection;

	[TestFixture]
	public class ModuleScopeTestCase
	{
		[Test]
		public void ModuleScopeStoresModuleBuilder ()
		{
			ModuleScope scope = new ModuleScope ();
			ModuleBuilder one = scope.ObtainDynamicModuleWithStrongName ();
			ModuleBuilder two = scope.ObtainDynamicModuleWithStrongName ();

			Assert.AreSame (one, two);
			Assert.AreSame (one.Assembly, two.Assembly);
		}

		[Test]
		public void ModuleScopeCanHandleSignedAndUnsignedInParallel ()
		{
			ModuleScope scope = new ModuleScope ();
			Assert.IsNull (scope.StrongNamedModule);
			Assert.IsNull (scope.WeakNamedModule);

			ModuleBuilder one = scope.ObtainDynamicModuleWithStrongName ();
			Assert.IsNotNull (scope.StrongNamedModule);
			Assert.IsNull (scope.WeakNamedModule);
			Assert.AreSame (one, scope.StrongNamedModule);

			ModuleBuilder two = scope.ObtainDynamicModuleWithWeakName ();
			Assert.IsNotNull (scope.StrongNamedModule);
			Assert.IsNotNull (scope.WeakNamedModule);
			Assert.AreSame (two, scope.WeakNamedModule);

			Assert.AreNotSame (one, two);
			Assert.AreNotSame (one.Assembly, two.Assembly);

			ModuleBuilder three = scope.ObtainDynamicModuleWithStrongName ();
			ModuleBuilder four = scope.ObtainDynamicModuleWithWeakName ();

			Assert.AreSame (one, three);
			Assert.AreSame (two, four);
		}

#if !MONO

		[Test]
		public void ImplicitModulePaths ()
		{
			ModuleScope scope = new ModuleScope (true);
			Assert.AreEqual (ModuleScope.DEFAULT_FILE_NAME, scope.StrongNamedModuleName);
			Assert.AreEqual (Path.Combine (Environment.CurrentDirectory, ModuleScope.DEFAULT_FILE_NAME),
					scope.ObtainDynamicModuleWithStrongName ().FullyQualifiedName);
			Assert.IsNull (scope.StrongNamedModuleDirectory);

			Assert.AreEqual (ModuleScope.DEFAULT_FILE_NAME, scope.WeakNamedModuleName);
			Assert.AreEqual (Path.Combine (Environment.CurrentDirectory, ModuleScope.DEFAULT_FILE_NAME),
					scope.ObtainDynamicModuleWithWeakName ().FullyQualifiedName);
			Assert.IsNull (scope.WeakNamedModuleDirectory);
		}
		
		[Test]
		public void ExplicitModulePaths ()
		{
			ModuleScope scope = new ModuleScope (true, "Strong", "StrongModule.dll", "Weak", "WeakModule.dll");
			Assert.AreEqual ("StrongModule.dll", scope.StrongNamedModuleName);
			Assert.AreEqual (Path.Combine (Environment.CurrentDirectory, "StrongModule.dll"), scope.ObtainDynamicModuleWithStrongName ().FullyQualifiedName);
			Assert.IsNull (scope.StrongNamedModuleDirectory);

			Assert.AreEqual ("WeakModule.dll", scope.WeakNamedModuleName);
			Assert.AreEqual (Path.Combine (Environment.CurrentDirectory, "WeakModule.dll"), scope.ObtainDynamicModuleWithWeakName ().FullyQualifiedName);
			Assert.IsNull (scope.WeakNamedModuleDirectory);

			scope = new ModuleScope (true, "Strong", @"c:\Foo\StrongModule.dll", "Weak", @"d:\Bar\WeakModule.dll");
			Assert.AreEqual ("StrongModule.dll", scope.StrongNamedModuleName);
			Assert.AreEqual (@"c:\Foo\StrongModule.dll", scope.ObtainDynamicModuleWithStrongName ().FullyQualifiedName);
			Assert.AreEqual (@"c:\Foo", scope.StrongNamedModuleDirectory);

			Assert.AreEqual ("WeakModule.dll", scope.WeakNamedModuleName);
			Assert.AreEqual (@"d:\Bar\WeakModule.dll", scope.ObtainDynamicModuleWithWeakName ().FullyQualifiedName);
			Assert.AreEqual (@"d:\Bar", scope.WeakNamedModuleDirectory);
		}

#endif

		private static void CheckSignedSavedAssembly (string path)
		{
			Assert.IsTrue (File.Exists (path));

			AssemblyName assemblyName = AssemblyName.GetAssemblyName (path);
			Assert.AreEqual (ModuleScope.DEFAULT_ASSEMBLY_NAME, assemblyName.Name);

			byte[] keyPairBytes = ModuleScope.GetKeyPair ();
			StrongNameKeyPair keyPair = new StrongNameKeyPair (keyPairBytes);
			byte[] loadedPublicKey = assemblyName.GetPublicKey ();

			Assert.AreEqual (keyPair.PublicKey.Length, loadedPublicKey.Length);
			for (int i = 0; i < keyPair.PublicKey.Length; ++i)
				Assert.AreEqual (keyPair.PublicKey[i], loadedPublicKey[i]);
		}

		[Test]
		public void SaveSigned ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.ObtainDynamicModuleWithStrongName ();
			
			string path = ModuleScope.DEFAULT_FILE_NAME;
			if (File.Exists (path))
				File.Delete (path);

			Assert.IsFalse (File.Exists (path));
			scope.SaveAssembly ();

			CheckSignedSavedAssembly(path);
			File.Delete (path);
		}

		[Test]
		public void SaveUnsigned ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.ObtainDynamicModuleWithWeakName ();

			string path = ModuleScope.DEFAULT_FILE_NAME;
			if (File.Exists (path))
				File.Delete (path);

			Assert.IsFalse (File.Exists (path));
			scope.SaveAssembly ();

			CheckUnsignedSavedAssembly(path);
			File.Delete (path);
		}

		[Test]
		public void SaveWithPath ()
		{
			string strongModulePath = Path.GetTempFileName ();
			string weakModulePath = Path.GetTempFileName ();

			File.Delete (strongModulePath);
			File.Delete (weakModulePath);

			Assert.IsFalse (File.Exists (strongModulePath));
			Assert.IsFalse (File.Exists (weakModulePath));

			ModuleScope scope = new ModuleScope (true, "Strong", strongModulePath, "Weak", weakModulePath);
			scope.ObtainDynamicModuleWithStrongName ();
			scope.ObtainDynamicModuleWithWeakName ();

			scope.SaveAssembly (true);
			scope.SaveAssembly (false);

			Assert.IsTrue (File.Exists (strongModulePath));
			Assert.IsTrue (File.Exists (weakModulePath));

			File.Delete (strongModulePath);
			File.Delete (weakModulePath);
		}

		private static void CheckUnsignedSavedAssembly (string path)
		{
			Assert.IsTrue (File.Exists (path));

			AssemblyName assemblyName = AssemblyName.GetAssemblyName (path);
			Assert.AreEqual (ModuleScope.DEFAULT_ASSEMBLY_NAME, assemblyName.Name);

			byte[] loadedPublicKey = assemblyName.GetPublicKey ();
			Assert.IsNull (loadedPublicKey);
		}

		[Test]
		[ExpectedException (typeof (InvalidOperationException))]
		public void SaveThrowsWhenNoModuleObtained ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.SaveAssembly ();
		}

		[Test]
		[ExpectedException (typeof (InvalidOperationException))]
		public void SaveThrowsWhenMultipleAssembliesGenerated ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.ObtainDynamicModuleWithStrongName ();
			scope.ObtainDynamicModuleWithWeakName ();

			scope.SaveAssembly ();
		}

		[Test]
		public void SaveWithFlagFalseDoesntThrowsWhenMultipleAssembliesGenerated ()
		{
			ModuleScope scope = new ModuleScope (false);
			scope.ObtainDynamicModuleWithStrongName ();
			scope.ObtainDynamicModuleWithWeakName ();

			scope.SaveAssembly ();
		}

		[Test]
		public void ExplicitSaveWorksEvenWhenMultipleAssembliesGenerated ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.ObtainDynamicModuleWithStrongName ();
			scope.ObtainDynamicModuleWithWeakName ();

			scope.SaveAssembly (true);
			CheckSignedSavedAssembly (ModuleScope.DEFAULT_FILE_NAME);

			scope.SaveAssembly (false);
			CheckUnsignedSavedAssembly (ModuleScope.DEFAULT_FILE_NAME);

			File.Delete (ModuleScope.DEFAULT_FILE_NAME);
		}

		[Test]
		[ExpectedException (typeof (InvalidOperationException))]
		public void ExplicitSaveThrowsWhenSpecifiedAssemblyNotGeneratedWeakName ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.ObtainDynamicModuleWithStrongName ();

			scope.SaveAssembly (false);
		}

		[Test]
		[ExpectedException (typeof (InvalidOperationException))]
		public void ExplicitSaveThrowsWhenSpecifiedAssemblyNotGeneratedStrongName ()
		{
			ModuleScope scope = new ModuleScope (true);
			scope.ObtainDynamicModuleWithWeakName ();

			scope.SaveAssembly (true);
		}

		[Test]
		public void GeneratedAssembliesDefaultName ()
		{
			ModuleScope scope = new ModuleScope ();
			ModuleBuilder strong = scope.ObtainDynamicModuleWithStrongName ();
			ModuleBuilder weak = scope.ObtainDynamicModuleWithWeakName ();

			Assert.AreEqual (ModuleScope.DEFAULT_ASSEMBLY_NAME, strong.Assembly.GetName ().Name);
			Assert.AreEqual (ModuleScope.DEFAULT_ASSEMBLY_NAME, weak.Assembly.GetName ().Name);
		}

		[Test]
		public void GeneratedAssembliesWithCustomName ()
		{
			ModuleScope scope = new ModuleScope (false, "Strong", "Module1.dll", "Weak", "Module2,dll");
			ModuleBuilder strong = scope.ObtainDynamicModuleWithStrongName ();
			ModuleBuilder weak = scope.ObtainDynamicModuleWithWeakName ();

			Assert.AreEqual ("Strong", strong.Assembly.GetName ().Name);
			Assert.AreEqual ("Weak", weak.Assembly.GetName ().Name);
		}

    [Test]
    public void ModuleScopeDoesntTryToDeleteFromCurrentDirectory ()
    {
      string moduleDirectory = Path.Combine (Environment.CurrentDirectory, "GeneratedDlls");
      if (Directory.Exists (moduleDirectory))
        Directory.Delete (moduleDirectory, true);

      string strongModulePath = Path.Combine (moduleDirectory, "Strong.dll");
      string weakModulePath = Path.Combine (moduleDirectory, "Weak.dll");
      
      Directory.CreateDirectory(moduleDirectory);
      ModuleScope scope = new ModuleScope (true, "Strong", strongModulePath, "Weak", weakModulePath);

      using (File.Create (Path.Combine (Environment.CurrentDirectory, "Strong.dll")))
      {
        scope.ObtainDynamicModuleWithStrongName ();
        scope.SaveAssembly (true); // this will throw if SaveAssembly tries to delete from the current directory
      }

      using (File.Create (Path.Combine (Environment.CurrentDirectory, "Weak.dll")))
      {
        scope.ObtainDynamicModuleWithWeakName ();
        scope.SaveAssembly (false);  // this will throw if SaveAssembly tries to delete from the current directory
      }
    }
	}
}