package jp.naist.sd.kenja.factextractor;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.AbstractTypeDeclaration;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;

import com.google.common.collect.Multimap;

import jp.naist.sd.kenja.factextractor.TestASTVisitor;

public class ASTParserTest {
	
	private List<PackageDeclaration> packages = new ArrayList<PackageDeclaration>();
	
	private PackageDeclaration currentPackage;
	
	private ASTFileTreeCreator treeCreator = new ASTFileTreeCreator();

	public static void main(String[] args){
		String filePath = "/Users/kenjif/repos/git-svn/columba_all/ristretto/trunk/src/test/org/columba/ristretto/testserver/TestServerSession.java";
		String baseDirPath = "/Users/kenjif/repos/git-svn/columba_all";
		
		ASTParserTest test = new ASTParserTest();
//		test.createAST(filePath);
		test.createAST(test.searchSourceCode(baseDirPath));
	}
	
	public ASTParserTest(){
		
	}
	
	private List<File> searchSourceCode(String directoryPath){
		List<String> extensions = new ArrayList<String>();
		extensions.add(".java");
		
		SourcecodeFinder finder = new SourcecodeFinder(directoryPath, extensions);
		return finder.getFiles();		
	}
	
	public void createAST(File file){
		ASTParser parser = ASTParser.newParser(AST.JLS4);
		
		StringBuffer sb = new StringBuffer();
		try {
			BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
			String line;
			while((line = br.readLine()) != null){
				sb.append(line + "\n");
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
			
		parser.setSource(sb.toString().toCharArray());

		NullProgressMonitor nullMonitor = new NullProgressMonitor();
		CompilationUnit unit = (CompilationUnit) parser.createAST(nullMonitor);

		visitCompilationUnit(unit);
			
		
	    //TestASTVisitor visitor = new TestASTVisitor();
		//unit.accept(visitor);
		
		//visitor.showTree();
	}
	
	private void visitCompilationUnit(CompilationUnit unit){
		if(unit.getPackage() != null){
			//System.out.println("[Package]:" + unit.getPackage().getName());
			treeCreator.append(unit.getPackage());
			currentPackage = unit.getPackage();
		}
		
		for(Object o: unit.types()){
			AbstractTypeDeclaration type = (AbstractTypeDeclaration)o;
			if(type.getNodeType() == ASTNode.TYPE_DECLARATION)
				visitTopLevelTypeDeclarration((TypeDeclaration)type);
		}	
	}
	
	private void visitTopLevelTypeDeclarration(TypeDeclaration node){
		StringBuffer sb = new StringBuffer();
		
		treeCreator.append(node, this.currentPackage);
		
		for(FieldDeclaration field: node.getFields()){
			for(Object o: field.fragments()){
				VariableDeclarationFragment fragment = (VariableDeclarationFragment)o;
				sb.append("[Field]:" + fragment.getName());
			}
		}
		
		sb.append("\n");
		for(MethodDeclaration method: node.getMethods()){
			visitMethod(method);
		}	
		System.out.println(sb.toString());
	}
	
	private void visitMethod(MethodDeclaration method){
		StringBuffer sb = new StringBuffer();
		sb.append("[Method]:" + method.getName());
		sb.append("\n");	
		
		if(method.getBody() != null){
			sb.append(method.getBody().toString());
		}
		
		System.out.println(sb.toString());
	}
	
	public void createAST(List<File> files){
		for(File file: files){
		    System.out.println("Creating:" + file.getAbsolutePath());
			createAST(file);
		    System.out.println("Done!");
		}
	}
	
}
