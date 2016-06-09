#!/bin/sh

find . -name "*.pyc" -depth -exec rm {} \;
find . -name ".DS_Store" -depth -exec rm {} \;
