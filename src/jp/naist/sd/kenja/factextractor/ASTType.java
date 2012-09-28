package jp.naist.sd.kenja.factextractor;

public abstract class ASTType implements Treeable{

	private final String METHOD_ROOT_NAME = "[MT]";
	
	protected Tree root;
	
	protected Tree methodRoot;
	
	protected ASTType(){
		
	}
	
	public ASTType(String name) {
		root = new Tree(name);
		methodRoot = new Tree(METHOD_ROOT_NAME);
		root.append(methodRoot);
	}

	@Override
	public Tree getTree() {
		return root;
	}
}
