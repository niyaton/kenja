package jp.naist.sd.kenja.factextractor;

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
}
