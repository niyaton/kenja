package jp.naist.sd.kenja.factextractor;

import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class ASTClass extends ASTType {

	private final String FIELD_ROOT_NAME = "[FE]";

	private Tree fieldRoot = new Tree(FIELD_ROOT_NAME);

	protected ASTClass(TypeDeclaration typeDec) {
		super(typeDec.getName().toString());
		
		root.append(fieldRoot);

		for (MethodDeclaration methodDec : typeDec.getMethods()) {
			ASTMethod method = ASTMethod.fromMethodDeclaralation(methodDec);
			methodRoot.append(method.getTree());
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
