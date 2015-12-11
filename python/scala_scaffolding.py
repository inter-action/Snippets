import subprocess
import os

def mkdirs():
    subprocess.call("mkdir -p src/main/scala", shell=True)
    subprocess.call("mkdir -p src/main/java", shell=True)
    subprocess.call("mkdir -p src/test/scala", shell=True)
    subprocess.call("mkdir -p src/test/java", shell=True)
    subprocess.call("mkdir project", shell=True)



def write_files():
    write_file('build.sbt', sbt_file_content, 'x')

def write_file(file_path, file_content, *open_args):
    with open(file_path, *open_args) as file:
        file.write(file_content)


############# start: init #################

sbt_file_content = """
name := "problem99"

version := "0.1-SNAPSHOT"

scalaVersion := "2.10.1"

libraryDependencies ++= Seq(
)
    
"""
############# end: init #################

if __name__ == '__main__':
    print('current directory is: ', os.getcwd())
    mkdirs()
    write_files()