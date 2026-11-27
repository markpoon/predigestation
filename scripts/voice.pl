#!/usr/bin/perl
# voice.pl est "<text>"            -> estimated seconds, from the calibrated model
# voice.pl cal "<text>" <seconds>  -> update the model from a measured duration (moving average)
use strict; my ($mode,$t,$act)=@ARGV; use File::Basename qw(dirname); my $V=dirname(__FILE__)."/voice.json";
my $k=0.047; if(open my $fh,'<',$V){local $/;my $j=<$fh>; $k=$1 if $j=~/"k":([\d.]+)/;}
my @w=split /\s+/,$t; my ($s,$p)=(0,0);
for my $i(0..$#w){(my $x=$w[$i])=~s/[^A-Za-z0-9]//g;$s+=length($x)+2;
  if($i<$#w){$p+=0.45 if $w[$i]=~/[.!?]$/;$p+=0.25 if $w[$i]=~/[,;:]$/;}}
my $fixed=0.22+$p; my $est=$fixed+$s*$k;
if($mode eq 'est'){printf "%.2f",$est;exit}
my $ko=($act-$fixed)/$s; $ko=$k if $ko<=0; my $kn=0.7*$k+0.3*$ko;
open my $o,'>',$V; printf $o '{"k":%.5f,"updated":%d}',$kn,time; close $o;
printf '{"mode":"voice-cal","est_s":%.2f,"actual_s":%.2f,"err_ms":%d,"k_old":%.5f,"k_new":%.5f}',$est,$act,($est-$act)*1000,$k,$kn;
