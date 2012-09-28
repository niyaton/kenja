package jp.naist.sd.kenja.factextractor;

import org.eclipse.jdt.core.dom.MethodDeclaration;

public class ASTMethod implements Treeable{
	
	private Blob body;
	
	private Tree root; 
	
	private static final String BODY_BLOB_NAME = "body";
	
	protected ASTMethod(){
		
	}
	
	protected ASTMethod(MethodDeclaration node){
		root = new Tree(node.getName().toString());
		
		body = new Blob(BODY_BLOB_NAME);
		if(node.getBody() == null)
			body.setBody("");
		else
			body.setBody(node.getBody().toString());
		
		root.append(body);
	}
	
	public static ASTMethod fromMethodDeclaralation(MethodDeclaration node){
		return new ASTMethod(node);
	}

	@Override
	public Tree getTree() {
		return root;
	}
}
