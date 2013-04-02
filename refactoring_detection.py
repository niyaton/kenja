from __future__ import absolute_import
from git.repo import Repo
from kenja.extract_method import detect_extract_method
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract Method Detector')
    parser.add_argument('historage_dir',
            help='path of historage repository dir')
    args = parser.parse_args()

    historage = Repo(args.historage_dir)
    extract_method_information = detect_extract_method(historage)

    candidate_revisions = set()
    for commit, org_commit, a_package, b_package, c, m, method, sim in extract_method_information:
        candidate_revisions.add(commit)
        target_method_info = ['jedit']
        if a_package:
            target_method_info.append(a_package)
        target_method_info.extend((c, m))
        target_method = '.'.join(target_method_info)
        extracted_method_info = ['jedit']
        if b_package:
            extracted_method_info.append(b_package)
        extracted_method_info.extend((c, method))
        extracted_method = '.'.join(extracted_method_info)
        print '"%s","%s","%s","%s","%s"' % (commit, org_commit, target_method, extracted_method, sim)
        #print '"%s","%s","%s","%s","%s","%s","%s","%s"' % info

    print 'candidates:', len(extract_method_information)
    print 'candidate revisions:', len(candidate_revisions)