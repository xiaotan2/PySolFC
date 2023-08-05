#! /bin/bash
#
# repack-min-cardsets.bash
# Copyright (C) 2018 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.
#

set -e

src_base="PySolFC-Cardsets"
dest_base="$src_base--Minimal"
ver="2.1.0"
src_vbase="$src_base-2.1"
dest_vbase="$dest_base-2.1.0"
src_arc="$src_vbase.tar.bz2"

if ! test -f "$src_arc"
then
    wget -c "https://pysolfc-cardsets-2-mirror.s3.eu-west-1.amazonaws.com/$src_base/$src_vbase/$src_arc" -O "$src_arc"
fi

tar -xf "$src_arc" 
rm -rf "$dest_vbase"
mkdir -p "$dest_vbase"
cat scripts/cardsets_to_bundle | (while read b
do
    cp -a "$src_vbase/$b" "$dest_vbase/$b"
done)

tar -caf "$dest_vbase.tar.xz" "$dest_vbase"
