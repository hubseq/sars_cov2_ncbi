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
#    datasets = aws_s3_utils.listSubFolders(remote_dir_in[0], [], [], '--no-sign-request')
#    print('DATASETS: {}'.format(str(datasets)))

    # make sure sra toolkit works
    os.chdir(output_dir)
    print(str(remote_dir_out))
    sf = aws_s3_utils.listSubFiles(remote_dir_out, ['.fastq', '.fq'], [])
    print('IN OUTPUT DIR: {}'.format(str(sf)))
    for f in sf:
        print('GET SAMPLE ID: {}'.format(file_utils.getSampleIDfromFASTQ(f)))
#    subprocess.call(['prefetch','ERR4424705'])
#    subprocess.call(['fastq-dump', 'ERR4424705'])
    return


if __name__ == '__main__':                                                                                                          
    run_sars_cov2_ncbi( sys.argv[1:] )
