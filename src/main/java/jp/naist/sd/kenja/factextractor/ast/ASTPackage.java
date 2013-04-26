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

	public static ASTPackage fromPackageDeclaration(
			PackageDeclaration packageDec) {
		return new ASTPackage(packageDec);
	}

	@Override
	public Iterable<Blob> getBlobs() {
		return blobs;
	}

}
