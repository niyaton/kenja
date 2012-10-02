package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.util.List;

import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class ASTCompilation implements Treeable {

	private Tree root;

	ASTPackage pack;

	private final String CLASS_ROOT_NAME = "[CN]";

	private final String INTERFACE_ROOT_NAME = "[IN]";

	private Tree classRoot;

	private Tree interfaceRoot;

	protected ASTCompilation() {

	}

	
	public static ASTCompilation fromCompilation(CompilationUnit unit){
		return new ASTCompilation(unit, new Tree(""));
	}
	
	protected ASTCompilation(CompilationUnit unit, Tree root) {
		this.root = root;
		if (unit.getPackage() != null) {
			pack = ASTPackage.fromPackageDeclaration(unit.getPackage());
			root.append(pack.getTree());
		}

		Tree typeRoot = root;
		if (pack != null)
			typeRoot = pack.getLeaf();
		
		if (typeRoot.has(CLASS_ROOT_NAME))
			classRoot = typeRoot.getChild(CLASS_ROOT_NAME);
		else
			classRoot = new Tree(CLASS_ROOT_NAME);

		if (typeRoot.has(INTERFACE_ROOT_NAME))
			interfaceRoot = typeRoot.getChild(INTERFACE_ROOT_NAME);
		else
			interfaceRoot = new Tree(INTERFACE_ROOT_NAME);

		typeRoot.append(classRoot);
		typeRoot.append(interfaceRoot);

		addTypes(unit);
	}
	
	public void writeFiles(File baseDir){
		root.writeTree(baseDir);
//		for(String str: root.getObjectsPath(baseDir.getAbsolutePath())){
//			System.out.println(str);
//		}
	}
	
	public List<String> getChangedFileList(File baseDir){
		return root.getObjectsPath("");
	}

	public void addTypes(CompilationUnit unit) {
		for (Object o : unit.types()) {
			TypeDeclaration typeDec = (TypeDeclaration) o;
			if (typeDec.isInterface()) {
				// ASTInterface i = ASTInterface.
			} else {
				ASTClass c = ASTClass.fromTypeDeclaration(typeDec);
				classRoot.append(c.getTree());
			}
		}
	}

	@Override
	public Tree getTree() {
		return root;
	}

}
