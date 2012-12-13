package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;

import org.apache.commons.io.IOUtils;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;

public class ASTGitTreeCreator{
	private Tree root = new Tree("");
	
	private File baseDir;
	
	private ASTCompilation compilation;
	
	public ASTGitTreeCreator(File baseDir){
		this.baseDir = baseDir;
	}
	
	private void parseSourcecode(char[] src) {
		ASTParser parser = ASTParser.newParser(AST.JLS4);

		parser.setSource(src);

		NullProgressMonitor nullMonitor = new NullProgressMonitor();
		CompilationUnit unit = (CompilationUnit) parser.createAST(nullMonitor);
		
		compilation = new ASTCompilation(unit, root);
	}
	
	public void writeASTAsFileTree(){
		compilation.getTree().writeTree(baseDir);
	}

	public static void main(String[] args){
		if(args.length != 1){
			System.out.println("please input commit hash");
			return;
		}
		
		File baseDir = new File(args[0]);
		ASTGitTreeCreator creator = new ASTGitTreeCreator(baseDir);
			
		try {
			creator.parseSourcecode(IOUtils.toCharArray(System.in));
			creator.writeASTAsFileTree();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
