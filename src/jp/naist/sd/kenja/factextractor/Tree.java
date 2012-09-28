package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

import com.google.common.io.Files;

public class Tree {

	private final String ROOT_NAME = "";
	
	private List<Blob> blobs = new ArrayList<Blob>();
	private List<Tree> trees = new ArrayList<Tree>();

	private String name;
	
	public boolean isRoot(){
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

	public void testPrint() {
		StringBuilder builder = new StringBuilder();
		// builder.append(this.name);
		// builder.append("\n");
		System.out.println(this.name);

		for (String line : getBlobsPath()) {
			// builder.append(line);
			System.out.println(line);
			// builder.append("\n");
		}

		for (String line : getChildTreesPath(true, this.name + "/")) {
			// builder.append(line);
			System.out.println(line);
			// builder.append("\n");
		}

		// return builder.toString();
	}

	private List<String> getChildTreesPath(boolean recursive, String prefix) {
		List<String> result = new ArrayList<String>();
		Stack<String> prefixStack = new Stack<String>();
		Stack<Tree> treeStack = new Stack<Tree>();

		prefixStack.push(this.name + "/");
		treeStack.push(this);

		while (!treeStack.empty()) {
			Tree t = treeStack.pop();
			prefix = prefixStack.pop();
			result.addAll(t.getBlobsPath(prefix));

			for (Tree next : t.trees) {
				treeStack.push(next);
				prefixStack.push(prefix + next.name + "/");
			}
		}
		return result;
	}

	private List<String> getBlobsPath() {
		String prefix = name + "/";
		return getBlobsPath(prefix);
	}

	public void writeTree(File baseDir) {
		if (!baseDir.exists())
			try {
				Files.createParentDirs(baseDir);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

		if (!name.equals("")) {
			baseDir = new File(baseDir, this.name);
			if (baseDir.exists())
				baseDir.mkdir();
		}

		for (Blob blob : blobs) {
			blob.writeBlob(baseDir);
		}

		for (Tree t : trees) {
			t.writeTree(baseDir);
		}
	}

	private List<String> getBlobsPath(String prefix) {
		List<String> result = new ArrayList<String>();
		for (Blob blob : blobs) {
			// result.add(prefix + blob.getName());
		}

		return result;
	}
}
