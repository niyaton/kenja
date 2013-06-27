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

public class TextFormatTreeWriter implements TreeWriter {
	private File outputFile;

	private static final String BLOB = "[Blob]";
	private static final String TREE = "[Tree]";

	private static final String BLOB_LINEINFO = "[BlobInfo]";

	private static final String START_TREE = "[StartTree]";
	private static final String END_TREE = "[EndTree]";

	public TextFormatTreeWriter(File outputFile) {
		this.outputFile = outputFile.getAbsoluteFile();
		if (!this.outputFile.getParentFile().exists()) {
			try {
				Files.createParentDirs(this.outputFile);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	public void writeTree(Tree tree) {
		if (tree.isRoot()) {
			try {
				Files.touch(outputFile);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		} else {
			String line = START_TREE + tree.getName() + "\n";
			try {
				Files.append(line, outputFile, Charsets.US_ASCII);
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}

		HashMap<String, Tree> treeMap = createTreeMap(tree);
		HashMap<String, Blob> blobMap = createBlobMap(tree);

		for (Pair<String, String> content : createTreeContents(tree)) {
			StringBuilder builder = new StringBuilder();
			builder.append(content.getLeft());
			builder.append(" ");
			builder.append(content.getRight());
			builder.append("\n");
			if (content.getLeft() == BLOB) {
				try {
					Files.append(builder.toString(), outputFile,
							Charsets.US_ASCII);
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				writeBlob(blobMap.get(content.getRight()));
			} else if (content.getLeft() == TREE) {
				writeTree(treeMap.get(content.getRight()));
				try {
					Files.append(builder.toString(), outputFile,
							Charsets.US_ASCII);
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}

		}
		if (!tree.isRoot()) {
			String line = END_TREE + tree.getName() + "\n";
			try {
				Files.append(line, outputFile, Charsets.US_ASCII);
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}
	}

	private HashMap<String, Tree> createTreeMap(Tree tree) {
		HashMap<String, Tree> result = new HashMap<String, Tree>();
		for (Tree childTree : tree.getChildTrees()) {
			result.put(childTree.getName(), childTree);
		}
		return result;
	}

	private HashMap<String, Blob> createBlobMap(Tree tree) {
		HashMap<String, Blob> result = new HashMap<String, Blob>();
		for (Blob blob : tree.getBlobs()) {
			result.put(blob.getName(), blob);
		}
		return result;
	}

	public void writeBlob(Blob blob) {
		int lines = blob.getBody().split("\n").length;
		try {
			Files.append(BLOB_LINEINFO + lines + " lines" + "\n", outputFile,
					Charsets.US_ASCII);
			Files.append(blob.getBody(), outputFile, Charsets.US_ASCII);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private List<Pair<String, String>> createTreeContents(Tree tree) {
		List<Pair<String, String>> contents = new ArrayList<Pair<String, String>>();

		for (Blob blbo : tree.getBlobs()) {
			contents.add(Pair.of(BLOB, blbo.getName()));
		}

		for (Tree childTree : tree.getChildTrees()) {
			contents.add(Pair.of(TREE, childTree.getName()));
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
