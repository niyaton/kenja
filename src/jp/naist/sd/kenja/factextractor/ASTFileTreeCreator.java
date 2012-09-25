package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;

import com.google.common.io.Files;

public class ASTFileTreeCreator {
	//private List<String> packages = new ArrayList<PackageDeclaration>();
	private Map<String, File> packages = new HashMap<String, File>();
	
	private File rootDir;
	
	public ASTFileTreeCreator(){
		rootDir = new File("root");
		rootDir.mkdir();
	}
	
	private String getRootPath(){
		return rootDir.getAbsolutePath();
	}
	
	private String getAbsolutePath(String path){
		StringBuilder builder = new StringBuilder();
		builder.append(getRootPath());
		builder.append("/");
		builder.append(path);
		return builder.toString();
	}
	
	public void append(PackageDeclaration pack){
		String packageName = pack.getName().getFullyQualifiedName();
		if(packages.containsKey(packageName)){
			return;
		}
		
		File dir = new File(getAbsolutePath(packageName.toString().replace('.', '/')));
		try {
			Files.createParentDirs(dir);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		dir.mkdir();
		
		packages.put(packageName, dir);
	}
	
	public void append(TypeDeclaration node, PackageDeclaration pack){
		File dir = packages.get(pack.getName().getFullyQualifiedName());
		
		if(node.isInterface()){
			appendInterface(node, dir);
		}
		else{
			appendClass(node, dir);
		}
	}
	
	private void appendClass(TypeDeclaration node, File parent){
		File dir = getTypeDir(parent, node.getName().toString(), "[CN]");
		
		for(MethodDeclaration method: node.getMethods()){
			appendMethod(method, dir);
		}
		
		for(FieldDeclaration field: node.getFields()){
			appendField(field, dir);
		}
	}
	
	private void appendInterface(TypeDeclaration node, File parent){
		File dir = getTypeDir(parent, node.getName().toString(), "[IN]");
	}
	
	private void appendMethod(MethodDeclaration node, File parent){
		File dir = getTypeDir(parent, node.getName().toString(), "[MT]");
	}
	
	private void appendField(FieldDeclaration node, File parent) {
		File fieldDir = new File(parent, "[FE]");
		//File targetDir = new File(sDir, simpleName);
		
		if(!fieldDir.exists()){
			try {
				Files.createParentDirs(fieldDir);
				fieldDir.mkdir();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		for (Object o : node.fragments()) {
			VariableDeclarationFragment fragment = (VariableDeclarationFragment) o;
			File targetDir = new File(fieldDir, fragment.getName().toString());
			targetDir.mkdir();
		}
	}
	
	
	private File getTypeDir(File parent, String simpleName, String suffix){
		//String suffix = "CN";
		//if(isInterface)
		//	suffix = "IN";
		File classDir = new File(parent, suffix);
		File targetDir = new File(classDir, simpleName);
		
		if(!classDir.exists()){
			try {
				Files.createParentDirs(targetDir);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		targetDir.mkdir();
		return targetDir;
	}
}
