package jp.naist.sd.kenja.git;

import java.io.File;
import java.io.IOException;
import java.util.Stack;

import jp.naist.sd.kenja.factextractor.ASTGitTreeCreator;

import org.apache.commons.io.IOUtils;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.ConcurrentRefUpdateException;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.api.errors.NoHeadException;
import org.eclipse.jgit.api.errors.NoMessageException;
import org.eclipse.jgit.api.errors.UnmergedPathsException;
import org.eclipse.jgit.api.errors.WrongRepositoryStateException;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.diff.DiffEntry.ChangeType;
import org.eclipse.jgit.errors.AmbiguousObjectException;
import org.eclipse.jgit.errors.CorruptObjectException;
import org.eclipse.jgit.errors.IncorrectObjectTypeException;
import org.eclipse.jgit.errors.MissingObjectException;
import org.eclipse.jgit.lib.Constants;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectLoader;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevSort;
import org.eclipse.jgit.revwalk.RevTree;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import org.eclipse.jgit.treewalk.TreeWalk;
import org.eclipse.jgit.treewalk.filter.PathSuffixFilter;

public class Git2Historage {

	private Stack<Thread> threadPool = new Stack<Thread>();
	
	public static void main(String[] args) {
		File testDir = new File(
				"/Users/kenjif/Documents/workspace-juno/kenja2/test/.git");
		File testBaseDir = new File(
				"/Users/kenjif/repos/git-svn/columba_all/.git");

		Git2Historage historage = new Git2Historage();
		historage.createHistorage(testDir, testBaseDir);
		historage.traceBaseHistory();
	}

	private Repository baseRepository;

	private Repository hisotrageRepository;

	private RevCommit previousCommit;
	

	// private ASTParserTest parser = new ASTParserTest();
//	private ASTFileTreeCreator creator;
	private ASTGitTreeCreator creator;

	public Git2Historage() {

	}

	private File baseDir = new File("/Users/kenjif/Documents/workspace-juno/kenja2/historage");
	public void createHistorage(File historageDir, File baseRepository) {
//		creator = new ASTFileTreeCreator(new File(
//				"/Users/kenjif/Documents/workspace-juno/kenja2/historage"));
	
//		creator = new ASTGitTreeCreator();
		
		try {
			FileRepositoryBuilder builder = new FileRepositoryBuilder();
			builder.setGitDir(baseRepository);
			builder.setMustExist(true);
			this.baseRepository = builder.build();

			builder = new FileRepositoryBuilder();
			builder.setGitDir(historageDir);
			// builder.setBare();
			builder.setWorkTree(new File(
					"/Users/kenjif/Documents/workspace-juno/kenja2/historage"));
			this.hisotrageRepository = builder.build();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private void traceBaseHistory() {
		try {
			ObjectId head = baseRepository.resolve(Constants.HEAD);
			RevWalk walk = new RevWalk(baseRepository);
			walk.sort(RevSort.TOPO);
			walk.sort(RevSort.REVERSE);
			walk.markStart(walk.lookupCommit(head));
			for (RevCommit commit : walk) {
				processCommit(commit);
			}
		} catch (AmbiguousObjectException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private void processCommit(RevCommit commit) {

		RevTree tree = commit.getTree();
		PathSuffixFilter filter = PathSuffixFilter.create(".java");
		TreeWalk walker = new TreeWalk(baseRepository);

		walker.setFilter(filter);
		walker.setRecursive(true);
		if (previousCommit == null) {
			try {
				walker.addTree(tree.getId());
				while (walker.next()) {
					System.out
							.println("[file name?]:" + walker.getPathString());
					loadJavaFile(walker.getObjectId(0));
					// System.out.println("[file?]:" +
					// walker.getObjectId(0).name());
					// walker.enterSubtree();
				}
			} catch (MissingObjectException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IncorrectObjectTypeException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (CorruptObjectException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

		} else {
			RevTree previousTree = previousCommit.getTree();
			try {
				walker.addTree(previousTree);
				walker.addTree(tree);
				for (DiffEntry diff : DiffEntry.scan(walker)) {
					if (diff.getChangeType() == ChangeType.DELETE)
						continue;
					System.out.println("[change?]:" + diff.getNewPath());
					loadJavaFile(diff.getNewId().toObjectId());
				}
			} catch (MissingObjectException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (IncorrectObjectTypeException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (CorruptObjectException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}

		System.out.println(commit.name());
		previousCommit = commit;

		while(!threadPool.empty()){
			if(!threadPool.peek().isAlive())
				threadPool.pop();
		}
		
		Git git = new Git(hisotrageRepository);
		try {
			git.add().addFilepattern(".").call();
			git.commit().setAll(true).setAuthor("Kenja", "kenji-f@is.naist.jp")
					.setMessage(commit.name()).call();
		} catch (NoHeadException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NoMessageException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (UnmergedPathsException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ConcurrentRefUpdateException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (WrongRepositoryStateException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (GitAPIException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private void loadJavaFile(ObjectId id) {
		try {
			ObjectLoader loader = baseRepository.open(id);
			ASTGitTreeCreator creator = new ASTGitTreeCreator(baseDir);
			creator.setSource(IOUtils.toCharArray(loader.openStream()));
			Thread thread = new Thread(creator);
			threadPool.add(thread);
			thread.run();
		} catch (MissingObjectException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
