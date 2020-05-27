#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 22:33:23 2019

@author:Naveen Kumar Vasudevan, 
        Doctoral Student, 
        The Xi Research Group, 
        McMaster University, 
        Hamilton, 
        Canada.
        
        naveenovan@gmail.com
        https://naveenovan.wixsite.com/kuroonai
"""

'''
################################### pdf2image convertor ######################################

https://pypi.org/project/pdf2image/

       Using conda
conda install -c conda-forge poppler
pip install pdf2image
pip install pillow

for large files to track progress use tqdm:
    
conda install -c conda-forge tqdm

make sure pip is from conda using "which pip" in commandline

usage :
    
    1) python p2i.py </location/to/folder/with/pdf/files/for/conversion>

        output : converts all .pdf file from location into .jpg file
    
    2) python p2i.py </location/to/folder/with/pdf/file/with/itsname.pdf> <page number>
        
        output : converts specified page of the pdf file in path
        
    3) python p2i.py <location_with_filename> <page number range eg: <start> <stop> >
    
        output : converts the range of pages from specified pdf file
'''

'''

add alias in linux or unix for easy access

use following commands:
    cd 
    open .bashrc file (vi .bashrc) and type the below line
    alias p2i = "python /location to p2i.py"
    
    now code can be used from command line as follows 
    
    p2i /location/of/pdf/files(/test.pdf) pagenumber or <start> <stop>
    
'''

'''

examples:

python p2i.py /home/user/Desktop/
python p2i.py /home/user/Desktop/test.pdf 2
python p2i.py /home/user/Desktop/test.pdf 2 19
    
'''

from pdf2image import convert_from_path
import os
import sys
from tqdm import tqdm

loc = sys.argv[1]

if len(sys.argv) < 2: raise SyntaxError("Syntax: p2i.py <location of pdf files>")


elif len(sys.argv) == 2 and len(loc.split('/')[-1].split('.')) == 2 :

    if loc.split('/')[-1].split('.')[1] != 'pdf': raise SyntaxError("Syntax: p2i.py <./pdf file> need, directed file is not a pdf file")
    
    if os.name == 'posix':
    	location = loc.split('/')[:-1]
    	s = '/'
    elif os.name == 'nt':
    	location = loc.split('\\')[:-1]
    	s = '\\'
    newlocation = s.join(location)
    
    path = sys.argv[1]
    pageno = 1
    pagename = loc.split('/')[-1].split('.')[0]
    
    images = convert_from_path(path,dpi=300,output_folder=None,first_page=pageno,last_page=pageno)
    print(('\n\nconverting page number %d of "%s"\n'%(pageno,path.split('/')[-1])))
    
    #for page in tqdm(range(len(images))):
    if os.name == 'posix':
    	images[0].save(newlocation+'/'+'%s'%(pagename)+'.jpg')
    elif os.name =='nt':
    	images[0].save(newlocation+'\\'+'%s'%(pagename)+'.jpg')
    
    


elif len(sys.argv) == 2:
       
    
    #loc = '/media/sf_dive/Research_work/afinalpaperrun/analysis/OPT/bmark/splits/results'
    os.chdir(loc)
    source = os.listdir(loc)

    print('\n')

    for file in source:
        if file.endswith('.pdf'):
            filename = file.split('.')
            if os.name == 'posix':
            	images = convert_from_path(loc+'/'+file,dpi=300)
            elif os.name =='nt':
            	images = convert_from_path(loc+'\\'+file,dpi=300)
            print(('\n\nconverting "%s" with %d page(s)\n'%(str(file),len(images))))
        
            for page in tqdm(list(range(len(images)))):
                if os.name == 'posix':
                    if page > 0: images[page].save(loc+'/'+'.'.join(filename[:-1])+'_%d'%(page+1)+'.jpg')
                    else: images[page].save(loc+'/'+'.'.join(filename[:-1])+'.jpg')
                elif os.name == 'nt':
                    if page > 0: images[page].save(loc+'\\'+'.'.join(filename[:-1])+'_%d'%(page+1)+'.jpg')
                    else: images[page].save(loc+'\\'+'.'.join(filename[:-1])+'.jpg')
              	


elif len(sys.argv) == 3:
    
    if os.name == 'posix':
    	location = loc.split('/')[:-1]
    	s = '/'
    elif os.name == 'nt':
    	location = loc.split('\\')[:-1]
    	s = '\\'
    newlocation = s.join(location)
    
    path = sys.argv[1]
    pageno = int(sys.argv[2])
    
    images = convert_from_path(path,dpi=300,output_folder=None,first_page=pageno,last_page=pageno)
    print(('\n\nconverting page number %d of "%s"\n'%(pageno,path.split('/')[-1])))
    
    #for page in tqdm(range(len(images))):
    if os.name == 'posix':
    	images[0].save(newlocation+'/'+'pagenumer_%d'%(pageno)+'.jpg')
    elif os.name =='nt':
    	images[0].save(newlocation+'\\'+'pagenumer_%d'%(pageno)+'.jpg')

                

elif len(sys.argv) == 4:
    
    if os.name == 'posix':
    	location = loc.split('/')[:-1]
    	s = '/'
    elif os.name == 'nt':
    	location = loc.split('\\')[:-1]
    	s = '\\'
    newlocation = s.join(location)
    
    path = sys.argv[1]
    start = int(sys.argv[2])
    stop = int(sys.argv[3])
    
    print(('\n\nconverting page numbers %d to %d of "%s"\n'%(start,stop,path.split('/')[-1])))
    
    images = convert_from_path(path,dpi=300,output_folder=None,first_page=start, last_page=stop)
    
    pagenumbers = list(range(start,stop+1))
    
    for pages in tqdm(list(range(len(images)))):
    		if os.name == 'posix':
    			images[pages].save(newlocation+'/'+'pagenumer_%d'%(pagenumbers[pages])+'.jpg')
    		elif os.name == 'nt':
    			images[pages].save(newlocation+'\\'+'pagenumer_%d'%(pagenumbers[pages])+'.jpg')
    			

elif len(sys.argv) != 4 or len(sys.argv) > 4:
    raise SyntaxError("Syntax: p2i.py <location_with_filename> <page number range eg: <start> <stop> >")
        
        
    
            

