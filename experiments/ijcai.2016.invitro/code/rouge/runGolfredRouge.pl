#!/usr/bin/perl -w
use Cwd;
$curdir=getcwd;
$ROUGE="../ROUGE-1.5.5.pl";
chdir("golfred-test");
$cmd="$ROUGE -e ../data -c 95 -2 -1 -U -a 2golfred.peer.vs.5models.xml";
print $cmd,"\n";
system($cmd);
chdir($curdir);
