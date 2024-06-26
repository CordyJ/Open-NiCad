package org.eclipse.jdt.internal.codeassist.complete;
import org.eclipse.jdt.internal.codeassist.complete.CompletionNodeFound;
import org.eclipse.jdt.internal.compiler.ast.MethodDeclaration;
import org.eclipse.jdt.internal.compiler.lookup.ClassScope;
import org.eclipse.jdt.internal.compiler.parser.*;
public class CompletionOnMethodName extends MethodDeclaration {
       public int selectorEnd;
       public void resolve(ClassScope upperScope) {
             super.resolve(upperScope);
             throw new CompletionNodeFound(this,upperScope); }
       public String toString(int tab) {
       /* slow code */
       String s = tabString(tab);
       s += "<CompletionOnMethodName:"; //$NON-NLS-1$
       if (modifiers != AccDefault) {
             s += modifiersString(modifiers); }
       s += returnTypeToString(0);
       s += new String(selector) + "("; //$NON-NLS-1$
       if (arguments != null) {
             for (int i = 0; i < arguments.length; i++) {
                  s += arguments[i].toString(0);
                  if (i != (arguments.length - 1))
                      s = s + ", "; //$NON-NLS-1$
             };
       };
       s += ")"; //$NON-NLS-1$
       if (thrownExceptions != null) {
             s += " throws "; //$NON-NLS-1$
             for (int i = 0; i < thrownExceptions.length; i++) {
                  s += thrownExceptions[i].toString(0);
                  if (i != (thrownExceptions.length - 1))
                      s = s + ", "; //$NON-NLS-1$
             };
       };
       s += ">"; //$NON-NLS-1$
       return s; } }
