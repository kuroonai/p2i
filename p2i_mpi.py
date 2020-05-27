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
import multiprocessing
from contextlib import contextmanager

n_cpu = multiprocessing.cpu_count()

loc = sys.argv[1]

if os.name == 'posix':
	location = loc.split('/')[:-1]
	s = '/'
elif os.name == 'nt':
	location = loc.split('\\')[:-1]
	s = '\\'

if len(sys.argv) == 4 and '.pdf' in loc.split(s)[-1]:
    
    newlocation = s.join(location)
    path = sys.argv[1]
    start = int(sys.argv[2])
    stop = int(sys.argv[3])
    pagename = loc.split(s)[-1].split('.')[0]
    pagenumbers = list(range(start,stop+1))
    images = convert_from_path(path,dpi=300,output_folder=None,first_page=start, last_page=stop)


def equalto2(file):
    
    if file.endswith('.pdf'):
        filename = file.split('.')
        if os.name == 'posix':
        	images = convert_from_path(loc+'/'+file,dpi=300)
        elif os.name =='nt':
        	images = convert_from_path(loc+'\\'+file,dpi=300)
        print(('\n\nconverting "%s" with %d page(s)\n'%(str(file),len(images))))
    
        for page in tqdm(list(range(len(images)))):
            if os.name == 'posix':
                if page > 0: images[page].save(loc+'/{}/'.format(filename[0])+'.'.join(filename[:-1])+'_%d'%(page+1)+'.jpg')
                else: images[page].save(loc+'/{}/'.format(filename[0])+'.'.join(filename[:-1])+'.jpg')
            elif os.name == 'nt':
                if page > 0: images[page].save(loc+'\\{}\\'.format(filename[0])+'.'.join(filename[:-1])+'_%d'%(page+1)+'.jpg')
                else: images[page].save(loc+'\\{}\\'.format(filename[0])+'.'.join(filename[:-1])+'.jpg')
 
def equalto4(page):
    if os.name == 'posix':
        images[page].save(newlocation+'/{}/'.format(pagename)+'%s_%d'%(pagename,pagenumbers[page])+'.jpg')
    elif os.name == 'nt':
        images[page].save(newlocation+'\\{}\\'.format(pagename)+'%s_%d'%(pagename,pagenumbers[page])+'.jpg')
			
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()  



if __name__ == "__main__" :
    
    with poolcontext(processes=n_cpu) as pool:
        
        if len(sys.argv) < 2: raise SyntaxError("Syntax: p2i.py <location of pdf files>")


        elif len(sys.argv) == 2 and loc.split(s)[-1].split('.')[-1] == 'pdf':
        
            if loc.split(s)[-1].split('.')[-1] != 'pdf': raise SyntaxError("Syntax: p2i.py <./pdf file> need, directed file is not a pdf file")
            
            newlocation = s.join(location)
            
            path = sys.argv[1]
            pageno = 1
            pagename = loc.split(s)[-1].split('.')[0]
            
            images = convert_from_path(path,dpi=300,output_folder=None,first_page=pageno,last_page=pageno)
            print(('\n\nconverting page number %d of "%s"\n'%(pageno,path.split(s)[-1])))
            
            #for page in tqdm(range(len(images))):
            if os.name == 'posix':
            	images[0].save(newlocation+'/'+'%s'%(pagename)+'.jpg')
            elif os.name =='nt':
            	images[0].save(newlocation+'\\'+'%s'%(pagename)+'.jpg')
            
            
        
        
        elif len(sys.argv) == 2 and '.pdf' not in loc.split(s)[-1]:
               
            
            #loc = '/media/sf_dive/Research_work/afinalpaperrun/analysis/OPT/bmark/splits/results'
            os.chdir(loc)
            source = list(filter(lambda k: k.endswith('.pdf'),  os.listdir(loc)))
            foldname = [f.split('.')[0] for f in source]
            
            for foldn in foldname:
                if os.path.isdir(foldn): pass
                else : os.mkdir(foldn)
                
            print('\n')
            
            pool.map(equalto2, (file  for file in tqdm(source) ))                    	
        
        
        elif len(sys.argv) == 3 and '.pdf' in loc.split(s)[-1]:
            

            newlocation = s.join(location)
            
            path = sys.argv[1]
            pageno = int(sys.argv[2])
            pagename = loc.split(s)[-1].split('.')[0]
            
            images = convert_from_path(path,dpi=300,output_folder=None,first_page=pageno,last_page=pageno)
            print(('\n\nconverting page number %d of "%s"\n'%(pageno,path.split(s)[-1])))
            
            #for page in tqdm(range(len(images))):
            if os.name == 'posix':
            	images[0].save(newlocation+'/'+'%s_%d'%(pagename,pageno)+'.jpg')
            elif os.name =='nt':
            	images[0].save(newlocation+'\\'+'%s_%d'%(pagename,pageno)+'.jpg')
        
                        
        
        elif len(sys.argv) == 4 and '.pdf' in loc.split(s)[-1]:
            
            newlocation = s.join(location)
            
            # path = sys.argv[1]
            # start = int(sys.argv[2])
            # stop = int(sys.argv[3])
            # pagename = loc.split(s)[-1].split('.')[0]
            # images = convert_from_path(path,dpi=300,output_folder=None,first_page=start, last_page=stop)
            print(('\n\nconverting page numbers %d to %d of "%s"\n'%(start,stop,path.split(s)[-1])))
            
            images = convert_from_path(path,dpi=300,output_folder=None,first_page=start, last_page=stop)
            
            pagenumbers = list(range(start,stop+1))
            
            pages = tqdm(list(range(len(images))))
            
            if os.path.isdir(pagename): pass
            else : os.mkdir(pagename)

            pool.map(equalto4,(page for page in tqdm(pages)))
            # for page in tqdm(pages):
            #     equalto4(page)
            
            		
        
        elif len(sys.argv) != 4 or len(sys.argv) > 4:
            raise SyntaxError("Syntax: p2i.py <location_with_filename> <page number range eg: <start> <stop> >")
                
        
    
            



