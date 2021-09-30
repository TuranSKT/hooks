#!bin/bash
full_path=$(realpath $0)
dir_path=$(dirname $full_path)
/home/cellari/env/cel-apus/bin/python3 $dir_path/event2io.py
