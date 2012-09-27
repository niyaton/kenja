package jp.naist.sd.kenja.factextractor;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.AbstractTypeDeclaration;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;

import com.google.common.base.Charsets;
import com.google.common.io.Files;

public class ASTFileTreeCreator {
	// private List<String> packages = new ArrayList<PackageDeclaration>();
	private Map<String, File> packages = new HashMap<String, File>();

	private PackageDeclaration currentPackage;

	private File rootDir;

	public ASTFileTreeCreator() {
		rootDir = new File("root");
		rootDir.mkdir();
	}

	public ASTFileTreeCreator(File root) {
		rootDir = root;
	}

	private String getRootPath() {
		return rootDir.getAbsolutePath();
	}

	private String getAbsolutePath(String path) {
		StringBuilder builder = new StringBuilder();
		builder.append(getRootPath());
		builder.append("/");
		builder.append(path);
		return builder.toString();
	}

	public void append(PackageDeclaration pack) {
		String packageName = pack.getName().getFullyQualifiedName();
		if (packages.containsKey(packageName)) {
			return;
		}

		File dir = new File(getAbsolutePath(packageName.toString().replace('.',
				'/')));
		try {
			Files.createParentDirs(dir);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		dir.mkdir();

		packages.put(packageName, dir);
	}

	public void append(TypeDeclaration node, PackageDeclaration pack) {
		File dir;
		if (pack == null)
			dir = rootDir;
		else
			dir = packages.get(pack.getName().getFullyQualifiedName());

		if (node.isInterface()) {
			appendInterface(node, dir);
		} else {
			appendClass(node, dir);
		}
	}

	private void appendClass(TypeDeclaration node, File parent) {
		File dir = getTypeDir(parent, node.getName().toString(), "[CN]");

		for (MethodDeclaration method : node.getMethods()) {
			appendMethod(method, dir);
		}

		for (FieldDeclaration field : node.getFields()) {
			appendField(field, dir);
		}
	}

	private void appendInterface(TypeDeclaration node, File parent) {
		File dir = getTypeDir(parent, node.getName().toString(), "[IN]");
	}

	private void appendMethod(MethodDeclaration node, File parent) {
		File dir = getTypeDir(parent, node.getName().toString(), "[MT]");
		if (node.getBody() != null) {
			File body = new File(dir, "body");
			try {
				BufferedWriter writer = Files
						.newWriter(body, Charsets.US_ASCII);
				writer.write(node.getBody().toString());

			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	private void appendField(FieldDeclaration node, File parent) {
		File fieldDir = new File(parent, "[FE]");
		// File targetDir = new File(sDir, simpleName);

		if (!fieldDir.exists()) {
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

	public void parseSourcecode(char[] src) {
		currentPackage = null;
		ASTParser parser = ASTParser.newParser(AST.JLS4);

		parser.setSource(src);

		NullProgressMonitor nullMonitor = new NullProgressMonitor();
		CompilationUnit unit = (CompilationUnit) parser.createAST(nullMonitor);

		visitCompilationUnit(unit);
	}

	private void visitCompilationUnit(CompilationUnit unit) {
		if (unit.getPackage() != null) {
			// System.out.println("[Package]:" + unit.getPackage().getName());
			append(unit.getPackage());
			currentPackage = unit.getPackage();
		}

		for (Object o : unit.types()) {
			AbstractTypeDeclaration type = (AbstractTypeDeclaration) o;
			if (type.getNodeType() == ASTNode.TYPE_DECLARATION)
				visitTopLevelTypeDeclarration((TypeDeclaration) type);
		}
	}

	private void visitTopLevelTypeDeclarration(TypeDeclaration node) {
		StringBuffer sb = new StringBuffer();

		append(node, this.currentPackage);

		for (FieldDeclaration field : node.getFields()) {
			for (Object o : field.fragments()) {
				VariableDeclarationFragment fragment = (VariableDeclarationFragment) o;
				sb.append("[Field]:" + fragment.getName());
			}
		}

		sb.append("\n");
		for (MethodDeclaration method : node.getMethods()) {
			visitMethod(method);
		}
		// System.out.println(sb.toString());
	}

	private void visitMethod(MethodDeclaration method) {
		StringBuffer sb = new StringBuffer();
		sb.append("[Method]:" + method.getName());
		sb.append("\n");

		if (method.getBody() != null) {
			sb.append(method.getBody().toString());
		}

		// System.out.println(sb.toString());
	}

	private File getTypeDir(File parent, String simpleName, String suffix) {
		// String suffix = "CN";
		// if(isInterface)
		// suffix = "IN";
		File classDir = new File(parent, suffix);
		File targetDir = new File(classDir, simpleName);

		if (!classDir.exists()) {
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
