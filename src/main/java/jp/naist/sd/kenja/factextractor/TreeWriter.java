package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;


import com.google.common.base.Charsets;
import com.google.common.io.Files;

public class TreeWriter {

	private File baseDir;
	private File currentDir;

	public TreeWriter(File baseDir) {
		this.baseDir = baseDir;
		if (!baseDir.exists()) {
			try {
				Files.createParentDirs(baseDir);
				baseDir.mkdir();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	public void writeTree(Tree tree) {
		if (!tree.isRoot()) {
			currentDir = new File(baseDir, tree.getName());
			if (!currentDir.exists())
				currentDir.mkdir();
		}

		for (Blob blob : tree.getBlobs()) {
			writeBlob(blob);
		}

		for (Tree childTree : tree.getChildTrees()) {
			writeTree(childTree);
		}
	}

	public void writeBlob(Blob blob) {
		if (!currentDir.exists())
			try {
				Files.createParentDirs(currentDir);
				currentDir.mkdir();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		File blobFile = new File(currentDir, blob.getName());
		try {
			blobFile.createNewFile();
			Files.write(blob.getBody(), blobFile, Charsets.US_ASCII);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
