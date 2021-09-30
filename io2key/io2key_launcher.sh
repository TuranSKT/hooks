#!bin/bash
export DISPLAY=:0.0
full_path=$(realpath $0)
dir_path=$(dirname $full_path)
/home/cellari/env/cel-apus/bin/python3 $dir_path/io2key.py
