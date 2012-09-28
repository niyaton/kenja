package jp.naist.sd.kenja.factextractor;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;

public class ASTField implements Blobable{

	private List<Blob> blobs = new ArrayList<Blob>();
	
	protected ASTField(FieldDeclaration node){
		for(Object obj: node.fragments()){
			VariableDeclarationFragment fragment = (VariableDeclarationFragment)obj;
			blobs.add(new Blob(fragment.getName().toString()));
		}
	}
	
	public static ASTField fromFieldDeclaration(FieldDeclaration node){
		return new ASTField(node);
	}

	@Override
	public Iterable<Blob> getBlobs() {
		return blobs;
	}
}
