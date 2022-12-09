//Maya ASCII 2012 scene
//Name: fish.ma
//Last modified: Fri, Nov 25, 2016 09:19:13 PM
//Codeset: 1252
requires maya "2008";
fileInfo "application" "maya";
fileInfo "product" "Maya 2012";
fileInfo "version" "2012 x64";
fileInfo "cutIdentifier" "201201172029-821146";
fileInfo "osv" "Microsoft Business Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -32.169778766441027 10.720441346401984 16.241508297398795 ;
	setAttr ".r" -type "double3" -10.53835272838791 -64.199999999988236 1.8269344068295162e-015 ;
	setAttr ".rp" -type "double3" -7.1054273576010019e-015 -6.6613381477509392e-016 
		7.1054273576010019e-015 ;
	setAttr ".rpt" -type "double3" -5.9557606421402406e-015 3.2346389146233795e-015 
		1.3524766818645888e-014 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999979;
	setAttr ".ncp" 1;
	setAttr ".coi" 41.677492821322957;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0 5.0929105390923128 1.6372266348746543 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 101.51445051952885 1.6372266348746756 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
	setAttr ".rp" -type "double3" 0 0 -1.4210854715202004e-014 ;
	setAttr ".rpt" -type "double3" 0 -1.4210854715202007e-014 1.4210854715202038e-014 ;
createNode camera -s -n "topShape" -p "top";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".ncp" 1;
	setAttr ".coi" 95.959202704722571;
	setAttr ".ow" 71.155769032592858;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".tp" -type "double3" 3.9769202443274065 5.2241065502166748 9.2678484836247179 ;
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 5.0929105390923128 100.22790961747118 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".ncp" 1;
	setAttr ".coi" 89.28688305188264;
	setAttr ".ow" 29.79543022525511;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".tp" -type "double3" -3.0587439213178407e-006 3.5160879320255307 10.928055281217482 ;
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 106.65456920115902 5.0929105390923128 1.6372266348746782 ;
	setAttr ".r" -type "double3" -4.7928194511400284e-016 89.999999999999986 0 ;
	setAttr ".rp" -type "double3" 2.2204460492503131e-016 0 -1.4210854715202004e-014 ;
	setAttr ".rpt" -type "double3" -1.4432899320127041e-014 0 1.398881011027701e-014 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".ncp" 1;
	setAttr ".coi" 106.17732510518786;
	setAttr ".ow" 37.132258111668605;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".tp" -type "double3" 0 2.3091136794508915 1.6372266348746549 ;
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "FitSkeleton";
	addAttr -ci true -sn "visCylinders" -ln "visCylinders" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "visBoxes" -ln "visBoxes" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "visBones" -ln "visBones" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "lockCenterJoints" -ln "lockCenterJoints" -dv 1 -min 0 -max 
		1 -at "bool";
	addAttr -ci true -sn "visGap" -ln "visGap" -dv 0.75 -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "visGeoType" -ln "visGeoType" -min 0 -max 3 -en "cylinders:boxes:spheres:bones" 
		-at "enum";
	addAttr -ci true -sn "visSpheres" -ln "visSpheres" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "visGeo" -ln "visGeo" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "numMainExtras" -ln "numMainExtras" -at "long";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr ".visCylinders" yes;
	setAttr ".visGap" 1;
createNode nurbsCurve -n "FitSkeletonShape" -p "FitSkeleton";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 29;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		7.4281782225557524 4.5484473418744768e-016 -7.4281782225557444
		-1.1984983579866045e-015 6.4324759186187512e-016 -10.50503038606281
		-7.4281782225557462 4.5484473418744807e-016 -7.4281782225557462
		-10.50503038606281 2.3964034686954702e-031 -4.003240790329802e-015
		-7.4281782225557471 -4.5484473418744768e-016 7.4281782225557444
		-3.1653706727369662e-015 -6.4324759186187522e-016 10.505030386062812
		7.4281782225557444 -4.5484473418744807e-016 7.4281782225557462
		10.50503038606281 -2.9224624886215383e-031 4.6831265133208731e-015
		7.4281782225557524 4.5484473418744768e-016 -7.4281782225557444
		-1.1984983579866045e-015 6.4324759186187512e-016 -10.50503038606281
		-7.4281782225557462 4.5484473418744807e-016 -7.4281782225557462
		;
createNode joint -n "Root" -p "FitSkeleton";
	addAttr -ci true -sn "run" -ln "run" -dt "string";
	addAttr -ci true -k true -sn "centerBtwFeet" -ln "centerBtwFeet" -dv 1 -min 0 -max 
		1 -at "bool";
	addAttr -ci true -k true -sn "numMainExtras" -ln "numMainExtras" -min 0 -at "long";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6513860869518515 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0 4.365042701528143 5.9286271944734859 ;
	setAttr -l on ".tx";
	setAttr ".r" -type "double3" -7.3947896344026762e-014 9.0571264171363477e-015 9.541664044390544e-015 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 90 85.843421145494901 90 ;
	setAttr ".dl" yes;
	setAttr ".typ" 1;
	setAttr ".radi" 0.56260248658386702;
	setAttr -k on ".run" -type "string" "setAttr \"AimEye_M.follow\" 10;";
	setAttr ".fatYabs" 2.651386022567749;
	setAttr ".fatZabs" 2.651386022567749;
createNode joint -n "BackA" -p "Root";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6513860869518515 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6513860869518524 8.8817841970012523e-016 -2.4539423167062912e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -9.2213655748728796e-016 -2.3854160110976384e-015 ;
	setAttr ".radi" 0.5715910433455943;
	setAttr ".fatYabs" 2.651386022567749;
	setAttr ".fatZabs" 2.651386022567749;
createNode joint -n "BackB" -p "BackA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6513860869518542 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6513860869518577 -5.3290705182007514e-015 -2.6631586312918689e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -9.2213655748728796e-016 -2.3854160110976384e-015 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Mid";
	setAttr ".radi" 0.62803708455100304;
	setAttr ".fatYabs" 2.651386022567749;
	setAttr ".fatZabs" 2.651386022567749;
createNode joint -n "BackC" -p "BackB";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6513860869518515 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6513860869518577 1.7763568394002505e-014 -3.8388294140003632e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -9.2213655748728796e-016 -2.3854160110976384e-015 ;
	setAttr ".radi" 0.59943130353491136;
	setAttr ".fatYabs" 2.651386022567749;
	setAttr ".fatZabs" 2.651386022567749;
createNode joint -n "BackD" -p "BackC";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6513860869518515 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6513860869518515 4.4408920985006262e-015 -3.1578726885954246e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -9.2213655748728796e-016 -2.3854160110976384e-015 ;
	setAttr ".radi" 0.54429159943558547;
	setAttr ".fatYabs" 2.651386022567749;
	setAttr ".fatZabs" 2.651386022567749;
createNode joint -n "BackE" -p "BackD";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.651386086951856 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6513860869518604 -3.0198066269804258e-014 -2.0525726385648183e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -9.2213655748728796e-016 -2.3854160110976384e-015 ;
	setAttr ".radi" 0.59408661293452403;
	setAttr -k on ".fat" 2;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 2;
createNode joint -n "BackF" -p "BackE";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.031906238462720893 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "freeOrient" -ln "freeOrient" -dv 1 -min 0 -max 1 -at "bool";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6513860869518595 3.6415315207705135e-014 -3.0209229901353765e-016 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" 3.5236388832575822e-015 3.7010879760956662e-015 2.2263882770244617e-013 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Chest";
	setAttr ".radi" 0.59408661293452403;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "TailFinUpper" -p "BackF";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 4.1781431410683556 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.031906238462713787 0.64912926426650142 -4.1981886481139992e-017 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" -1.0760078161517421e-014 1.2722218725853993e-014 1.2086107789561363e-013 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -2.404733207644407e-015 6.7389248289076145 ;
	setAttr ".radi" 0.66438671419319073;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "TailFinUpperEnd" -p "TailFinUpper";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 4.1781431410683556 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 4.1781431410683485 7.9936057773011271e-015 -9.2773414307874508e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -10.895503683412716 -90 0 ;
	setAttr ".radi" 0.66438671419319073;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "TailFinLower" -p "BackF";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 4.1975899654232087 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" -0.18494733507816719 -0.47457190642986813 -3.3500789855740126e-017 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" -1.4281228088245341e-014 1.2722218725854053e-014 1.717499527990299e-013 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -1.1676060625009717e-015 -9.4224191662842411 ;
	setAttr ".radi" 0.66539258441844185;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "TailFinLowerEnd" -p "TailFinLower";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 4.1975899654232087 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 4.1975899654231981 1.1546319456101628e-014 -9.3205220550966846e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 5.265840311779141 -90 0 ;
	setAttr ".radi" 0.66539258441844185;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinLowerB" -p "BackD";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.9362300464491899 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.4573560719861236 -1.6052739485131604 -0.9181271805473652 ;
	setAttr ".r" -type "double3" -1.5902773407317581e-014 1.6538884343610288e-013 1.5902773407317357e-015 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 5.5945298410345385 31.514328999271207 -81.002180279898084 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatY" 2;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinLowerAEnd1" -p "BodyFinLowerB";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.9362300464491899 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 1.9362300464491855 -8.8817841970012523e-016 -6.2172489379008766e-015 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 34.114472945341468 -89.999999999999986 0 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinUpperB" -p "BackC";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.2666000221057967 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.47746292519960232 2.0774386133928555 -1.1674709107279631e-017 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" 1.6973477980997443e-014 1.9083328088781161e-014 1.5902773407317584e-013 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 83.30235628493368 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatY" 2;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinUpperBEnd" -p "BodyFinUpperB";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.2666000221057967 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.266600022105802 6.2172489379008766e-015 -7.5492945964732802e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -57.578935237493056 -90 0 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinUpperA" -p "BackA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.9761916362248035 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" -0.018202652799295116 2.5506788888302108 -1.1550075610080961e-017 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" 1.2346768563938843e-029 1.2339158524872432e-029 -1.9083328088781101e-014 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 90.035325641613923 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatY" 2;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinUpperAEnd" -p "BodyFinUpperA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.9761916362248035 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.9761916362248044 -1.7763568394002505e-015 -6.9025329206838533e-031 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -39.359450567843197 -90 0 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinLowerA" -p "BackA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6585942973040915 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.75520137523378716 -2.1458672506289451 -1.6259284228912188e-016 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" -1.2289633365759865e-014 1.2722218725854095e-014 8.2694421718051442e-014 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -88.018311921311664 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatY" 2;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinLowerAEnd" -p "BodyFinLowerA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2.6585942973040915 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.6585942973040857 3.5527136788005009e-015 -5.9032652040082871e-016 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 40.661733208571889 -90 0 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "BodyFinSide1" -p "Root";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.91690660584086148 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 1.4929537494793985 -0.67590201966062047 -2.4425574425574434 ;
	setAttr ".r" -type "double3" -7.4315647979071519e-013 -5.7296263821766241e-013 1.0706107355016246e-012 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 11.309932474020224 -4.1565788545052573 ;
	setAttr ".radi" 0.5;
	setAttr -k on ".fat" 1.5;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1.5;
	setAttr ".fatZabs" 0.45000001788139343;
createNode joint -n "BodyFinSide2" -p "BodyFinSide1";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.2243775154334962 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.91690660584085037 1.6875389974302379e-014 8.8817841970012523e-015 ;
	setAttr ".r" -type "double3" 9.8599975694253299e-014 -1.6697912077683369e-013 -1.1014210633091078e-012 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -3.0265687930967092e-014 10.231043444518214 1.4410433878423573e-013 ;
	setAttr ".radi" 0.51160573355690497;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 1.2243775129318237;
	setAttr ".fatZabs" 0.36731326580047607;
createNode joint -n "BodyFinSide3" -p "BodyFinSide2";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.3941702317218398 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 1.224377515433501 -2.4868995751603507e-014 3.5527136788005009e-015 ;
	setAttr ".r" -type "double3" 1.1249029262001992e-014 2.1468744099878742e-013 -3.2851072538330213e-013 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -5.589304841483327e-014 3.9223691433331913 1.3798054745827438e-013 ;
	setAttr ".radi" 0.52038811543388819;
	setAttr -k on ".fat" 0.7;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 0.69999998807907104;
	setAttr ".fatZabs" 0.21000000834465027;
createNode joint -n "BodyFinSide4" -p "BodyFinSide3";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.3941702317218398 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 1.3941702317218412 -7.1054273576010019e-015 -5.3290705182007514e-015 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.526666247102488e-013 244.53665493812838 0 ;
	setAttr ".radi" 0.52038811543388819;
	setAttr -k on ".fat" 0.3;
	setAttr -k on ".fatZ" 0.3;
	setAttr ".fatYabs" 0.30000001192092896;
	setAttr ".fatZabs" 0.090000003576278687;
createNode joint -n "Head" -p "Root";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" -0.34321926966019678 -0.027153919429655282 3.7728157235182412e-017 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" -7.0167092985348752e-015 -7.0167092985348239e-015 9.2301645756003963e-013 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 179.99999999999994 ;
	setAttr ".radi" 0.59012513509477516;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 2;

createNode joint -n "HeadEnd" -p "Head";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 2 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 1.9999999999999707 1.7763568394002505e-014 0 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -9.2213655748728796e-016 -179.99999999999994 ;
	setAttr ".fatYabs" 2;
	setAttr ".fatZabs" 2;

createNode joint -n "Eye" -p "Head";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.79026673428566419 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 2.8771821771837232 0.13580068747279572 -1.0929334729715861 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 3.2854009666651112 26.773965852599218 3.1055275567000429 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Eye";
	setAttr ".radi" 0.5;
	setAttr -k on ".fat" 0.3;
	setAttr ".fatYabs" 0.30000001192092896;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "Eye1" -p "Eye";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.79026673428566419 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.7902667342856784 -1.5099033134902129e-014 1.4654943925052066e-014 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 6.2034479016915736 89.999999999999545 0 ;
	setAttr ".radi" 0.5;
	setAttr -k on ".fat" 0.3;
	setAttr ".fatYabs" 0.30000001192092896;
	setAttr ".fatZabs" 0.30000001192092896;
createNode joint -n "Jaw" -p "Head";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 7.6114426698511677 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 0.95031263244374831 0.94661336014774955 2.7292184655780615e-016 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" -7.7683100771985599e-016 -1.2722218725853987e-014 -5.9635400277440935e-014 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.7757707362726162e-014 -2.1767214296586955e-015 6.9883950172007472 ;
	setAttr -k on ".fat" 1;
	setAttr -k on ".fatZ" 2.5;
	setAttr ".fatYabs" 1;
	setAttr ".fatZabs" 2.5;
createNode joint -n "JawEnd" -p "Jaw";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 7.6114426698511677 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".ove" yes;
	setAttr ".t" -type "double3" 7.6114426698511739 -4.4408920985006262e-015 1.6900797805366276e-015 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.5902773407317584e-014 -2.459105202388907e-015 7.9513867036587919e-015 ;
	setAttr -k on ".fat" 0.1;
	setAttr ".fatYabs" 0.10000000149011612;
	setAttr ".fatZabs" 0.10000000149011612;

createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	setAttr ".cdl" 1;
	setAttr -s 29 ".dli[1:28]"  1 2 3 4 5 6 7 8 
		9 10 11 12 13 14 15 16 18 17 19 20 0 0 0 0 0 
		0 0 0;

connectAttr "Root.s" "BackA.is";
connectAttr "BackA.s" "BackB.is";
connectAttr "BackB.s" "BackC.is";
connectAttr "BackC.s" "BackD.is";
connectAttr "BackD.s" "BackE.is";
connectAttr "BackE.s" "BackF.is";
connectAttr "BackF.s" "TailFinUpper.is";
connectAttr "TailFinUpper.s" "TailFinUpperEnd.is";
connectAttr "BackF.s" "TailFinLower.is";
connectAttr "TailFinLower.s" "TailFinLowerEnd.is";
connectAttr "BackD.s" "BodyFinLowerB.is";
connectAttr "BodyFinLowerB.s" "BodyFinLowerAEnd1.is";
connectAttr "BackC.s" "BodyFinUpperB.is";
connectAttr "BodyFinUpperB.s" "BodyFinUpperBEnd.is";
connectAttr "BackA.s" "BodyFinUpperA.is";
connectAttr "BodyFinUpperA.s" "BodyFinUpperAEnd.is";
connectAttr "BackA.s" "BodyFinLowerA.is";
connectAttr "BodyFinLowerA.s" "BodyFinLowerAEnd.is";
connectAttr "Root.s" "BodyFinSide1.is";
connectAttr "BodyFinSide1.s" "BodyFinSide2.is";
connectAttr "BodyFinSide2.s" "BodyFinSide3.is";
connectAttr "BodyFinSide3.s" "BodyFinSide4.is";
connectAttr "Root.s" "Head.is";
connectAttr "Head.s" "Eye.is";
connectAttr "Eye.s" "Eye1.is";
connectAttr "Head.s" "Jaw.is";
connectAttr "Jaw.s" "JawEnd.is";
connectAttr "Head.s" "HeadEnd.is";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of fish.ma