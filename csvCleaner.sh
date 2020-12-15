#! /usr/bin/env bash

sed -i 's/CHOPHOUSE\ -\ NOLA/CHOPHOUSE-NOLA/g' Product\ Mix.csv
sed -i 's/CHOPHOUSE\ -\ NOLA/CHOPHOUSE-NOLA/g' Menu\ Price\ Analysis.csv
sed -i 's/\ -\ /-/g2' Product\ Mix.csv
sed -i 's/\ -\ /-/g2' Menu\ Price\ Analysis.csv
