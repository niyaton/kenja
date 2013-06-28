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

	private static final String BLOB = "[BN] ";
	private static final String TREE = "[TN] ";

	private static final String BLOB_LINEINFO = "[BI] ";

	private static final String START_TREE = "[TS] ";
	private static final String END_TREE = "[TE] ";

	public TextFormatTreeWriter(File outputFile) throws IOException{
		this.outputFile = outputFile.getAbsoluteFile();
		if (!this.outputFile.getParentFile().exists()) {
			Files.createParentDirs(this.outputFile);
		}
	}

	public void writeTree(Tree tree) throws IOException{
		if (tree.isRoot()) {
			Files.touch(outputFile);
		} else {
			String line = START_TREE + tree.getName() + "\n";
			Files.append(line, outputFile, Charsets.US_ASCII);
		}

		HashMap<String, Tree> treeMap = createTreeMap(tree);
		HashMap<String, Blob> blobMap = createBlobMap(tree);

		for (Pair<String, String> content : createTreeContents(tree)) {
			StringBuilder builder = new StringBuilder();
			builder.append(content.getLeft());
			builder.append(content.getRight());
			builder.append("\n");
			if (content.getLeft() == BLOB) {
					Files.append(builder.toString(), outputFile,
							Charsets.US_ASCII);
				writeBlob(blobMap.get(content.getRight()));
			} else if (content.getLeft() == TREE) {
				writeTree(treeMap.get(content.getRight()));
			}

		}
		if (!tree.isRoot()) {
			String line = END_TREE + tree.getName() + "\n";
				Files.append(line, outputFile, Charsets.US_ASCII);
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

	public void writeBlob(Blob blob) throws IOException{
		int lines = 0;
		if (blob.getBody() != ""){
			lines = blob.getBody().split("\n").length;
		}
			Files.append(BLOB_LINEINFO + lines + "\n", outputFile,
					Charsets.US_ASCII);
			if(lines != 0){
				Files.append(blob.getBody(), outputFile, Charsets.US_ASCII);
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
