from sys import platform as plat
import os
import argparse

def libSetup(pathExtra, name=None):
    envPath = os.path.relpath('./environment/')
    filePath = envPath + '/' + pathExtra
    libPath = os.path.relpath('./lib/')
    for file in os.listdir(filePath):
        os.rename(filePath+'/'+file, libPath+'/'+file)
    if name == None:
        command = 'conda env create -f ' + envPath + '/environment.yml'
    else:
        command = 'conda env create -f ' + envPath + '/environment.yml --name ' + name
    os.system(command)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, help='Name for the anaconda environment that will automatically be made after running this script')
    args = parser.parse_args()
    readPath = os.path.relpath('./ReadGUI')
    if os.path.isdir(readPath) == False:
        os.mkdir(readPath)
    if plat.startswith('linux'):
        libSetup('Linux', args.name)
    elif plat.startswith('win32'):
        libSetup('Windows', args.name)
    else:
        print('Invalid OS, please follow manual installation instructions')