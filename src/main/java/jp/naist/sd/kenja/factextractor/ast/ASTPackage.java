package jp.naist.sd.kenja.factextractor.ast;

import java.util.ArrayList;
import java.util.List;

import jp.naist.sd.kenja.factextractor.Blob;
import jp.naist.sd.kenja.factextractor.Blobable;
import jp.naist.sd.kenja.factextractor.Tree;
import jp.naist.sd.kenja.factextractor.Treeable;

import org.eclipse.jdt.core.dom.PackageDeclaration;

public class ASTPackage implements Blobable{

	public static final String PACKAGE_BLOB_NAME = "package";

	private String packageName;

	private Blob blob;
	
	private List<Blob> blobs = new ArrayList<Blob>();

	protected ASTPackage() {

	}

	protected ASTPackage(PackageDeclaration packageDec) {
		packageName = packageDec.getName().toString();

		blob = new Blob(PACKAGE_BLOB_NAME);
		blob.setBody(packageName);
		blobs.add(blob);
	}

	private void addPackage() {
		//separatedPackageName = packageName.split("\\.");

		//String packagePrefix = separatedPackageName[0];
		//root = new Tree(packagePrefix);

		//leaf = root;
		//for (int i = 1; i < separatedPackageName.length; i++) {
		//	if (leaf.hasTree(separatedPackageName[i])) {
		//		leaf = leaf.getChild(separatedPackageName[i]);
		//		continue;
		//	}
//
//			Tree tree = new Tree(separatedPackageName[i]);
//			leaf.append(tree);
//			leaf = tree;
//		}
	}

	public static ASTPackage fromPackageDeclaration(
			PackageDeclaration packageDec) {
		return new ASTPackage(packageDec);
	}

	@Override
	public Iterable<Blob> getBlobs() {
		return blobs;
	}

}
