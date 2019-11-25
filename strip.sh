#!/bin/bash

for sf in lib*.so*
do
   libfile=$(find /usr/lib -name $sf -print)
   if [[ -z $libfile ]]; then
        echo "$sf NOT found"
        continue
   fi
   if [[ $sf == "libpython3.7m.so.1.0" ]]; then
        continue
   fi
   if [[ $sf == "libFLAC.so.8" ]]; then
        continue
   fi
   if [[ $sf == "libfluidsynth.so.1" ]]; then
        continue
   fi
   if [[ $sf == "libgstreamer-1.0.so.0" ]]; then
        continue
   fi
   if [[ $sf == "libmodplug.so.1" ]]; then
        continue
   fi
   if [[ $sf == "libmpdec.so.2" ]]; then
        continue
   fi
   if [[ $sf == "libopusfile.so.0" ]]; then
        continue
   fi
   if [[ $sf == "libSDL2_image-2.0.so.0" ]]; then
        continue
   fi
   if [[ $sf == "libSDL2_mixer-2.0.so.0" ]]; then
        continue
   fi
   if [[ $sf == "libSDL2_ttf-2.0.so.0" ]]; then
        continue
   fi

   echo "$libfile  FOUND for  $sf"
   ls -l $libfile
   ls -l $sf
   diff $libfile $sf
   rm $sf
   ln -s $libfile $sf
   echo "Linked $sf\n"
done

