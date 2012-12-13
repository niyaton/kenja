package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.FilenameFilter;
import java.util.List;

public class ExtensionsFilter implements FilenameFilter{
	private List<String> extensions;
	
	public ExtensionsFilter(List<String> extensions){
		this.extensions = extensions;
	}
	
	@Override
	public boolean accept(File dir, String name) {
		for(String extension: extensions){
			if(name.endsWith(extension))
				return true;
		}
		return false;
	}
	
}
