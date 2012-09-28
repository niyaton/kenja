package jp.naist.sd.kenja.factextractor;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.jdt.core.dom.PackageDeclaration;

public class ASTPackage implements Treeable {

	private Tree root;

	private Tree leaf;

//	private static Map<String, Tree> packagesRoots = new HashMap<String, Tree>();

	private String packageName;

	private String[] separatedPackageName;

	protected ASTPackage() {

	}

	protected ASTPackage(PackageDeclaration packageDec) {
		packageName = packageDec.getName().toString();

		addPackage();
	}

	private void addPackage() {
		separatedPackageName = packageName.split("\\.");

		String packagePrefix = separatedPackageName[0];
//		if (!packagesRoots.containsKey(packagePrefix)) {
//			packagesRoots.put(packagePrefix, new Tree(packagePrefix));
//		}
//		root = packagesRoots.get(packagePrefix);
		root = new Tree(packagePrefix);

		leaf = root;
		for (int i = 1; i < separatedPackageName.length; i++) {
			if (leaf.hasTree(separatedPackageName[i])) {
				leaf = leaf.getChild(separatedPackageName[i]);
				continue;
			}

			Tree tree = new Tree(separatedPackageName[i]);
			leaf.append(tree);
			leaf = tree;
		}
	}

	public static ASTPackage fromPackageDeclaration(
			PackageDeclaration packageDec) {
		return new ASTPackage(packageDec);
	}

	@Override
	public Tree getTree() {
		return root;
	}

	public Tree getLeaf() {
		return leaf;
	}

}
