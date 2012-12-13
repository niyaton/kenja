package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.IOException;

import com.google.common.base.Charsets;
import com.google.common.io.Files;

public class Blob {
	private String body;

	private String name;

	public Blob(String body, String name) {
		this.body = body;
		this.name = name;
	}

	public Blob(String name) {
		this.body = "";
		this.name = name;
	}

	public String getBody() {
		return body;
	}

	public String getName() {
		return name;
	}

	public void setBody(String body) {
		this.body = body;
	}

	public void setName(String name) {
		this.name = name;
	}

	public void writeBlob(File parentDir) {
		if (!parentDir.exists())
			try {
				Files.createParentDirs(parentDir);
				parentDir.mkdir();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		File blob = new File(parentDir, name);
		try {
			blob.createNewFile();
			Files.write(body, blob, Charsets.US_ASCII);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
