#!/usr/bin/env python3
# to_psp8.py converts pseudopotentials from upf to psp8 format. 
# Python 3.6 and numpy are required to use this script.

import re
import numpy as np
from math import pi

def main():
    from sys import argv, exit
    from os import path
    import getopt

    help = '''
How to use in terminal:
    -----------------------------------------------------------------------
    python to_psp8.py path/to/psp.upf 
    -----------------------------------------------------------------------
    To convert multiple files, run
    -----------------------------------------------------------------------
    python to_psp8.py path/to/psp1.upf path/to/psp2.upf path/to/psp3.upf  
    -----------------------------------------------------------------------
    converted output files are generated in the same directory as the corresponding
    input files and have the same name, but psp8 file extension. 

Requirements:
    python 3.6 or higher
    numpy

Limitation:
    Does not support pseudopotentials with nonlinear core correction. (will be added)
    '''

    try:
        opts, args = getopt.gnu_getopt(argv[1:], "hs", ["help", "stdout"])
    except getopt.GetoptError as err:
        print('\nto_pspd8.py:', err)
        print(help)
        exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help)
            exit()
        elif opt in ("-s", "--stdout"):
            print('\nto_pspd8.py does\'t support stdout, ')
            print(help)
            exit()

    if len(args) < 1:
        print("\nto_pspd8.py: please specify upf file(s) to convert")
        print(help)
        exit()
    
    for arg in args:
        if not path.isfile(arg):
                print("to_pspd8.py: can\'t find %s" % arg)
        else:
            convert(arg)


def get_upf_tag_text(tag,read_upf_file):
    '''extracts content of the upf file within a tagged block: <{tag},attributes> content </{tag}>'''
    return re.search(r'(<{tag}.*>\n)(.*?)(</{tag}>)'.format(tag=tag), read_upf_file, re.DOTALL).group(2)

def get_upf_tag_data(tag,read_upf_file):
    '''if applicable to the tagged block, extracts block's data and returns it in an array'''
    return [float(s) for s in get_upf_tag_text(tag,read_upf_file).split()]

def read_psp_input_text(text):
    '''converts the ONCVPSP input text to a dictionary'''
    def try_float(s):
        try:
            return float(s)
        except:
            return s

    input_data = {}
    sections = text.split('#')
    for section in sections:
        section = section.strip().split('\n')
        if section[0] == 'TEST CONFIGURATIONS':
            break
        elif len(section) >= 2:
            keys = re.findall(r'[a-zA-Z0-9()]*[a-zA-Z0-9()]',section[0]) 
            if keys[0] == 'n':
                keys = ['nn','ll','ff'] 

            data = [d.split() for d in section[1:] ]        
            if len(data) > 1:
                # transpose
                m = len(data[0])
                datat = []
                for j in range(m):
                    c = []
                    for r in data:
                        c.append(try_float(r[j]))
                    datat.append(c)    
                data = datat
            else:
                data = [try_float(s) for s in data[0]]
            # print(data)

            for i,d in enumerate(data):
                input_data[keys[i]] = d

    return input_data

def convert(upf_file_path):
    '''
    Converts upf to psp8. 
    The converted file has the same name and is in the same directory.
    Does not support pseudopotentials with nonlinear core correction, will be added. 
    '''

    with open(upf_file_path) as myfile:
        upf_file = myfile.read()

    INPUT_TEXT = get_upf_tag_text('PP_INPUTFILE', upf_file)
    
    input_dic = read_psp_input_text(INPUT_TEXT)

    '''psp8 HEADER'''
    # line 1
    atsym = input_dic['atsym']
    ONCVPSP_version = re.search(r'version (\d.\d.\d)' ,upf_file).group(1)
    RC = input_dic['rc']
    if not isinstance(RC,float):
        rc_string = ' '.join([f"{rc:.5f}" for rc in RC])
    else:
        rc_string = f"{RC:.5f}"

    # line 2
    zatom = float(input_dic['z'])
    zion = float(re.search(r'z_valence="(.*)"',upf_file).group(1).strip())
    date = re.search(r'date="(\d{6})"',upf_file).group(1) 

    # line 3
    iexc_map = {3:2, 4:11}
    pspcod = 8  # psp8
    pspxc = iexc_map[int(input_dic['iexc'])]  
    lmax = int(input_dic['lmax'])
    lloc = input_dic['lloc']
    mmax = int(input_dic['rlmax'] / input_dic['drl'])

    # line 4
    # is the radius beyond which the model core charge (if used) is zero or negligible.
    # The maximum radial mesh point must equal or exceed this value.
    rchrg = input_dic['rlmax'] - input_dic['drl']
    # fchrg=1.0 signals that a model core charge is present. 
    # Any value >0.0 will do, and the value is not used otherwise.
    if input_dic['icmod'] != 0:
        fchrg = 1
    else:
        fchrg = 0

    # line 5
    nproj = input_dic['nproj']
    if isinstance(nproj,float):
        nproj= [nproj]
    nprj = [0,0,0,0,0]
    for i,n in enumerate(nproj):
        nprj[i] = int(n)
    nprj
    nproj_string = '   '.join([str(n) for n in nprj])

    '''reading relavent data for psp8'''
    RR = get_upf_tag_data('PP_R', upf_file)
    LOCAL = get_upf_tag_data('PP_LOCAL', upf_file)

    number_of_proj = int(re.search(r'number_of_proj="(.*)"', upf_file).group(1))

    BKB_projectors = []
    for i in range(number_of_proj):
        BKB_projectors.append(get_upf_tag_data(f'PP_BETA.{i+1}', upf_file))

    DIJ = get_upf_tag_data('PP_DIJ', upf_file)
    dij = []
    for x in DIJ:
        if x != 0:
            dij.append(x/2) 

    if fchrg > 0:
        NLCC = get_upf_tag_data('PP_NLCC', upf_file)
        NLCC = [x*4*pi for x in NLCC]

    RHOATOM = get_upf_tag_data('PP_RHOATOM', upf_file)

    '''writing the psp8 file'''
    text = f'''{atsym}   ONCVPSP-{ONCVPSP_version}   r_core=    {rc_string}
    {zatom:.4f}   {zion:.4f}   {date}   zatom,zion,pspd
    {pspcod:.0f}   {pspxc:.0f}   {lmax:.0f}   {lloc:.0f}   {mmax:.0f}   0   pspcod,pspxc,lmax,lloc,mmax,r2well
    {rchrg:.8f}   {fchrg:.8f}   0.00000000   rchrg fchrg qchrg
    {nproj_string}   nproj
    1   1   extension_switch
    '''
    c = np.cumsum(nproj).astype(int)
    for l in range(lmax+1):
        n = int(nproj[l])
        if l > 0:
            m = int(nproj[l-1])
            d = dij[c[l-1]:c[l]]
            P = BKB_projectors[c[l-1]:c[l]]
        else:
            d = dij[:c[l]]
            P = BKB_projectors[:c[l]]

        text += f'{l:>4}{"":23}'
        for i in range(n):
            text += f"{f'{d[i]:.13E}':>21}"
        text += '\n'

        for i in range(mmax):
            text += f"{i+1:>6}{f'{RR[i]:.13E}':>21}"    
            for k in range(n):
                text += f"{f'{P[k][i]:.13E}':>21}"
            text += '\n'

    text += f'{4:>4}\n'
    for i in range(mmax):
        text += f"{i+1:>6}{f'{RR[i]:.13E}':>21}{f'{LOCAL[i]/2:.13E}':>21}\n"

    # nonlinear core correction
    if fchrg > 0:
        for i in range(mmax):
            text += f"{i+1:>6}{f'{RR[i]:.13E}':>21}{f'{NLCC[i]:.13E}':>21}\n"

    for i in range(mmax):
        
        if RR[i] == 0:
            rhol = RHOATOM[i]/1e-9
        else:
            rhol = RHOATOM[i]/RR[i]**2

        rhotael = 0
        rhocl = 0

        text += f"{i+1:>6}{f'{RR[i]:.13E}':>21}{f'{rhol:.13E}':>21}{f'{rhotael:.13E}':>21}{f'{rhocl:.13E}':>21}\n"

    text += '<INPUT>\n'+INPUT_TEXT+'</INPUT>\n'

    with open(upf_file_path.rsplit('.',1)[0]+'.psp8','w') as f:
        f.write(text)
        

if __name__ == "__main__":
    main()