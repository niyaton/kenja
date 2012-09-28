package jp.naist.sd.kenja.factextractor;

import java.io.File;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;

public class ASTGitTreeCreator implements Runnable{
	private Tree root = new Tree("");
	
	private char[] src;
	
	public void setSource(char[] src){
		this.src = src;
	}
	
	private File baseDir;
	
	public ASTGitTreeCreator(File baseDir){
		this.baseDir = baseDir;
	}
	
	public void parseSourcecode(char[] src, File baseDir) {
		ASTParser parser = ASTParser.newParser(AST.JLS4);

		parser.setSource(src);

		NullProgressMonitor nullMonitor = new NullProgressMonitor();
		CompilationUnit unit = (CompilationUnit) parser.createAST(nullMonitor);
		ASTCompilation compilation = new ASTCompilation(unit, root);
		compilation.writeFiles(baseDir);
	}
	
	//public String toString(){
		//return root.toString();
	//}
	public void testPrint(){
		root.testPrint();
	}

	@Override
	public void run() {
	ASTParser parser = ASTParser.newParser(AST.JLS4);

		parser.setSource(src);

		NullProgressMonitor nullMonitor = new NullProgressMonitor();
		CompilationUnit unit = (CompilationUnit) parser.createAST(nullMonitor);
		ASTCompilation compilation = new ASTCompilation(unit, root);
		compilation.writeFiles(baseDir);	
	}
}
