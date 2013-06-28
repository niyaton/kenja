package jp.naist.sd.kenja.factextractor;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Stack;

import org.apache.commons.lang3.tuple.Pair;

public class Tree {

	private final String ROOT_NAME = "";

	private List<Blob> blobs = new ArrayList<Blob>();
	private List<Tree> trees = new ArrayList<Tree>();

	private String name;

	public boolean isRoot() {
		return name.equals(ROOT_NAME);
	}

	public Tree(String name) {
		this.name = name;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public void append(Blob blob) {
		blobs.add(blob);
	}

	public void append(Tree tree) {
		trees.add(tree);
	}

	public void addAll(Iterable<Blob> blobs) {
		for (Blob blob : blobs) {
			this.blobs.add(blob);
		}
	}

	public Iterable<Blob> getBlobs() {
		return blobs;
	}

	public Iterable<Tree> getChildTrees() {
		return trees;
	}

	public boolean has(String name) {
		if (hasTree(name))
			return true;

		return hasBlob(name);
	}

	public Tree getChild(String name) {
		for (Tree t : trees) {
			if (t.getName().equals(name))
				return t;
		}

		return null;
	}

	public boolean hasBlob(String name) {
		for (Blob b : blobs) {
			if (b.getName().equals(name))
				return true;
		}

		return false;
	}

	public boolean hasTree(String name) {
		for (Tree t : trees) {
			if (t.getName().equals(name))
				return true;
		}
		return false;
	}

	public List<String> getObjectsPath(String prefix){
		Stack<Pair<String, Tree>> treeStack = new Stack<Pair<String, Tree>>();
		List<String> result = new LinkedList<String>();
		
		treeStack.push(Pair.of(prefix, this));
		
		while(!treeStack.empty()){
			Pair<String, Tree> pair = treeStack.pop();
			Tree tree = pair.getRight();
			prefix = pair.getLeft();
			
			if(!tree.isRoot()){
				prefix += tree.name + "/" ;
				result.add(prefix);
			}
			
			result.addAll(getBlobsPath(prefix));
			
			for(Tree t: tree.trees){
				treeStack.add(Pair.of(prefix, t));
			}
		}
		
		return result;
	}
	
	private List<String> getBlobsPath(String prefix) {
		List<String> result = new ArrayList<String>();
		for (Blob blob : blobs) {
			 result.add(prefix + blob.getName());
		}

		return result;
	}
}
