package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;

import org.apache.commons.lang3.tuple.Pair;

import com.google.common.base.Charsets;
import com.google.common.io.Files;

public class TextFormatTreeWriter extends TreeWriter {
	private File outputFile;

	public TextFormatTreeWriter(File baseDir) {
		super(baseDir);
		outputFile = baseDir;
		// TODO Auto-generated constructor stub
	}

	@Override
	public void writeTree(Tree tree) {
		if (tree.isRoot()) {
			try {
				Files.touch(outputFile);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		} else {
			String line = "Start" + tree.getName() + "\n";
			try {
				Files.append(line, outputFile, Charsets.US_ASCII);
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}

		HashMap<String, Tree> treeMap = new HashMap<String, Tree>();
		for (Tree t : tree.getChildTrees()) {
			treeMap.put(t.getName(), t);
		}

		HashMap<String, Blob> blobMap = new HashMap<String, Blob>();
		for (Blob b : tree.getBlobs()) {
			blobMap.put(b.getName(), b);
		}

		for (Pair<String, String> content : createTreeContents(tree)) {
			if (content.getLeft() == "Blob") {
				writeBlob(blobMap.get(content.getRight()));
			} else if (content.getLeft() == "Tree") {
				writeTree(treeMap.get(content.getRight()));
			}
			StringBuilder builder = new StringBuilder();
			builder.append(content.getLeft());
			builder.append(" ");
			builder.append(content.getRight());
			builder.append("\n");
			try {
				Files.append(builder.toString(), outputFile, Charsets.US_ASCII);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		if (!tree.isRoot()) {
			String line = "End" + tree.getName() + "\n";
			try {
				Files.append(line, outputFile, Charsets.US_ASCII);
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}
	}

	@Override
	public void writeBlob(Blob blob) {
		int lines = blob.getBody().split("\n").length;
		try {
			Files.append(lines + " lines" + "\n", outputFile, Charsets.US_ASCII);
			Files.append(blob.getBody(), outputFile, Charsets.US_ASCII);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private List<Pair<String, String>> createTreeContents(Tree tree) {
		List<Pair<String, String>> contents = new ArrayList<Pair<String, String>>();

		for (Blob blbo : tree.getBlobs()) {
			contents.add(Pair.of("Blob", blbo.getName()));
		}

		for (Tree childTree : tree.getChildTrees()) {
			contents.add(Pair.of("Tree", childTree.getName()));
		}

		Comparator<Pair<String, String>> comparator = new Comparator<Pair<String, String>>() {

			@Override
			public int compare(Pair<String, String> o1, Pair<String, String> o2) {
				return o1.getRight().compareTo(o2.getRight());
			}
		};

		Collections.sort(contents, comparator);
		return contents;
	}
}
