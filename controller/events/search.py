#!/usr/bin/evn python3

from string import Template

def render():
    d = {}
    filein = open( '../templates/search.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)
    return content


if __name__ == "__main__":
    print( render() )
