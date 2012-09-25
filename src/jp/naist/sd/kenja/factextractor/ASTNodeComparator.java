package jp.naist.sd.kenja.factextractor;

import java.util.Comparator;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class ASTNodeComparator implements Comparator<ASTNode> {

	@Override
	public int compare(ASTNode left, ASTNode right) {
		// TODO Auto-generated method stub
		if(left.getNodeType() == ASTNode.COMPILATION_UNIT)
			return -1;
		
		if(left.getNodeType() == ASTNode.PACKAGE_DECLARATION && right.getNodeType() != ASTNode.COMPILATION_UNIT)
			return -1;
			
		
		
		
		return 0;
	}

}
