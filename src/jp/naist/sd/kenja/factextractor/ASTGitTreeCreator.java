package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.commons.io.IOUtils;
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
	
	private void parseSourcecode(char[] src, File baseDir) {
		ASTParser parser = ASTParser.newParser(AST.JLS4);

		parser.setSource(src);

		NullProgressMonitor nullMonitor = new NullProgressMonitor();
		CompilationUnit unit = (CompilationUnit) parser.createAST(nullMonitor);
		ASTCompilation compilation = new ASTCompilation(unit, root);
		compilation.writeFiles(baseDir);	
		synchronized (changedPathList) {
			changedPathList.addAll(compilation.getChangedFileList(baseDir));
		}
	}
	
	private List<String> changedPathList;
	
	public List<String> getChangedPathList(){
		return changedPathList;
	}

	@Override
	public void run() {
		parseSourcecode(src, baseDir);
	}

	public void setPathList(List<String> changedPathList) {
		this.changedPathList = changedPathList;
	}
	
	public static void main(String[] args){
		if(args.length != 1){
			System.out.println("please input commit hash");
			return;
		}
		
		File baseDir = new File(args[0]);
		
		ASTGitTreeCreator creator = new ASTGitTreeCreator(baseDir);
			
		try {
			creator.setSource(IOUtils.toCharArray(System.in));
			creator.run();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
