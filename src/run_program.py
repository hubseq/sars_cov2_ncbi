import os, subprocess, sys
import pandas as pd
import numpy as np
# sys.path.append('global_utils/src/')
sys.path.append('/global_utils/src/')
import module_utils
import aws_s3_utils
import file_utils

def run_sars_cov2_ncbi( arg_list ):
    """
    Parameters:
    -i not used
    -remotein <remote_dir_of_sars_cov2_sequencing_files>
    -remoteout <remote_output_dir>
    -listonly <True/False>
    -o <output_dir>
    """
    print('ARG LIST: {}'.format(str(arg_list)))
    remote_dir_in = module_utils.getArgument( arg_list, '-remotein', 'list' )  # remote input dir
    remote_dir_out = module_utils.getArgument( arg_list, '-remoteout', 'list' )  # remote output dir
    output_dir = module_utils.getArgument( arg_list, '-o' )  # local output dir
    list_only = module_utils.getArgument( arg_list, '-listonly' )
    
    # list all datasets and new datasets (check output dir for existing datasets)
    datasets = aws_s3_utils.listSubFolders(remote_dir_in[0], [], [], '--no-sign-request')

    # just test with first 10 datasets for now
    datasets = datasets[0:10]
    print('DATASETS: {}'.format(str(datasets_short)))
    
    # get existing datasets
    os.chdir(output_dir)
    # print(str(remote_dir_out))
    existing_files = aws_s3_utils.listSubFiles(remote_dir_out, ['.fastq', '.fq'], [])
    print('EXISTING FILES: {}'.format(str(existing_files)))
    existing_samples_list = list(set(list(map(lambda f: file_utils.getSampleIDfromFASTQ(f), existing_files)))) # list(set()) gets unique
    existing_samples_dict = dict(zip(existing_samples_list, len(existing_samples_list)*[1])) # dict is faster to search
    print('EXISTING SAMPLES: {}'.format(list(existing_samples_list)))
    
    # make sure sra toolkit works
    downloaded, not_downloaded, already_uploaded = [], [], []
    for d in datasets:
        if d not in existing_samples_dict:
            try:
                subprocess.check_call('prefetch {}'.format(str(d)), shell=True)
                subprocess.check_call('fastq-dump --gzip {}'.format(str(d)), shell=True)
                downloaded.append(d)
            except CalledProcessError:
                print('WARNING: Could not download {}'.format(str(d)))
                not_downloaded.append(d)
        else:
            already_updated.append(d)
            
    print('TOTAL DATASETS: {}'.format(str(len(datasets))))
    print('DATASETS DOWNLOADED SUCCESSFULLY: {}'.format(str(len(downloaded))))
    print('ERROR - NOT DOWNLOADED: {}'.format(str(len(not_downloaded))))
    print('ALREADY UPLOADED AND EXISTS: {}'.format(str(len(already_uploaded))))
    return


if __name__ == '__main__':                                                                                                          
    run_sars_cov2_ncbi( sys.argv[1:] )
