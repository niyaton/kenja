package jp.naist.sd.kenja.factextractor.ast;

import java.io.File;
import java.util.LinkedList;
import java.util.List;

import jp.naist.sd.kenja.factextractor.Tree;
import jp.naist.sd.kenja.factextractor.Treeable;

import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class ASTCompilation implements Treeable {

	private Tree root;

	ASTPackage pack;

	private final String CLASS_ROOT_NAME = "[CN]";

	private final String INTERFACE_ROOT_NAME = "[IN]";

	private Tree classRoot;
	
	private List<ASTClass> classes = new LinkedList<ASTClass>();

	private Tree interfaceRoot;

	protected ASTCompilation() {

	}
	
	public static ASTCompilation fromCompilation(CompilationUnit unit){
		return new ASTCompilation(unit, new Tree(""));
	}
	
	public ASTCompilation(CompilationUnit unit, Tree root) {
		this.root = root;
		//if (unit.getPackage() != null) {
		//	pack = ASTPackage.fromPackageDeclaration(unit.getPackage());
		//	root.append(pack.getTree());
		//}

//		Tree typeRoot = root;
//		if (pack != null)
//			typeRoot = pack.getLeaf();
//		
//		if (typeRoot.has(CLASS_ROOT_NAME))
//			classRoot = typeRoot.getChild(CLASS_ROOT_NAME);
//		else
//			classRoot = new Tree(CLASS_ROOT_NAME);
//
//		if (typeRoot.has(INTERFACE_ROOT_NAME))
//			interfaceRoot = typeRoot.getChild(INTERFACE_ROOT_NAME);
//		else
//			interfaceRoot = new Tree(INTERFACE_ROOT_NAME);
//
//		typeRoot.append(classRoot);
//		typeRoot.append(interfaceRoot);

		addTypes(unit);
	}
	
	public List<String> getChangedFileList(File baseDir){
		return root.getObjectsPath("");
	}
	
	private Tree getClassRoot(){
		if(classRoot == null){
			classRoot = new Tree(CLASS_ROOT_NAME);
			getTypeRoot().append(classRoot);
		}
		
		return classRoot;
			
	}
	
	private Tree getInterfaceRoot(){
		if(interfaceRoot == null){
			interfaceRoot = new Tree(INTERFACE_ROOT_NAME);
			getTypeRoot().append(interfaceRoot);
		}
		
		return interfaceRoot;
	}
		
	private Tree getTypeRoot(){
		if(pack == null)
			return root;
		return pack.getLeaf();
	}

	public void addTypes(CompilationUnit unit) {
		for (Object o : unit.types()) {
			TypeDeclaration typeDec = (TypeDeclaration) o;
			if (typeDec.isInterface()) {
				// ASTInterface i = ASTInterface.
			} else {
				ASTClass c = ASTClass.fromTypeDeclaration(typeDec);
				getClassRoot().append(c.getTree());
			}
		}
	}

	@Override
	public Tree getTree() {
		return root;
	}
}
