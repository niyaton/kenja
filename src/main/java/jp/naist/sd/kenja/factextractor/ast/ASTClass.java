package jp.naist.sd.kenja.factextractor.ast;

import java.util.HashSet;

import jp.naist.sd.kenja.factextractor.Tree;

import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class ASTClass extends ASTType {

	private final String FIELD_ROOT_NAME = "[FE]";
	private final String CONSTURCTOR_ROOT_NAME = "[CS]";

	private Tree fieldRoot = new Tree(FIELD_ROOT_NAME);
	private Tree constructorRoot = new Tree(CONSTURCTOR_ROOT_NAME);

	protected ASTClass(TypeDeclaration typeDec) {
		super(typeDec.getName().toString());
		
		root.append(fieldRoot);
		root.append(constructorRoot);

		//HashSet<String> tmpHashSet = new HashSet<String>();
		for (MethodDeclaration methodDec : typeDec.getMethods()) {
			//if(tmpHashSet.contains(methodDec.getName().toString())){
			//	System.out.println(methodDec.getName());
			//	continue;
			//}
			//tmpHashSet.add(methodDec.getName().toString());
			ASTMethod method = ASTMethod.fromMethodDeclaralation(methodDec);
			if(method.isConstructor()){
				constructorRoot.append(method.getTree());
			}
			else{
				methodRoot.append(method.getTree());
			}
			// TODO overload methods
		}

		for (FieldDeclaration fieldDec : typeDec.getFields()) {
			ASTField field = ASTField.fromFieldDeclaration(fieldDec);
			fieldRoot.addAll(field.getBlobs());
		}
	}

	public static ASTClass fromTypeDeclaration(TypeDeclaration node) {
		return new ASTClass(node);
	}

}
