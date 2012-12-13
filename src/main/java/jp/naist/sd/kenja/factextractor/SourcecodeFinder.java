package jp.naist.sd.kenja.factextractor;

import java.io.File;
import java.io.FileFilter;
import java.io.FilenameFilter;
import java.util.ArrayList;
import java.util.List;

public class SourcecodeFinder {
	private List<String> extensions;
	
	private List<File> files = new ArrayList<File>();
	
	private String basePath;
	
	private FilenameFilter extensionFilter;
	
	private FileFilter directoryFilter = new FileFilter(){
		public boolean accept(File file){
			if(file.isDirectory())
				return true;
			return false;
		}
	};
	
	public List<File> getFiles(){
		return files;
	}
	
	public SourcecodeFinder(String basePath, List<String> extensions){
		this.extensions = extensions;
		this.basePath = basePath;
		
		this.extensionFilter = new ExtensionsFilter(this.extensions);
		
		this.findSourcecode();
	}
	
	private void findSourcecode(){
		File base = new File(basePath);
		if(!base.isDirectory())
			return;
		findSourcecode(base);
	}
	
	private void findSourcecode(File dir){
		for(File nextDir: dir.listFiles(directoryFilter)){
			findSourcecode(nextDir);
		}
		for(File file: dir.listFiles(extensionFilter)){
			files.add(file);			
		}
	}
}
