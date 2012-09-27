package jp.naist.sd.kenja.factextractor;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Block;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.core.dom.TypeDeclaration;

import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.Multimap;

public class TestASTVisitor extends ASTVisitor {
	
	private Multimap<ASTNode, ASTNode> tree = ArrayListMultimap.create();
	
	private PackageDeclaration nullPackage;
	
    @Override
    public boolean visit(MethodDeclaration node) {
            StringBuffer sb = new StringBuffer();
            
            sb.append("[Method]");
            Block body = node.getBody();
            
            sb.append(node.modifiers().toString() + " ");
            sb.append(" ");

            // Return Type
            if( !node.isConstructor() ){
                    sb.append(node.getReturnType2().toString() );
                    sb.append(" ");
            }

            // Parameters
            sb.append(node.getName().toString());
            sb.append("(");
            sb.append(node.parameters().toString() + ", ");
            sb.append(")");

//            System.out.println(sb);
            return super.visit(node);
    }
    
    @Override
    public boolean visit(PackageDeclaration node){
    	StringBuffer sb = new StringBuffer();
    	
    	sb.append("[package]: ");
    	
    	
    	sb.append(node.getName().toString());
    	
    	sb.append(node.getParent().getNodeType());
    	
    	System.out.println(sb);
    	return super.visit(node);
    }
    
    @Override
    public boolean visit(TypeDeclaration node){
    	if(node.isPackageMemberTypeDeclaration()){
    		ASTNode parent = node.getParent();
    		if(parent.getNodeType() == ASTNode.COMPILATION_UNIT){
    			System.out.println("This is in the compilation unit.");
    			System.out.println("[compilation]");
    			CompilationUnit unit = (CompilationUnit)parent;
    			
    			if(unit.getPackage() != null){
    				tree.put(unit.getPackage(), node);
    			}
    		}
    	}
    	
    	System.out.println("[type]:" + node.getName().toString());
    	if(node.getName().toString().equals("DownloadThreadTest")){
    		System.out.println("!!!!!!!!!!");
    		// TypeDeclaration superClass = node.getSuperclassType();
    		System.out.println(node.getSuperclassType().toString());
    	}
    	return super.visit(node);
    }

	public void showTree() {
		
		System.out.println("ShowTree!");
		System.out.println(tree.size());
		for(ASTNode node: tree.keys()){
			String packageName = "";
			if(node.getNodeType() == ASTNode.PACKAGE_DECLARATION){
				PackageDeclaration pack = (PackageDeclaration)node;
				packageName = pack.getName().toString();
				
			}
			
			for(ASTNode child: tree.get(node)){
				if(child.getNodeType() == ASTNode.TYPE_DECLARATION){
					TypeDeclaration type = (TypeDeclaration)child;
					System.out.println(packageName + "." + type.getName().toString());
				}
			}
		}
	}
    
}
