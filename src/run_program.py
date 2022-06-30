import os, subprocess, sys
import pandas as pd
import numpy as np
# sys.path.append('global_utils/src/')
sys.path.append('/global_utils/src/')
import module_utils
import aws_s3_utils
import file_utils
import xmltodict, json

def xml2json( xml_in, as_json_string = 'True' ):
    json_out = xml_in[:-4]+'.json'
    with open(xml_in) as xml_file, open(json_out,'w') as fout:
        data_dict = xmltodict.parse(xml_file.read())
        if as_json_string[0].upper() == 'T':
            json_str = json.dumps(data_dict)
            fout.write(json_str)
        else:
            json.dump(data_dict, fout)
            # print(data_dict)
        # json_str_print = json.dumps(data_dict, indent=2)
        # print(json_str_print)
    return json_out


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
    remote_dir_in = module_utils.getArgument( arg_list, '-remotein' )  # remote input dir
    remote_dir_out = module_utils.getArgument( arg_list, '-remoteout', 'list' )  # remote output dir
    output_dir = module_utils.getArgument( arg_list, '-o' )  # local output dir
    list_only = module_utils.getArgument( arg_list, '-listonly' )
    
    # list all datasets and new datasets (check output dir for existing datasets)
    # datasets = aws_s3_utils.listSubFolders(remote_dir_in, [], [], '--no-sign-request')

    # just test with first 10 datasets for now
    # datasets = datasets[0:3]
    datasets = ['DRR001793', 'DRR009863'] # , 'DRR029830']
    print('DATASETS: {}'.format(str(datasets)))
    
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
            print('trying to download {}'.format(str(d)))
            try:
                # get SRA
                indir = '{}/{}/{}'.format(remote_dir_in.rstrip('/'),d,d)
                outfile_base = os.path.join(output_dir,d)
                print('fetching...{}'.format(indir))
                aws_s3_utils.downloadFile_S3('{}/{}/{}'.format(remote_dir_in.rstrip('/'),d,d), output_dir)
                ## subprocess.check_call('prefetch --max-size 30g {}'.format(str(d)), shell=True)
                # convert to FASTQ
                print('dumping fastq...{}'.format(str(d)))
                subprocess.check_call('fastq-dump --gzip {}'.format(str(outfile_base)), shell=True)
                downloaded.append(d)
                # get metadata
                # cmd = 'esearch -db sra -query {} | efetch -format xml'.format(d)
                # ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                # output_xml_stream = ps.communicate()[0]
                # print(output_xml_stream)
                # output_xml_file = '{}.xml'.format(os.path.join(output_dir,d))
                # with open(output_xml_file,'w') as fout:
                #    fout.write(output_xml_stream.decode("utf-8"))
                output_xml_file = os.path.join(output_dir, '{}.xml'.format(d))
                # temp_xml_file = os.path.join(output_dir,'tempp.xml')
                print('getting metadata xml from NCBI...')
                # subprocess.check_call('/root/edirect/esearch -db sra -query {} > {}'.format(d, temp_xml_file), shell=True)
                # subprocess.check_call('/root/edirect/efetch -format xml < {} > {}'.format(temp_xml_file, output_xml_file), shell=True)
                subprocess.check_call('/root/edirect/esearch -db sra -query | /root/edirect/efetch -format xml > {}'.format(output_xml_file), shell=True)
                print('outputing json metadata...')
                output_json_file = xml2json( output_xml_file )
                # remove temporary files
                subprocess.check_call('rm -rf {}'.format(os.path.join(output_dir,d)), shell=True)
                subprocess.check_call('rm {}'.format(output_xml_file), shell=True)
                # subprocess.check_call('rm {}'.format(temp_xml_file), shell=True)                
            except subprocess.CalledProcessError:
                print('WARNING: Could not download {}'.format(str(d)))
                not_downloaded.append(d)
        else:
            already_uploaded.append(d)
            
    print('TOTAL DATASETS: {}'.format(str(len(datasets))))
    print('DATASETS DOWNLOADED SUCCESSFULLY: {}'.format(str(len(downloaded))))
    print('ERROR - NOT DOWNLOADED: {}'.format(str(len(not_downloaded))))
    print('ALREADY UPLOADED AND EXISTS: {}'.format(str(len(already_uploaded))))
    return


if __name__ == '__main__':                                                                                                          
    run_sars_cov2_ncbi( sys.argv[1:] )
