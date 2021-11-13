#!/usr/bin/ksh
# get the latest build
# will overwrite existing

. $NFT_HOME/env.ksh

if [ $# -ne 1 ] ; then
    echo "usage: $0 build"
    exit
fi


buildhome=${NFT_BUILDS}tc_client/
build=$1
buildir=${MW_BUILDS}/${build}
echo $buildir
if [ ! -d $buildir ] ; then
    echo "build doesn't exist!"
    exit 1
fi

type=32
if [[ "$type" != "32" && $type != "64" ]] ; then
    echo "enter 32 or 64 only"
    exit 1
fi

target=$buildhome/$type/

client_zip=$buildir/${build}_client_win_${type}.zip
cd $target
mkdir $build
unzip $client_zip $build/* 


chmod 777 -R $build
